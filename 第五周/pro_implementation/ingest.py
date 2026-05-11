from pathlib import Path
import json
import os
import time
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "True")

from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from chromadb import PersistentClient
from tqdm import tqdm
from litellm import completion
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, wait_exponential, stop_after_attempt

load_dotenv(override=True)

MODEL = "deepseek-ai/DeepSeek-V3.2"

DB_NAME = str(Path(__file__).parent.parent / "preprocessed_db")
CHECKPOINT_PATH = Path(__file__).parent.parent / "preprocessed_chunks.jsonl"
FAILED_PATH = Path(__file__).parent.parent / "failed_chunks.jsonl"
collection_name = "docs"
embedding_model = "BAAI/bge-large-en-v1.5"
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent / "knowledge-base"
AVERAGE_CHUNK_SIZE = 500
wait = wait_exponential(multiplier=1, min=5, max=120)

WORKERS = int(os.getenv("INGEST_WORKERS", "3"))
REQUEST_TIMEOUT_SECONDS = int(os.getenv("INGEST_REQUEST_TIMEOUT_SECONDS", "120"))
RETRY_ATTEMPTS = int(os.getenv("INGEST_RETRY_ATTEMPTS", "3"))

embedding_client = OpenAI(api_key=os.getenv("SILICONCLOUD_API_KEY"), base_url="https://api.siliconflow.cn/v1")


class Result(BaseModel):
    page_content: str
    metadata: dict


class Chunk(BaseModel):
    headline: str = Field(
        description="A brief heading for this chunk, typically a few words, that is most likely to be surfaced in a query",
    )
    summary: str = Field(
        description="A few sentences summarizing the content of this chunk to answer common questions"
    )
    original_text: str = Field(
        description="The original text of this chunk from the provided document, exactly as is, not changed in any way"
    )

    def as_result(self, document):
        metadata = {"source": document["source"], "type": document["type"]}
        return Result(
            page_content=self.headline + "\n\n" + self.summary + "\n\n" + self.original_text,
            metadata=metadata,
        )


class Chunks(BaseModel):
    chunks: list[Chunk]


def fetch_documents():
    """A homemade version of the LangChain DirectoryLoader"""

    documents = []

    for folder in KNOWLEDGE_BASE_PATH.iterdir():
        doc_type = folder.name
        for file in folder.rglob("*.md"):
            if ".ipynb_checkpoints" in file.parts:
                continue
            with open(file, "r", encoding="utf-8") as f:
                documents.append({"type": doc_type, "source": file.as_posix(), "text": f.read()})

    print(f"Loaded {len(documents)} documents", flush=True)
    return documents


def make_prompt(document):
    how_many = (len(document["text"]) // AVERAGE_CHUNK_SIZE) + 1
    return f"""
You take a document and you split the document into overlapping chunks for a KnowledgeBase.

The document is from the shared drive of a company called Insurellm.
The document is of type: {document['type']}
The document has been retrieved from: {document['source']}

A chatbot will use these chunks to answer questions about the company.
You should divide up the document as you see fit, being sure that the entire document is returned across the chunks - don't leave anything out.
This document should probably be split into at least {how_many} chunks, but you can have more or less as appropriate, ensuring that there are individual chunks to answer specific questions.
There should be overlap between the chunks as appropriate; typically about 25% overlap or about 50 words, so you have the same text in multiple chunks for best retrieval results.

For each chunk, you should provide a headline, a summary, and the original text of the chunk.
Together your chunks should represent the entire document with overlap.

Here is the document:

{document['text']}

Respond with the chunks.
"""


def make_messages(document):
    return [
        {"role": "user", "content": make_prompt(document)},
    ]


@retry(wait=wait, stop=stop_after_attempt(RETRY_ATTEMPTS))
def process_document(document):
    messages = make_messages(document)
    start = time.perf_counter()
    response = completion(
        model=MODEL,
        messages=messages,
        response_format=Chunks,
        custom_llm_provider="openai",
        api_base="https://api.siliconflow.cn/v1",
        api_key=os.getenv("SILICONCLOUD_API_KEY"),
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    reply = response.choices[0].message.content
    doc_as_chunks = Chunks.model_validate_json(reply).chunks
    elapsed = time.perf_counter() - start
    return [chunk.as_result(document) for chunk in doc_as_chunks], elapsed


def load_checkpoint():
    if not CHECKPOINT_PATH.exists():
        return {}

    completed = {}
    with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            completed[item["source"]] = [Result.model_validate(chunk) for chunk in item["chunks"]]
    return completed


def save_checkpoint(document, chunks):
    item = {
        "source": document["source"],
        "chunks": [chunk.model_dump() for chunk in chunks],
    }
    with open(CHECKPOINT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


def save_failure(document, error):
    item = {
        "source": document["source"],
        "error": repr(error),
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(FAILED_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")


def create_chunks(documents):
    """
    Create chunks with threads because this step waits on remote API calls.
    """
    completed = load_checkpoint()
    chunks = [chunk for doc_chunks in completed.values() for chunk in doc_chunks]
    documents_to_process = [doc for doc in documents if doc["source"] not in completed]

    print(
        f"Starting chunk creation with {WORKERS} worker(s). "
        f"Loaded {len(completed)} completed document(s) from checkpoint; "
        f"{len(documents_to_process)} remaining.",
        flush=True,
    )

    if not documents_to_process:
        return chunks

    if WORKERS <= 1:
        for i, doc in enumerate(tqdm(documents_to_process)):
            print(f"[INGEST] Processing doc {i+1}/{len(documents_to_process)}: {doc['source']}", flush=True)
            try:
                doc_chunks, elapsed = process_document(doc)
            except Exception as error:
                save_failure(doc, error)
                print(f"[INGEST] Failed doc {i+1}/{len(documents_to_process)}: {doc['source']}", flush=True)
                print(f"[INGEST] Error: {error!r}", flush=True)
                continue
            save_checkpoint(doc, doc_chunks)
            chunks.extend(doc_chunks)
            print(
                f"[INGEST] Completed doc {i+1}/{len(documents_to_process)} in {elapsed:.1f}s, "
                f"total chunks so far: {len(chunks)}",
                flush=True,
            )
        return chunks

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {executor.submit(process_document, doc): (i, doc) for i, doc in enumerate(documents_to_process)}
        for future in tqdm(as_completed(futures), total=len(futures)):
            i, doc = futures[future]
            print(f"[INGEST] Completed doc {i+1}/{len(documents_to_process)}: {doc['source']}", flush=True)
            try:
                doc_chunks, elapsed = future.result()
            except Exception as error:
                save_failure(doc, error)
                print(f"[INGEST] Failed doc {i+1}/{len(documents_to_process)}: {doc['source']}", flush=True)
                print(f"[INGEST] Error: {error!r}", flush=True)
                continue
            save_checkpoint(doc, doc_chunks)
            chunks.extend(doc_chunks)
            print(
                f"[INGEST] Doc {i+1} produced {len(doc_chunks)} chunks in {elapsed:.1f}s, "
                f"total chunks so far: {len(chunks)}",
                flush=True,
            )
    return chunks


def split_text(text, max_tokens=400):
    """Split text into chunks of approximately max_tokens tokens."""
    words = text.split()
    chunks = []
    current = []
    current_len = 0
    for word in words:
        current_len += len(word) + 1
        if current_len > max_tokens * 4:
            chunks.append(' '.join(current))
            current = [word]
            current_len = len(word) + 1
        else:
            current.append(word)
    if current:
        chunks.append(' '.join(current))
    return chunks


def create_embeddings(chunks):
    chroma = PersistentClient(path=DB_NAME)
    if collection_name in [str(c) for c in chroma.list_collections()]:
        chroma.delete_collection(collection_name)

    # Split long texts and deduplicate
    seen = set()
    final_texts = []
    final_metas = []
    for chunk in chunks:
        text = chunk.page_content
        parts = split_text(text, max_tokens=400)
        for part in parts:
            if part not in seen:
                seen.add(part)
                final_texts.append(part)
                final_metas.append(chunk.metadata)

    print(f'Embedding {len(final_texts)} texts (from {len(chunks)} chunks, after dedup)', flush=True)

    # Batch embeddings (max 32 per request, each <512 tokens)
    vectors = []
    batch_size = 32
    for i in range(0, len(final_texts), batch_size):
        batch = final_texts[i:i+batch_size]
        emb = embedding_client.embeddings.create(
            model=embedding_model,
            input=batch,
            timeout=REQUEST_TIMEOUT_SECONDS,
        ).data
        vectors.extend([e.embedding for e in emb])
        print(f'Embedded {min(i+batch_size, len(final_texts))}/{len(final_texts)}', flush=True)

    ids = [str(i) for i in range(len(final_texts))]
    collection = chroma.get_or_create_collection(collection_name)
    collection.add(ids=ids, embeddings=vectors, documents=final_texts, metadatas=final_metas)
    print(f'Vectorstore created with {collection.count()} documents', flush=True)


if __name__ == "__main__":
    print("Script starting...", flush=True)
    print(f"CWD: {os.getcwd()}", flush=True)
    print(f"__file__: {__file__}", flush=True)
    print(f"KNOWLEDGE_BASE_PATH: {KNOWLEDGE_BASE_PATH}", flush=True)
    documents = fetch_documents()
    print(f"Fetched {len(documents)} documents, starting chunk creation...", flush=True)
    chunks = create_chunks(documents)
    print(f"Created {len(chunks)} chunks, starting embedding...", flush=True)
    create_embeddings(chunks)
    print("Ingestion complete", flush=True)
