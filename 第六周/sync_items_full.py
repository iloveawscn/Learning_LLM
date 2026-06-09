"""从 ed-donner/items_full 同步到 iloveawscn/items_full"""
import os
import sys

os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

sys.path.insert(0, "/Users/macbook/projects/Learning_LLM/第六周")
from pricer.items import Item

print("=" * 60)
print("[1] 加载 ed-donner/items_full")
print("=" * 60)

train, val, test = Item.from_hub("ed-donner/items_full")
items = train + val + test
print(f"Loaded {len(items):,} items (train={len(train)}, val={len(val)}, test={len(test)})")

# 清理不需要的字段（ed-donner 的数据可能没有 id）
for item in items:
    item.id = None
    item.full = None

print("\n" + "=" * 60)
print("[2] 导出 Parquet 分片")
print("=" * 60)

Item.export_to_parquet(
    "exported_datasets/items_full",
    train=train,
    val=val,
    test=test,
)

print("\n" + "=" * 60)
print("[3] 上传到 iloveawscn/items_full")
print("=" * 60)

print("Export done. Run:")
print("  hf upload-large-folder iloveawscn/items_full ./exported_datasets/items_full --repo-type dataset")