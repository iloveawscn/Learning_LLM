# LLM工程 - 掌握人工智能和大语言模型

## 你的8周专业之旅从今天开始

很高兴你能和我一起踏上这段旅程。在接下来的几周里，我们将构建一些令人满意的项目。有些项目简单，有些具有挑战性，许多项目会让你感到惊叹！这些项目是循序渐进的，让你能够逐周深入积累专业知识。有一点是确定的：在这个过程中你一定会收获很多乐趣。

### 开始之前

我会尽全力帮助你在学习过程中取得最好的成果！如果你遇到任何问题，或者有任何改进课程的建议，请提交至我们的课程官网：iloveaws.cn，或者在课程下方留言。

## 第1周第1天的快速上手指南

### 重要提示：请注意下面关于Llama3.3的警告 - 它对家用电脑来说太大了！请坚持使用llama3.2！有几位学员错过了这个警告...

我们将通过安装Ollama开始课程，让你能立即看到成果！
1. 从https://ollama.com 下载并安装Ollama，注意在PC上可能需要管理员权限才能正确安装
2. 在PC上，启动命令提示符/Powershell（按Win + R，输入`cmd`，然后按Enter）。在Mac上，启动终端（应用程序 > 实用工具 > 终端）。
3. 运行`ollama run llama3.2`，或者对于配置较低的机器，尝试运行`ollama run llama3.2:1b` - **请注意**避免使用Meta最新的llama3.3模型，因为它有700亿参数，对大多数家用电脑来说太大了！
4. 如果这不起作用：你可能需要在另一个Powershell（Windows）或终端（Mac）中运行`ollama serve`，然后重试步骤3。在PC上，你可能需要在管理员权限的Powershell中运行。

如有任何问题，请联系我！

## 然后，环境配置说明

在我们完成Ollama快速项目，并且在我介绍完自己和课程之后，我们就开始进行完整的环境配置。

希望我已经把这些指南做得足够完善

- PC用户请按照[SETUP-PC.md](SETUP-PC.md)中的说明操作
- Mac用户请按照[SETUP-mac.md](SETUP-mac.md)中的说明操作
- Linux用户请按照[SETUP-linux.md](SETUP-linux.md)中的说明操作

在这个文件夹中也有PDF版本的配置说明，如果你更喜欢这种格式。

### 关于API费用的重要说明（这是可选的！如果你不想花钱可以不用）

在课程中，我会建议你尝试使用处于进步前沿的领先模型，即前沿模型。我还会建议你使用Google Colab运行开源模型。这些服务会产生一些费用，但我会把成本控制在最低限度 - 比如，每次只需几分钱。如果你不想使用这些服务，我也会提供替代方案。

请务必监控你的API使用情况，确保你对支出感到舒适；我在下面提供了相关链接。整个课程你不需要花费超过几美元。一些AI提供商如OpenAI要求最低充值5美元或等值货币；我们应该只会用到其中的一小部分，剩余的额度你可以在自己的项目中充分利用。在第7周，如果你享受这个过程，你可以选择多花一点钱 - 我自己花了大约10美元，结果让我非常满意！但这完全不是必需的；重要的是你要专注于学习。

### 付费API的免费替代方案

在课程早期，我会向你展示如果你不想在API上花钱的替代方案：
任何时候当我们有这样的代码：
`openai = OpenAI()`
你都可以直接用这个替代：
`openai = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')`

下面是一个完整的示例：

```
# 你需要在电脑上执行一次这个命令
!ollama pull llama3.2

from openai import OpenAI
MODEL = "llama3.2"
openai = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

response = openai.chat.completions.create(
 model=MODEL,
 messages=[{"role": "user", "content": "2 + 2等于多少？"}]
)

print(response.choices[0].message.content)
```

### 代码仓库的组织结构

每个"周"都有对应的文件夹，代表课程的不同模块，最终在第8周culminating在一个强大的自主代理AI解决方案，这个解决方案会用到前面很多周的内容。
按照上面的配置说明进行操作，然后打开第1周的文件夹，准备开始愉快的学习之旅。

### 最重要的部分

课程的宗旨是：最好的学习方式是通过**实践**。在课程中我不会输入所有的代码；我会为你执行代码来展示结果。你应该跟着我一起操作或在每节课后运行每个单元，检查对象以详细了解发生了什么。然后调整代码，使其成为你自己的作品。整个课程中都有很多有趣的挑战。

## 从第3周开始，我们还将使用Google Colab来运行GPU

你应该能够使用免费层级或最少的花费来完成课程中的所有项目。我个人注册了Colab Pro+并且很喜欢它 - 但这不是必需的。

在[这里](https://colab.research.google.com/)了解Google Colab并设置Google账户（如果你还没有的话）


### 监控API费用

你可以在整个课程中将API支出保持在很低的水平；你可以在这些仪表板上监控支出：OpenAI在[这里](https://platform.openai.com/usage)，Anthropic在[这里](https://console.anthropic.com/settings/cost)，Google Gemini在[这里](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/cost)。

本课程中的练习费用应该始终很低，但如果你想将它们控制在最低限度，那么一定要始终选择模型的最便宜版本：
1. 对于OpenAI：在代码中始终使用模型`gpt-4o-mini`而不是`gpt-4o`
2. 对于Anthropic：在代码中始终使用模型`claude-3-haiku-20240307`而不是其他Claude模型
3. 在第7周，注意查看我关于使用更便宜数据集的说明
