from langgraph.graph import MessagesState


class RouteState(MessagesState):
    intent: str # 意图