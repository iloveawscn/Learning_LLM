from agents.agent import Agent
from agents.specialist_agent import SpecialistAgent
from agents.frontier_agent import FrontierAgent
from agents.neural_network_agent import NeuralNetworkAgent
from agents.preprocessor import Preprocessor


class EnsembleAgent(Agent):
    name = "Ensemble Agent"
    color = Agent.YELLOW

    def __init__(self, collection):
        """
        创建 Ensemble 实例，通过创建每个模型并加载集成权重
        """
        self.log("Initializing Ensemble Agent")
        self.specialist = SpecialistAgent()
        self.frontier = FrontierAgent(collection)
        self.neural_network = NeuralNetworkAgent()
        self.preprocessor = Preprocessor()
        self.log("Ensemble Agent is ready")

    def price(self, description: str) -> float:
        """
        运行此集成模型
        让每个模型对产品进行定价
        然后使用线性回归模型返回加权价格
        :param description: 产品描述
        :return: 价格估计
        """
        self.log("Running Ensemble Agent - preprocessing text")
        rewrite = self.preprocessor.preprocess(description)
        self.log(f"Pre-processed text using {self.preprocessor.model_name}")
        specialist = self.specialist.price(rewrite)
        frontier = self.frontier.price(rewrite)
        neural_network = self.neural_network.price(rewrite)
        combined = frontier * 0.8 + specialist * 0.1 + neural_network * 0.1
        self.log(f"Ensemble Agent complete - returning ${combined:.2f}")
        return combined
