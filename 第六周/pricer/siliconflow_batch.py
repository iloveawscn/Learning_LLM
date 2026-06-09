"""SiliconFlow Batch API 封装，复用 batch.py 设计，适配 SiliconFlow 差异"""
import os
import json
import pickle
import time
import requests
from pathlib import Path
from tqdm.notebook import tqdm
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.environ["SILICONCLOUD_API_KEY"]
BASE = "https://api.siliconflow.cn/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
CONTENT_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

MODEL = "deepseek-ai/DeepSeek-V3"  # SiliconFlow Batch API 只支持 V3
BATCHES_FOLDER = "batches"
OUTPUT_FOLDER = "output"

SYSTEM_PROMPT = """Create a concise description of a product. Respond only in this format. Do not include part numbers.
Title: Rewritten short precise title
Category: eg Electronics
Brand: Brand name
Description: 1 sentence description
Details: 1 sentence on features"""


class SiliconFlowBatch:
    BATCH_SIZE = 1_000

    batches = []

    def __init__(self, items, start, end, lite):
        self.items = items
        self.start = start
        self.end = end
        self.filename = f"{start}_{end}.jsonl"
        self.file_id = None
        self.batch_id = None
        self.output_file_id = None
        self.done = False
        self.error = None
        folder = Path("siliconflow_lite") if lite else Path("siliconflow_full")
        self.batches_dir = folder / BATCHES_FOLDER
        self.output_dir = folder / OUTPUT_FOLDER
        self.batches_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def make_jsonl(self, item):
        body = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": item.full},
            ],
            "temperature": 0.2,
            "max_tokens": 300,
        }
        line = {
            "custom_id": str(item.id),
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": body,
        }
        return json.dumps(line, ensure_ascii=False)

    def make_file(self):
        batch_file = self.batches_dir / self.filename
        with batch_file.open("w", encoding="utf-8") as f:
            for item in self.items[self.start : self.end]:
                f.write(self.make_jsonl(item))
                f.write("\n")

    def send_file(self):
        batch_file = self.batches_dir / self.filename
        with batch_file.open("rb") as f:
            r = requests.post(
                f"{BASE}/files",
                headers=HEADERS,
                files={"file": (self.filename, f, "application/jsonl")},
                data={"purpose": "batch"},
            )
        if r.status_code not in (200, 201):
            raise RuntimeError(
                f"上传文件失败: status={r.status_code}, body={r.text[:500]}"
            )
        resp = r.json()
        self.file_id = resp.get("data", {}).get("id") or resp.get("id")
        if not self.file_id:
            raise RuntimeError(f"上传文件失败，无 file_id: {r.text[:300]}")

    def submit_batch(self):
        payload = {
            "input_file_id": self.file_id,
            "endpoint": "/v1/chat/completions",
            "completion_window": "24h",
        }
        r = requests.post(
            f"{BASE}/batches", headers=CONTENT_HEADERS, json=payload
        )
        if r.status_code not in (200, 201):
            raise RuntimeError(
                f"创建 batch 失败: status={r.status_code}, body={r.text[:500]}"
            )
        resp = r.json()
        data = resp.get("data", resp)
        self.batch_id = data.get("id")
        status = data.get("status")
        if not self.batch_id:
            raise RuntimeError(f"创建 batch 失败: {r.text[:300]}")
        if status in ("failed", "expired", "cancelled"):
            self.error = f"batch 创建后立即失败: {status}"
            self.done = True

    def is_ready(self):
        r = requests.get(f"{BASE}/batches/{self.batch_id}", headers=HEADERS)
        r.raise_for_status()
        resp = r.json()
        data = resp.get("data", resp)
        status = data.get("status")
        if status == "completed":
            self.output_file_id = data.get("output_file_id")
            return True
        if status in ("failed", "expired", "cancelled"):
            self.error = f"batch 失败: {status}, {json.dumps(data, ensure_ascii=False)[:300]}"
            self.done = True
            return False
        return False

    def fetch_output(self):
        """下载 batch 结果。SiliconFlow 的 output_file_id 是 OSS 直链 URL。"""
        if not self.output_file_id:
            raise RuntimeError("output_file_id 为空")
        output_file = self.output_dir / self.filename
        r = requests.get(self.output_file_id)
        if r.status_code != 200:
            raise RuntimeError(
                f"下载结果失败: status={r.status_code}, body={r.text[:200]}"
            )
        output_file.write_bytes(r.content)

    def apply_output(self):
        output_file = self.output_dir / self.filename
        count = 0
        issues = []
        with output_file.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                json_line = json.loads(line)
                cid = int(json_line["custom_id"])
                summary = json_line["response"]["body"]["choices"][0]["message"][
                    "content"
                ]
                self.items[cid].summary = summary
                count += 1
                # 质量检查
                problem = SiliconFlowBatch.validate_summary(summary)
                if problem:
                    issues.append((cid, problem))
        if issues:
            print(f"  Batch {self.filename}: {len(issues)} quality issues:")
            for cid, problem in issues[:5]:
                preview = (self.items[cid].summary or "")[:60]
                print(f"    [{cid}] {problem}: {preview}")
            if len(issues) > 5:
                print(f"    ... and {len(issues) - 5} more")
        self.done = True
        return count

    @staticmethod
    def validate_summary(summary):
        """检查 summary 质量，返回问题描述或 None"""
        if not summary or not summary.strip():
            return "empty"
        s = summary.strip()
        if s.startswith("{") or s.startswith("["):
            return "json_output"
        if "```" in s:
            return "markdown"
        required = ["Title:", "Category:", "Brand:", "Description:", "Details:"]
        missing = [f for f in required if f not in s]
        if missing:
            return f"missing_fields({','.join(missing)})"
        return None

    @classmethod
    def create(cls, items, lite):
        cls.batches = []
        for start in range(0, len(items), cls.BATCH_SIZE):
            end = min(start + cls.BATCH_SIZE, len(items))
            batch = cls(items, start, end, lite)
            cls.batches.append(batch)
        print(f"Created {len(cls.batches)} batches")

    @classmethod
    def run(cls):
        """提交所有未提交的 batch"""
        submitted = 0
        skipped = 0
        for batch in tqdm(cls.batches, desc="Submitting"):
            if batch.batch_id:
                skipped += 1
                continue
            if batch.done and batch.error:
                continue
            batch.make_file()
            batch.send_file()
            batch.submit_batch()
            submitted += 1
        print(f"Submitted {submitted} batches, skipped {skipped} already submitted")

    @classmethod
    def fetch(cls, poll_interval=3, max_wait=3600):
        """轮询并下载已完成的 batch 结果"""
        pending = [b for b in cls.batches if not b.done]
        if not pending:
            print("All batches already done")
            return

        print(f"Polling {len(pending)} pending batches...")
        start_time = time.time()
        while True:
            still_pending = [b for b in cls.batches if not b.done and b.batch_id]
            if not still_pending:
                break
            if time.time() - start_time > max_wait:
                print(f"Timeout after {max_wait}s, {len(still_pending)} still pending")
                break

            for batch in still_pending:
                try:
                    if batch.is_ready():
                        batch.fetch_output()
                        count = batch.apply_output()
                        print(f"  Batch {batch.filename}: {count} results")
                except Exception as e:
                    batch.error = str(e)
                    batch.done = True
                    print(f"  Batch {batch.filename} ERROR: {e}")

            done_count = sum(1 for b in cls.batches if b.done and not b.error)
            err_count = sum(1 for b in cls.batches if b.done and b.error)
            pend_count = sum(1 for b in cls.batches if not b.done)
            if pend_count == 0:
                break
            print(f"  Status: {done_count} done, {err_count} errors, {pend_count} pending")
            time.sleep(poll_interval)

        done = [b for b in cls.batches if b.done and not b.error]
        errors = [b for b in cls.batches if b.error]
        print(f"Finished: {len(done)} success, {len(errors)} errors out of {len(cls.batches)}")
        if errors:
            print("Failed batches:")
            for b in errors:
                print(f"  {b.filename}: {b.error}")

    @classmethod
    def save(cls, lite):
        folder = Path("siliconflow_lite") if lite else Path("siliconflow_full")
        state_path = folder / "batches.pkl"
        items_ref = cls.batches[0].items if cls.batches else None
        # 临时置空 items 避免 pickle 大量数据
        for batch in cls.batches:
            batch.items = None
        with state_path.open("wb") as f:
            pickle.dump(cls.batches, f)
        for batch in cls.batches:
            batch.items = items_ref
        print(f"Saved {len(cls.batches)} batches to {state_path}")

    @classmethod
    def load(cls, items, lite):
        folder = Path("siliconflow_lite") if lite else Path("siliconflow_full")
        state_path = folder / "batches.pkl"
        with state_path.open("rb") as f:
            cls.batches = pickle.load(f)
        for batch in cls.batches:
            batch.items = items
        done = sum(1 for b in cls.batches if b.done and not b.error)
        errors = sum(1 for b in cls.batches if b.error)
        pending = sum(1 for b in cls.batches if not b.done)
        print(
            f"Loaded {len(cls.batches)} batches: {done} done, {errors} errors, {pending} pending"
        )
