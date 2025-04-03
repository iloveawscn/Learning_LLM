# LLM 工程 - 掌握人工智能与大语言模型

## Windows 系统安装指南

欢迎使用Windows系统的朋友！

首先需要说明：搭建前沿AI开发环境的过程可能比预期复杂。虽然多数情况下这些指引都能顺利执行，但偶尔可能会遇到问题。请随时联系我——我会帮助您快速解决问题，绝不让您卡在某个环节！

我们将使用Anaconda来构建开发环境。这个强大的工具能确保Python版本和软件包兼容性，虽然需要更多存储空间（约5GB以上），但能提供可靠的工作环境。

如果您遇到Anaconda安装问题，文末提供了替代方案（Part 2B）。

### 准备工作 - 重要提示！

### 第一部分：克隆代码仓库

1. **安装Git**
   - 官网下载：https://git-scm.com/download/win
   - 按默认选项安装

2. **打开命令提示符**
   - Win + R 输入cmd回车

3. **进入项目目录**
   ```
   cd C:\Users\您的用户名\Documents\Projects
   ```
   若无项目目录可新建：
   ```
   mkdir C:\Users\您的用户名\Documents\Projects
   cd C:\Users\您的用户名\Documents\Projects
   ```

4. **克隆仓库**
   ```
   git clone https://github.com/iloveawscn/Learning_LLM
   cd Learning_LLM
   ```

### 第二部分：安装Anaconda环境

1. **安装Anaconda**
   - 官网下载：https://docs.anaconda.com/anaconda/install/windows/

2. **配置环境**
   - 打开Anaconda Prompt
   - 进入项目根目录：
     ```
     cd C:\Users\您的用户名\Documents\Projects\Learning_LLM
     ```
   - 创建环境：
     ```
     conda env create -f environment.yml
     ```
   - 激活环境：
     ```
     conda activate llms
     ```

3. **启动Jupyter Lab**
   ```
   jupyter lab
   ```

### 第二部分备选方案（若Anaconda安装失败）

1. **检查Python版本**
   ```
   python --version
   ```
   推荐Python 3.11/3.12

2. **创建虚拟环境**
   ```
   python -m venv llms
   llms\Scripts\activate
   ```

3. **安装依赖**
   ```
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **启动Jupyter Lab**
   ```
   jupyter lab
   ```

### 第三部分：OpenAI密钥（推荐配置）

1. 注册OpenAI账号：https://platform.openai.com/
2. 充值至少$5余额
3. 创建API密钥（以sk-proj-开头）

### 第四部分：配置.env文件

1. 新建文本文件，内容：
   ```
   OPENAI_API_KEY=您的密钥
   ```
2. 另存为`.env`文件到项目根目录
3. 确保文件扩展名正确（非.txt）

### 第五部分：开始使用！

1. 在Anaconda Prompt中：
   ```
   cd C:\Users\您的用户名\Documents\Projects\Learning_LLM
   conda activate llms
   jupyter lab
   ```
2. 打开week1/day1.ipynb开始学习

祝学习顺利！