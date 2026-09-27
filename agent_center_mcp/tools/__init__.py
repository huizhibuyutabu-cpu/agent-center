import pkgutil
import importlib

from mcp.server import FastMCP


def register_all_tools(mcp: FastMCP):
    """
    自动发现并注册当前包下所有模块中的工具

    :param mcp: FastMCP 实例，用于注册工具
    """
    # 获取当前包名（即此文件所在的包）
    package = __name__

    # 遍历当前包路径下的所有子模块
    # pkgutil.iter_modules 会返回 (module_finder, module_name, is_pkg)
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        # 动态导入子模块，例如：package.module_name
        module = importlib.import_module(f"{package}.{module_name}")

        # 如果模块中定义了 register 函数，则调用它进行注册
        if hasattr(module, "register"):
            module.register(mcp)