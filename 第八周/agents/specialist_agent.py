import modal
from agents.agent import Agent


class SpecialistAgent(Agent):
    """
    一个运行我们在 Modal 上远程部署的微调 LLM 的 Agent
    """

    name = "Specialist Agent"
    color = Agent.RED

    def __init__(self):
        """
        通过创建 modal 类的实例来设置此 Agent
        """
        self.log("Specialist Agent is initializing - connecting to modal")
        Pricer = modal.Cls.from_name("pricer-service", "Pricer")
        self.pricer = Pricer()

    def price(self, description: str) -> float:
        """
        远程调用以返回此商品的价格估计
        """
        self.log("Specialist Agent is calling remote fine-tuned model")
        result = self.pricer.price.remote(description)
        self.log(f"Specialist Agent completed - predicting ${result:.2f}")
        return result
