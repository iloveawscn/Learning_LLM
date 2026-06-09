"""运行 lite batch: 22K 条 → SiliconFlow Batch → 验证 → 导出 Parquet"""
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from pricer.items import Item
from pricer.siliconflow_batch import SiliconFlowBatch

print("=" * 60)
print("[1] 加载 items_raw_lite")
print("=" * 60)

train, val, test = Item.from_hub("iloveawscn/items_raw_lite")
items = train + val + test
print(f"Loaded {len(items):,} items (train={len(train)}, val={len(val)}, test={len(test)})")

# 设置 id
for index, item in enumerate(items):
    item.id = index
print(f"IDs set: 0 ~ {len(items)-1}")

print("\n" + "=" * 60)
print("[2] 创建 batches")
print("=" * 60)

SiliconFlowBatch.create(items, lite=True)

print("\n" + "=" * 60)
print("[3] 提交 batches")
print("=" * 60)

SiliconFlowBatch.run()

# 保存状态（断点续跑用）
SiliconFlowBatch.save(lite=True)

print("\n" + "=" * 60)
print("[4] 轮询并下载结果")
print("=" * 60)

SiliconFlowBatch.fetch(poll_interval=5, max_wait=7200)

# 再保存一次
SiliconFlowBatch.save(lite=True)

print("\n" + "=" * 60)
print("[5] 验证结果")
print("=" * 60)

missing = [i for i, item in enumerate(items) if not item.summary]
empty = [i for i, item in enumerate(items) if item.summary and not item.summary.strip()]
has_markdown = [i for i, item in enumerate(items) if item.summary and "```" in item.summary]
has_json = [i for i, item in enumerate(items) if item.summary and (item.summary.strip().startswith("{") or item.summary.strip().startswith("["))]

print(f"  总条数: {len(items)}")
print(f"  有 summary: {len([i for i in items if i.summary])}")
print(f"  缺失 summary: {len(missing)}")
print(f"  空 summary: {len(empty)}")
print(f"  含 markdown: {len(has_markdown)}")
print(f"  含 JSON: {len(has_json)}")

# 打印 10 条随机样例
import random
random.seed(42)
sample_indices = random.sample(range(len(items)), min(10, len(items)))
print("\n  随机 10 条 summary 样例:")
for idx in sample_indices:
    s = items[idx].summary or "MISSING"
    print(f"  [{idx}] {s[:100]}")

# 列出失败的 batch
errors = [b for b in SiliconFlowBatch.batches if b.error]
if errors:
    print(f"\n  失败的 batch ({len(errors)}):")
    for b in errors:
        print(f"    {b.filename}: {b.error}")

if missing:
    print(f"\n  缺失 summary 的 item ids (前 20): {missing[:20]}")

print("\n" + "=" * 60)
print("[6] 清理字段 + 导出 Parquet")
print("=" * 60)

for item in items:
    item.full = None
    item.id = None

train_items = items[:20_000]
val_items = items[20_000:21_000]
test_items = items[21_000:]

Item.export_to_parquet(
    "exported_datasets/items_lite",
    train=train_items,
    val=val_items,
    test=test_items,
)

print("\n" + "=" * 60)
print("[完成] lite batch 处理完毕")
print("=" * 60)
print("下一步: hf upload-large-folder iloveawscn/items_lite ./exported_datasets/items_lite --repo-type dataset")
