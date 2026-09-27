import orjson
from dataclasses import is_dataclass, asdict, dataclass
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Type, TypeVar

T = TypeVar("T")


class JsonUtil:

    @staticmethod
    def to_str(data: Any) -> str:
        """
        将 Python 对象序列化为 JSON 字符串。
        支持 dataclass、datetime、date、Decimal。
        """

        def default(obj):
            if is_dataclass(obj):
                return asdict(obj)  # 将 dataclass 转为 dict
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()  # datetime/date 转 ISO 格式字符串
            if isinstance(obj, Decimal):
                return float(obj)  # Decimal 转 float
            raise TypeError(f"对象类型 {type(obj)} 不可序列化")

        return orjson.dumps(data, default=default).decode("utf-8")

    @staticmethod
    def to_obj(json_str: str, cls: Type[T] = None) -> Any:
        """
        将 JSON 字符串反序列化为 Python 对象。
        如果 cls 是 dataclass，则返回 dataclass 实例。
        否则返回 dict/list 等原生类型。
        解析结果为 null 时返回 None。
        """
        # 输入本身为 None，直接返回
        if json_str is None:
            return None

        obj = orjson.loads(json_str)

        if cls and is_dataclass(cls):
            # 解析出来是 null → 返回 None，不构建 dataclass
            if obj is None:
                return None
            # 解析出来不是 dict → 抛出明确错误，而不是让 cls(**obj) 直接炸
            if not isinstance(obj, dict):
                raise ValueError(
                    f"to_obj 无法用 {cls.__name__} 构建非 dict 对象: "
                    f"type={type(obj).__name__}, value={obj!r}"
                )
            try:
                return cls(**obj)
            except TypeError as e:
                # 字段不匹配时给出更清楚的错误信息
                raise ValueError(
                    f"无法构建 {cls.__name__}，字段不匹配: {e}"
                ) from e

        return obj