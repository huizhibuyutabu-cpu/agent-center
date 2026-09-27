from datetime import datetime

from agent.tianji.nodes.BaseNodeAgent import BaseNodeAgent
from agent.tianji.tools import query_course_by_id
from agent.prompts import system_prompt_config

class ConsultAgent(BaseNodeAgent):
    """
    课程咨询智能体
    """

    def system_prompt(self):
        return system_prompt_config.chat_consult_message

    def system_prompt_params(self):
        return {"now": datetime.now()}

    def tools(self):
        return [query_course_by_id]