from datetime import datetime
from tqdm import tqdm
from datasets import load_dataset
from concurrent.futures import ProcessPoolExecutor
from pricer.parser import parse
import os
import json
from pathlib import Path

CHUNK_SIZE = 1000

cpu_count = os.cpu_count()
WORKERS = max(cpu_count - 1, 1)


class ItemLoader:
    LOCAL_DATA_DIR = (
        Path(__file__).resolve().parents[1]
        / "hf_data"
        / "Amazon-Reviews-2023"
        / "raw"
        / "meta_categories"
    )

    def __init__(self, category):
        self.category = category
        self.dataset = None
        self.local_path = None

    def _local_jsonl_path(self):
        """检查本地 JSONL 文件是否存在，返回路径或 None"""
        path = self.LOCAL_DATA_DIR / f"meta_{self.category}.jsonl"
        return path if path.exists() else None

    def _normalize_datapoint(self, datapoint):
        """规范化单条数据，确保格式与 HuggingFace Dataset 一致"""
        if isinstance(datapoint.get("details"), dict):
            datapoint = dict(datapoint)
            datapoint["details"] = json.dumps(datapoint["details"], ensure_ascii=False)
        return datapoint

    def from_datapoint(self, datapoint):
        """
        Try to create an Item from this datapoint
        Return the Item if successful, or None if it shouldn't be included
        """
        datapoint = self._normalize_datapoint(datapoint)
        return parse(datapoint, self.category)

    def from_chunk(self, chunk):
        """
        Create a list of Items from this chunk of elements from the Dataset
        """
        batch = [self.from_datapoint(datapoint) for datapoint in chunk]
        return [item for item in batch if item is not None]

    def chunk_generator(self):
        """
        Iterate over the Dataset, yielding chunks of datapoints at a time.
        Compatible with both local JSONL and HuggingFace Dataset.
        """
        if self.local_path:
            chunk = []
            with open(self.local_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        datapoint = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    chunk.append(datapoint)

                    if len(chunk) == CHUNK_SIZE:
                        yield chunk
                        chunk = []

            if chunk:
                yield chunk
            return

        size = len(self.dataset)
        for i in range(0, size, CHUNK_SIZE):
            yield self.dataset.select(range(i, min(i + CHUNK_SIZE, size)))

    def load_in_parallel(self, workers):
        """
        Use concurrent.futures to farm out the work to process chunks of datapoints.
        """
        results = []

        if self.local_path:
            chunk_count = None
        else:
            chunk_count = (len(self.dataset) // CHUNK_SIZE) + 1

        with ProcessPoolExecutor(max_workers=workers) as pool:
            for batch in tqdm(pool.map(self.from_chunk, self.chunk_generator()), total=chunk_count):
                results.extend(batch)

        return results

    def load(self, workers=WORKERS):
        """
        Load in this dataset; the workers parameter specifies how many processes
        should work on loading and scrubbing the data
        """
        start = datetime.now()
        print(f"Loading dataset {self.category}", flush=True)

        local_path = self._local_jsonl_path()

        if local_path:
            print(f"Loading from local JSONL: {local_path}", flush=True)
            self.local_path = local_path
            self.dataset = None
        else:
            print("Local file not found, loading from HuggingFace Hub", flush=True)
            self.local_path = None
            self.dataset = load_dataset(
                "McAuley-Lab/Amazon-Reviews-2023",
                f"raw_meta_{self.category}",
                split="full",
                trust_remote_code=True,
            )

        results = self.load_in_parallel(workers)

        finish = datetime.now()
        print(
            f"Completed {self.category} with {len(results):,} datapoints in {(finish - start).total_seconds() / 60:.1f} mins",
            flush=True,
        )
        return results
