import logging

class Agent:
    """
    Agent 的抽象基类
    用于以可识别每个 Agent 的方式记录日志消息
    """

    # 前景色
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # 背景色
    BG_BLACK = '\033[40m'
    
    # 重置代码，恢复默认颜色
    RESET = '\033[0m'

    name: str = ""
    color: str = '\033[37m'

    def log(self, message):
        """
        记录信息级别的日志，标识出是哪个 Agent
        """
        color_code = self.BG_BLACK + self.color
        message = f"[{self.name}] {message}"
        logging.info(color_code + message + self.RESET)