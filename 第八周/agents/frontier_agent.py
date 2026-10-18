import re
from typing import List, Dict
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from agents.agent import Agent


class FrontierAgent(Agent):
    name = "Frontier Agent"
    color = Agent.BLUE

    MODEL = "gpt-4o-mini"

    def __init__(self, collection):
        """
        通过连接到 OpenAI 或 DeepSeek、Chroma 数据存储来设置此实例，
        并设置向量编码模型
        """
        self.log("Initializing Frontier Agent")
        self.client = OpenAI()
        self.MODEL = "gpt-5.1"
        self.log("Frontier Agent is setting up with OpenAI")
        self.collection = collection
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.log("Frontier Agent is ready")

    def make_context(self, similars: List[str], prices: List[float]) -> str:
        """
        创建可插入提示词的上下文
        :param similars: 与被估价产品相似的产品
        :param prices: 相似产品的价格
        :return: 插入提示词中提供上下文的文本
        """
        message = "To provide some context, here are some other items that might be similar to the item you need to estimate.\n\n"
        for similar, price in zip(similars, prices):
            message += f"Potentially related product:\n{similar}\nPrice is ${price:.2f}\n\n"
        return message

    def messages_for(
        self, description: str, similars: List[str], prices: List[float]
    ) -> List[Dict[str, str]]:
        """
        创建用于调用 OpenAI 的消息列表，包含系统和用户提示词
        :param description: 产品描述
        :param similars: 与此产品相似的产品
        :param prices: 相似产品的价格
        :return: 符合 OpenAI 格式要求的消息列表
        """
        message = f"Estimate the price of this product. Respond with the price, no explanation\n\n{description}\n\n"
        message += self.make_context(similars, prices)
        return [{"role": "user", "content": message}]

    def find_similars(self, description: str):
        """
        通过在 Chroma 数据存储中查找，返回与给定产品相似的项目列表
        """
        self.log(
            "Frontier Agent is performing a RAG search of the Chroma datastore to find 5 similar products"
        )
        vector = self.model.encode([description])
        results = self.collection.query(query_embeddings=vector.astype(float).tolist(), n_results=5)
        documents = results["documents"][0][:]
        prices = [m["price"] for m in results["metadatas"][0][:]]
        self.log("Frontier Agent has found similar products")
        return documents, prices

    def get_price(self, s) -> float:
        """
        从字符串中提取浮点数的工具函数
        """
        s = s.replace("$", "").replace(",", "")
        match = re.search(r"[-+]?\d*\.\d+|\d+", s)
        return float(match.group()) if match else 0.0

    def price(self, description: str) -> float:
        """
        调用 OpenAI 或 DeepSeek 来估算所描述产品的价格，
        通过查找 5 个相似产品并将其包含在提示词中提供上下文
        :param description: 产品描述
        :return: 价格估计
        """
        documents, prices = self.find_similars(description)
        self.log(
            f"Frontier Agent is about to call {self.MODEL} with context including 5 similar products"
        )
        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=self.messages_for(description, documents, prices),
            seed=42,
            reasoning_effort="none",
        )
        reply = response.choices[0].message.content
        result = self.get_price(reply)
        self.log(f"Frontier Agent completed - predicting ${result:.2f}")
        return result
