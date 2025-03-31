# LLM 工程 - 掌握AI和大语言模型

## Mac 安装指南

欢迎使用Mac的朋友们！

首先我要坦白：搭建一个强大的AI前沿开发环境并不像我希望的那么简单。对大多数人来说这些指南会很顺利；但某些情况下，你可能会遇到问题。请不要犹豫联系我 - 我会帮你快速解决问题。没有什么比卡住更糟糕的了！

我使用Anaconda平台来设置你的环境。这是一个强大的工具，可以构建完整的科学环境。Anaconda确保你使用正确版本的Python，所有包都与我的兼容，即使我们的系统完全不同。它需要更多时间来设置，并且占用更多硬盘空间(5GB以上)，但一旦运行起来就非常可靠。

话虽如此：如果你在使用Anaconda时遇到任何问题，我提供了一个替代方案。它更快更简单，能让你快速运行，但兼容性保证较低。


### 第一部分：克隆仓库

这会在你的电脑上获取代码的本地副本。

1. **安装Git**(如果尚未安装，大多数情况下已经安装)

- 打开终端(应用程序 > 实用工具 > 终端)
- 输入`git --version` 如果未安装，系统会提示你安装

2. **导航到你的项目文件夹：**

如果你有专门的项目文件夹，使用cd命令导航到它。例如：
`cd ~/Documents/Projects`

如果没有项目文件夹，可以创建一个：
```
mkdir ~/Documents/Projects
cd ~/Documents/Projects
```

3. **克隆仓库：**

在终端中，在Projects文件夹下输入：

`git clone https://github.com/iloveawscn/Learning_LLM.git`

这会在你的Projects文件夹内创建一个名为`Learning_LLM`的新目录并下载课程代码。输入`cd Learning_LLM`进入该目录。这个`Learning_LLM`目录被称为"项目根目录"。

### 第二部分：安装Anaconda环境

如果这部分遇到问题，可以使用下面的替代方案2B部分。

1. **安装Anaconda：**

- 从https://docs.anaconda.com/anaconda/install/mac-os/下载Anaconda
- 双击下载的文件并按照安装提示操作。注意它会占用几GB空间并且需要一段时间安装，但这将是你未来使用的强大平台。
- 安装后，你需要打开一个新的终端才能使用它(甚至可能需要重启)。

2. **设置环境：**

- 打开一个**新**终端(应用程序 > 实用工具 > 终端)
- 使用`cd ~/Documents/Projects/Learning_LLM`导航到"项目根目录"(根据需要替换此路径为实际的Learning_LLM目录路径，即你本地克隆的仓库版本)。输入`ls`检查是否能看到课程每周的子目录。
- 创建环境：`conda env create -f environment.yml`
- 等待几分钟安装所有包 - 在某些情况下，如果你之前没有使用过Anaconda，这可能需要20-30分钟，甚至更长时间取决于你的网络连接。重要的事情正在发生！如果运行超过1小时15分钟，或者遇到其他问题，请转到2B部分。
- 你现在已经为LLM工程、运行向量数据库等构建了一个隔离的专用AI环境！现在你需要使用这个命令**激活**它：`conda activate llms`  

你应该在提示符中看到`(llms)`，这表示你已经激活了新环境。

3. **启动Jupyter Lab：**

在终端窗口中，从`Learning_LLM`文件夹内输入：`jupyter lab`

...Jupyter Lab应该在浏览器中打开。如果你之前没见过Jupyter Lab，我稍后会解释！现在关闭jupyter lab浏览器标签，关闭终端，继续第三部分。

### 2B部分 - 2部分的替代方案(如果Anaconda有问题)

1. **打开一个新终端**(应用程序 > 实用工具 > 终端)

运行`python --version`查看你使用的python版本。  
理想情况下你应该使用Python 3.11版本，这样我们完全同步。  
我认为Python 3.12也可以工作，但(截至2025年2月)Python 3.13还**不能**工作，因为几个数据科学依赖尚未准备好支持Python 3.13。  
如果需要安装Python或其他版本，可以在这里下载：  
https://www.python.org/downloads/

2. 使用`cd ~/Documents/Projects/Learning_LLM`导航到"项目根目录"(根据需要替换此路径为实际的Learning_LLM目录路径)。输入`ls`检查是否能看到课程每周的子目录。  

然后，使用这个命令创建一个新的虚拟环境：  
`python -m venv llms`

3. 使用以下命令激活虚拟环境：  
`source llms/bin/activate`
你应该在命令提示符中看到(llms)，这是事情进展顺利的标志。

4. 运行`python -m pip install --upgrade pip`然后`pip install -r requirements.txt`  
这可能需要几分钟安装。
在极少数情况下如果不顺利，你应该尝试这个更可靠(但更慢)的版本：  
`pip install --retries 5 --timeout 15 --no-cache-dir --force-reinstall -r requirements.txt`

5. **启动Jupyter Lab：**

从`Learning_LLM`文件夹内输入：`jupyter lab`  
...Jupyter Lab应该会打开，准备开始。打开`week1`文件夹并双击`day1.ipynb`。成功！现在关闭jupyter lab继续第三部分。

如果有任何问题，请联系我！

### 第三部分 - OpenAI密钥(可选但推荐)

特别是在课程的第1周和第2周，你将编写代码调用前沿模型的API(位于AI前沿的模型)。

第1周你只需要OpenAI，其他的可以以后根据需要添加。

1. 如果没有OpenAI账号，访问以下网址创建：
https://platform.openai.com/

2. OpenAI要求最低信用额度才能使用API。在美国是5美元。API调用将消耗这5美元。本课程我们只会使用一小部分。我建议你进行这项投资，因为你可以很好地利用它。但如果你不想为API付费，我在课程中提供了使用Ollama的替代方案。

你可以在设置 > 账单中添加OpenAI的信用余额：  
https://platform.openai.com/settings/organization/billing/overview

我建议你禁用自动充值！

3. 创建你的API密钥

设置OpenAI密钥的网页在https://platform.openai.com/api-keys - 点击绿色的'创建新的密钥'按钮，然后点击'创建密钥'。将API密钥保存在某个私密的地方；以后你将无法从OpenAI界面检索它。它应该以`sk-proj-`开头。

第2周我们还将设置Anthropic和Google的密钥，到时候你可以在这里操作。  
- Anthropic的Claude API在https://console.anthropic.com/  
- Google的Gemini API在https://ai.google.dev/gemini-api  

课程后期你将使用出色的HuggingFace平台；可以在https://huggingface.co免费创建账号 - 你可以从头像菜单 >> 设置 >> 访问令牌创建API令牌。

第6/7周你将使用优秀的Weights & Biases https://wandb.ai来监控你的训练批次。账号也是免费的，你可以用类似的方式设置令牌。

### 第四部分 - .env文件

当你有了这些密钥，请在项目根目录创建一个名为`.env`的新文件。文件名需要正好是四个字符".env"，而不是"my-keys.env"或".env.txt"。操作如下：

1. 打开终端(应用程序 > 实用工具 > 终端)

2. 使用`cd ~/Documents/Projects/Learning_LLM`导航到"项目根目录"(根据需要替换此路径为实际的Learning_LLM目录路径)。

3. 使用以下命令创建.env文件：

nano .env

4. 然后在nano中输入你的API密钥，将xxxx替换为你的API密钥(以`sk-proj-`开头)。

```
OPENAI_API_KEY=xxxx
```

如果你有其他密钥，也可以添加，或者以后几周再回来添加：  
```
GOOGLE_API_KEY=xxxx
ANTHROPIC_API_KEY=xxxx
DEEPSEEK_API_KEY=xxxx
HF_TOKEN=xxxx
```

5. 保存文件：

Control + O  
回车(确认保存文件)  
Control + X 退出编辑器

6. 使用这个命令列出项目根目录的文件：

`ls -a`

确认`.env`文件存在。

这个文件不会出现在Jupyter Lab中，因为jupyter会隐藏以点开头的文件。这个文件列在`.gitignore`文件中，所以不会被检入，你的密钥保持安全。

### 第五部分 - 开始吧！！

- 打开终端(应用程序 > 实用工具 > 终端)
  
- 使用`cd ~/Documents/Projects/Learning_LLM`导航到"项目根目录"(根据需要替换此路径为实际的Learning_LLM目录路径)。输入`ls`检查是否能看到课程每周的子目录。  

- 使用`conda activate llms`激活你的环境(如果你使用了2B部分的替代方案，则使用`source llms/bin/activate`)

- 你应该在提示符中看到(llms)，这表示一切正常。现在输入：`jupyter lab`，Jupyter Lab应该会打开，准备开始。打开`week1`文件夹并双击`day1.ipynb`。

你就可以开始了！

注意以后每次启动jupyter lab时，你都需要按照第五部分的说明，在`Learning_LLM`目录内启动，并且激活`llms`环境。

对于Jupyter Lab/Jupyter Notebook的新用户来说，这是一个令人愉快的数据科学环境，你可以在任何单元格中简单地按shift+return来运行它；从顶部开始，逐步向下！我包含了一个名为'Jupyter指南'的笔记本，向你展示更多功能。当我们在第3周转到Google Colab时，你将体验相同的界面，但在云中运行Python。

如果有任何问题，我在week1中包含了一个名为[troubleshooting.ipynb](week1/troubleshooting.ipynb)的笔记本来解决问题。

