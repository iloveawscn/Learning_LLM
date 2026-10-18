from typing import Optional, List
from agents.agent import Agent
from agents.deals import ScrapedDeal, DealSelection, Deal, Opportunity
from agents.scanner_agent import ScannerAgent
from agents.ensemble_agent import EnsembleAgent
from agents.messaging_agent import MessagingAgent


class PlanningAgent(Agent):

    name = "Planning Agent"
    color = Agent.GREEN
    DEAL_THRESHOLD = 50

    def __init__(self, collection):
        """
        创建此规划器协调的 3 个 Agent 实例
        """
        self.log("Planning Agent is initializing")
        self.scanner = ScannerAgent()
        self.ensemble = EnsembleAgent(collection)
        self.messenger = MessagingAgent()
        self.log("Planning Agent is ready")

    def run(self, deal: Deal) -> Opportunity:
        """
        运行特定优惠的工作流程
        :param deal: 从 RSS 抓取并摘要的优惠信息
        :returns: 包含折扣的商机
        """
        self.log("Planning Agent is pricing up a potential deal")
        estimate = self.ensemble.price(deal.product_description)
        discount = estimate - deal.price
        self.log(f"Planning Agent has processed a deal with discount ${discount:.2f}")
        return Opportunity(deal=deal, estimate=estimate, discount=discount)

    def plan(self, memory: List[str] = []) -> Optional[Opportunity]:
        """
        运行完整工作流程：
        1. 使用 ScannerAgent 从 RSS 源查找优惠信息
        2. 使用 EnsembleAgent 估算价格
        3. 使用 MessagingAgent 发送优惠通知
        :param memory: 过去已展示的 URL 列表
        :return: 如果找到机会则返回 Opportunity，否则返回 None
        """
        self.log("Planning Agent is kicking off a run")
        selection = self.scanner.scan(memory=memory)
        if selection:
            opportunities = [self.run(deal) for deal in selection.deals[:5]]
            opportunities.sort(key=lambda opp: opp.discount, reverse=True)
            best = opportunities[0]
            self.log(f"Planning Agent has identified the best deal has discount ${best.discount:.2f}")
            if best.discount > self.DEAL_THRESHOLD:
                self.messenger.alert(best)
            self.log("Planning Agent has completed a run")
            return best if best.discount > self.DEAL_THRESHOLD else None
        return None