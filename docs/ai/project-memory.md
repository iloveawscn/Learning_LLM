# Project Memory

## 基本信息

- **项目名**: Learning_LLM
- **项目类型**: 8周 LLM 工程学习课程
- **当前阶段**: 进行中（第五周有未提交改动）

## 技术栈

- Python 3
- Jupyter Notebook / Jupyter Lab
- PyTorch, Transformers, LangChain
- Gradio（界面）
- Ollama（本地模型）

## 依赖

- 见 requirements.txt（39个依赖）
- 主要：torch, transformers, langchain, openai, anthropic, gradio

## 目录结构

- `第一周/` ~ `第八周/`：按周组织的课程内容
- `tests/`：测试文件
- `docs/`：课程文档和交接记录

## 常用命令

- 安装：`pip install -r requirements.txt`
- 启动：`jupyter notebook`

## 历史决策

- 使用 Ollama 本地运行 llama3.2（不是 llama3.3，太大）
- OpenAI API 优先使用 gpt-4o-mini 降低成本
- Anthropic 优先使用 claude-3-haiku-20240307

## 踩坑记录

- Llama3.3 有700亿参数，对家用电脑太大，避免使用
- API 费用需要监控，见 README.md 中的仪表板链接

## 待确认事项

- 第五周的 app.py 和 evaluation/eval.py 未提交，需确认是否需要提交