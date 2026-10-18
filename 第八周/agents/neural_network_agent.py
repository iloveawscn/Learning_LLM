from agents.agent import Agent
from agents.deep_neural_network import DeepNeuralNetworkInference


class NeuralNetworkAgent(Agent):
    name = "Neural Network Agent"
    color = Agent.MAGENTA

    def __init__(self):
        """
        通过加载保存的模型权重和 SentenceTransformer 向量编码模型来初始化此对象
        """
        self.log("Neural Network Agent is initializing")
        self.neural_network = DeepNeuralNetworkInference()
        self.neural_network.setup()
        self.neural_network.load("deep_neural_network.pth")
        self.log("Neural Network Agent is ready and weights are loaded")

    def price(self, description: str) -> float:
        """
        使用深度神经网络估算所描述商品的价格
        :param description: 待估价的产品
        :return: 价格（浮点数）
        """
        self.log("Neural Network Agent is starting a prediction")
        result = self.neural_network.inference(description)
        self.log(f"Neural Network Agent completed - predicting ${result:.2f}")
        return result
