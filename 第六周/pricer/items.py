from pydantic import BaseModel
from datasets import Dataset, DatasetDict, load_dataset
from typing import Optional, Self


PREFIX = "Price is $"
QUESTION = "What does this cost to the nearest dollar?"


class Item(BaseModel):
    """
    An Item is a data-point of a Product with a Price
    """

    title: str
    category: str
    price: float
    full: Optional[str] = None
    weight: Optional[float] = None
    summary: Optional[str] = None
    prompt: Optional[str] = None
    id: Optional[int] = None

    def make_prompt(self, text: str):
        self.prompt = f"{QUESTION}\n\n{text}\n\n{PREFIX}{round(self.price)}.00"

    def test_prompt(self) -> str:
        return self.prompt.split(PREFIX)[0] + PREFIX

    def __repr__(self) -> str:
        return f"<{self.title} = ${self.price}>"

    @staticmethod
    def push_to_hub(dataset_name: str, train: list[Self], val: list[Self], test: list[Self]):
        """Push Item lists to HuggingFace Hub"""
        DatasetDict(
            {
                "train": Dataset.from_list([item.model_dump() for item in train]),
                "validation": Dataset.from_list([item.model_dump() for item in val]),
                "test": Dataset.from_list([item.model_dump() for item in test]),
            }
        ).push_to_hub(dataset_name)

    @staticmethod
    def export_to_parquet(
        output_dir: str,
        train: list[Self],
        val: list[Self],
        test: list[Self],
        max_shard_bytes: int = 200_000_000,  # 200MB per shard
    ):
        """导出为 Parquet 分片目录，符合 HuggingFace Hub 标准格式"""
        import math
        from pathlib import Path

        output_path = Path(output_dir)
        data_dir = output_path / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        splits = {"train": train, "validation": val, "test": test}

        for split_name, items in splits.items():
            ds = Dataset.from_list([item.model_dump() for item in items])

            # 计算 shard 数量
            table = ds.data.table
            nbytes = table.nbytes
            num_shards = max(1, math.ceil(nbytes / max_shard_bytes))

            # 分 shard 导出
            for shard_idx in range(num_shards):
                shard = ds.shard(num_shards, shard_idx, contiguous=True)
                filename = f"{split_name}-{shard_idx:05d}-of-{num_shards:05d}.parquet"
                shard.to_parquet(str(data_dir / filename))

            print(f"  {split_name}: {len(items):,} items -> {num_shards} shards")

        # 生成 README.md
        readme_path = output_path / "README.md"
        readme_path.write_text(f"""---
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-*.parquet
  - split: validation
    path: data/validation-*.parquet
  - split: test
    path: data/test-*.parquet
dataset_info:
  splits:
  - name: train
    num_examples: {len(train)}
  - name: validation
    num_examples: {len(val)}
  - name: test
    num_examples: {len(test)}
---
# items_raw_full

Amazon Reviews 2023 product items for price prediction.
""")

        print(f"Exported to {output_path}")
        return output_path

    @classmethod
    def from_hub(cls, dataset_name: str) -> tuple[list[Self], list[Self], list[Self]]:
        """Load from HuggingFace Hub and reconstruct Items"""
        ds = load_dataset(dataset_name)
        return (
            [cls.model_validate(row) for row in ds["train"]],
            [cls.model_validate(row) for row in ds["validation"]],
            [cls.model_validate(row) for row in ds["test"]],
        )
