import modal
from modal import Volume, Image
# 设置 - 用代码定义基础设施！

app = modal.App("pricer-service")
image = Image.debian_slim().pip_install(
    "huggingface", "torch", "transformers", "bitsandbytes", "accelerate", "peft"
)

# 从 Modal 收集密钥。
# 根据你的 Modal 配置，可能需要将 "huggingface-secret" 替换为 "hf-secret"
secrets = [modal.Secret.from_name("huggingface-secret")]

GPU = "T4"
BASE_MODEL = "meta-llama/Llama-3.2-3B"
PROJECT_NAME = "price"
HF_USER = "iloveawscn"  # 你的 HF 用户名
RUN_NAME = "2025-11-28_18.47.07"
PROJECT_RUN_NAME = f"{PROJECT_NAME}-{RUN_NAME}"
REVISION = "826c7e122cbba3b9303b47c641c5322e369c5d1c"  # 修复后的 6200 步最佳 checkpoint
FINETUNED_MODEL = f"{HF_USER}/{PROJECT_RUN_NAME}"
CACHE_DIR = "/cache"

# 如果希望 Modal 始终运行，将此值改为 1，否则 2 分钟后会进入休眠状态
MIN_CONTAINERS = 0

PREFIX = "Price is $"
QUESTION = "What does this cost to the nearest dollar?"

hf_cache_volume = Volume.from_name("hf-hub-cache", create_if_missing=True)


@app.cls(
    image=image.env({"HF_HUB_CACHE": CACHE_DIR}),
    secrets=secrets,
    gpu=GPU,
    timeout=1800,
    min_containers=MIN_CONTAINERS,
    volumes={CACHE_DIR: hf_cache_volume},
)
class Pricer:
    @modal.enter()
    def setup(self):
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
        from peft import PeftModel

        # 量化配置
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
        )

        # 加载模型和分词器
        self.tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        self.base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL, quantization_config=quant_config, device_map="auto"
        )
        self.fine_tuned_model = PeftModel.from_pretrained(
            self.base_model, FINETUNED_MODEL, revision=REVISION
        )

    @modal.method()
    def price(self, description: str) -> float:
        import re
        import torch
        from transformers import set_seed

        set_seed(42)
        prompt = f"{QUESTION}\n\n{description}\n\n{PREFIX}"

        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to("cuda")
        with torch.no_grad():
            outputs = self.fine_tuned_model.generate(inputs, max_new_tokens=5)
        result = self.tokenizer.decode(outputs[0])
        contents = result.split("Price is $")[1]
        contents = contents.replace(",", "")
        match = re.search(r"[-+]?\d*\.\d+|\d+", contents)
        return float(match.group()) if match else 0
