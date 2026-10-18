import os
from agents.deals import Opportunity
from agents.agent import Agent
from litellm import completion
import requests

pushover_url = "https://api.pushover.net/1/messages.json"


class MessagingAgent(Agent):
    name = "Messaging Agent"
    color = Agent.WHITE
    MODEL = "gpt-5.1"

    def __init__(self):
        """
        设置此对象以通过 Pushover 发送推送通知，
        或通过 Twilio 发送短信，
        具体方式由常量指定
        """
        self.log("Messaging Agent is initializing")
        self.pushover_user = os.getenv("PUSHOVER_USER", "your-pushover-user-if-not-using-env")
        self.pushover_token = os.getenv("PUSHOVER_TOKEN", "your-pushover-user-if-not-using-env")
        self.log("Messaging Agent has initialized Pushover and GPT-5.1")

    def push(self, text):
        """
        使用 Pushover API 发送推送通知
        """
        self.log("Messaging Agent is sending a push notification")
        payload = {
            "user": self.pushover_user,
            "token": self.pushover_token,
            "message": text,
            "sound": "cashregister",
        }
        requests.post(pushover_url, data=payload)

    def alert(self, opportunity: Opportunity):
        """
        针对指定的商机发送警报
        """
        text = f"Deal Alert! Price=${opportunity.deal.price:.2f}, "
        text += f"Estimate=${opportunity.estimate:.2f}, "
        text += f"Discount=${opportunity.discount:.2f} :"
        text += opportunity.deal.product_description[:10] + "... "
        text += opportunity.deal.url
        self.push(text)
        self.log("Messaging Agent has completed")

    def craft_message(
        self, description: str, deal_price: float, estimated_true_value: float
    ) -> str:
        user_prompt = "Please summarize this great deal in 2-3 sentences to be sent as an exciting push notification alerting the user about this deal.\n"
        user_prompt += f"Item Description: {description}\nOffered Price: {deal_price}\nEstimated true value: {estimated_true_value}"
        user_prompt += "\n\nRespond only with the 2-3 sentence message which will be used to alert & excite the user about this deal"
        response = completion(
            model=self.MODEL,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content

    def notify(self, description: str, deal_price: float, estimated_true_value: float, url: str):
        """
        针对指定详情发送警报
        """
        self.log("Messaging Agent is using GPT-5.1 to craft the message")
        text = self.craft_message(description, deal_price, estimated_true_value)
        self.push(text[:200] + "... " + url)
        self.log("Messaging Agent has completed")
