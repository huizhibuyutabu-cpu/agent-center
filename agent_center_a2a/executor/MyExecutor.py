import logging
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import TaskArtifactUpdateEvent, TaskStatusUpdateEvent, TaskState, TaskStatus
from a2a.utils import new_text_artifact

from agent.BaseAgent import BaseAgent
from agent.result import CourseInfo, PrePlaceOrder
from util import JsonUtil

logger = logging.getLogger(__name__)


class MyExecutor(AgentExecutor):
    """
    MyExecutor 执行器（面向 A2A 执行框架）。

    功能：
        - 接收 RequestContext 中的用户消息
        - 调用 agent 执行逻辑（通常是 LLM 流式响应）
        - 将 agent 产生的事件逐条推送到前端（EventQueue）
        - 在消息流结束后，检查并返回工具执行结果（tool result）
        - 发送最终 Task 状态（completed）

    """

    def __init__(self, agent: BaseAgent):
        """
        初始化执行器。

        参数:
            agent (BaseAgent): 业务层的智能体对象，必须实现 execute(message) 方法，
                               且返回一个异步生成器，按流式输出内容。
        """
        self.agent = agent

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        执行主流程（核心逻辑）。

        步骤：
            1. 校验输入 message
            2. 调用 agent.execute() 获取流式返回数据
            3. 将每个事件作为 TaskArtifactUpdateEvent 推送到客户端
            4. 如果是工具事件，进行判断类型，将结果metadata方式传递会客户端
            5. 发送最终 TaskStatusUpdateEvent（标记任务完成）

        参数:
            context (RequestContext): 请求上下文（包含 message、task_id、context_id 等）
            event_queue (EventQueue): 用于向 A2A 系统发送事件
        """
        if not context.message:
            raise Exception('No message provided')

        tool_result = {}
        # 使用 agent 的异步生成器流式输出结果
        async for event in self.agent.execute(context.message):
            # 构建并发送 artifact 更新事件（发送给客户端）
            if not event.get("tool", False):
                message = TaskArtifactUpdateEvent(
                    context_id=context.context_id,
                    task_id=context.task_id,
                    artifact=new_text_artifact(
                        name="current_result",  # 客户端可根据 name 识别当前内容
                        text=event.get("content"),  # LLM 产生的文本
                    ),
                )
                await event_queue.enqueue_event(message)
            else:
                _content = event.get("content")
                tool_name = event.get("name")

                # 打印工具事件内容，方便排查 _content 实际值
                logger.debug(
                    f"[tool event] name={tool_name}, "
                    f"content={_content!r}, type={type(_content).__name__}"
                )

                if _content:
                    if tool_name == "query_course_by_id":
                        course_info = JsonUtil.to_obj(_content, CourseInfo)
                        # to_obj 解析出 null 时返回 None，这里做兜底
                        if course_info is None:
                            logger.warning(
                                f"query_course_by_id 返回空数据，跳过。"
                                f"原始 _content={_content!r}"
                            )
                        elif getattr(course_info, "id", None) is None:
                            logger.warning(f"CourseInfo 缺少 id 字段: {course_info!r}")
                        else:
                            tool_result[f"courseInfo_{course_info.id}"] = course_info
                    elif tool_name == "pre_place_order":
                        order = JsonUtil.to_obj(_content, PrePlaceOrder)
                        # to_obj 解析出 null 时返回 None，这里做兜底
                        if order is None:
                            logger.warning(
                                f"pre_place_order 返回空数据，跳过。"
                                f"原始 _content={_content!r}"
                            )
                        else:
                            tool_result["prePlaceOrder"] = order
                else:
                    # content 为空时记录日志，避免问题被静默吞掉
                    logger.warning(f"工具 {tool_name} 的 content 为空，event={event!r}")

            # 如果 agent 返回 done=True，则结束流式输出
            if event["done"]:
                break

        # 定义元数据，将请求id和工具调用结果一起返回给客户端
        request_id = context.message.metadata.get("request_id", "")
        metadata = {"request_id": request_id}

        if tool_result:
            # 如果存在工具调用结果，则写入 metadata，随最终事件输出
            metadata["tool_result"] = tool_result

            # -----------------------------------------------
            # 推送任务最终状态（completed）
            # -----------------------------------------------

        status = TaskStatusUpdateEvent(
            context_id=context.context_id,
            task_id=context.task_id,
            status=TaskStatus(state=TaskState.completed),  # 标记任务已完成
            final=True,  # 表示最后一个事件
            metadata=metadata  # 附带元数据返回
        )
        await event_queue.enqueue_event(status)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        取消任务（当前不支持）。

        A2A 框架可能调用此接口取消任务，当前场景不支持，因此直接抛出异常。
        """
        raise Exception("cancel not supported")