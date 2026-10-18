#!/usr/bin/env python3
"""录课前预构建 Chroma 向量库（LITE 版，2万条）。
完全复刻 day2.ipynb cell[12] 逻辑：collection 'products'，每1000条一批。
构建产物：第八周/products_vectorstore/，录课时 cell[7-12] 秒加载。"""

import os
import sys
import time

# 工作目录固定为第八周（DB 相对路径与 notebook 一致）
os.chdir("/Users/macbook/projects/Learning_LLM/第八周")
sys.path.insert(0, "/Users/macbook/projects/Learning_LLM/第八周")

# 下载走镜像（更稳）；如失败可改走代理直连
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import chromadb
from agents.items import Item

DB = "products_vectorstore"
DATASET = "iloveawscn/items_lite"

print(f"[{time.strftime('%H:%M:%S')}] 1. 加载数据集 {DATASET} ...", flush=True)
train, val, test = Item.from_hub(DATASET)
print(f"   训练 {len(train):,} / 验证 {len(val):,} / 测试 {len(test):,}", flush=True)

print(f"[{time.strftime('%H:%M:%S')}] 2. 加载编码器 all-MiniLM-L6-v2 ...", flush=True)
encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
print("   编码器就绪", flush=True)

print(f"[{time.strftime('%H:%M:%S')}] 3. 连接 Chroma（{DB}）...", flush=True)
client = chromadb.PersistentClient(path=DB)

collection_name = "products"
existing = [c.name for c in client.list_collections()]
print(f"   现有 collections: {existing}", flush=True)

if collection_name in existing:
    col = client.get_or_create_collection(collection_name)
    print(f"   ✅ collection 已存在，count={col.count()}，跳过构建", flush=True)
else:
    collection = client.create_collection(collection_name)
    total = len(train)
    t0 = time.time()
    for i in tqdm(range(0, total, 1000), desc="encoding"):
        documents = [item.summary for item in train[i : i + 1000]]
        vectors = encoder.encode(documents).astype(float).tolist()
        metadatas = [
            {"category": item.category, "price": item.price}
            for item in train[i : i + 1000]
        ]
        ids = [f"doc_{j}" for j in range(i, i + 1000)]
        ids = ids[: len(documents)]
        collection.add(
            ids=ids, documents=documents, embeddings=vectors, metadatas=metadatas
        )
    dt = time.time() - t0
    col = client.get_or_create_collection(collection_name)
    print(f"   ✅ 构建完成 count={col.count()}，耗时 {dt/60:.1f} 分钟", flush=True)

print(f"[{time.strftime('%H:%M:%S')}] 全部完成", flush=True)
