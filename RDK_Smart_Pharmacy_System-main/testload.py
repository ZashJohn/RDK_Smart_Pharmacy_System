import json
import ast

def load_and_parse_results():
    """从 global_results.txt 加载并解析为 Python 列表"""
    try:
        with open("global_results.txt", "r", encoding="utf-8") as f:
            content = f.read().strip()  # 读取并去除首尾空格
            data = ast.literal_eval(content)  # 安全解析 Python 字面量
            return data
    except FileNotFoundError:
        print("错误：未找到 global_results.txt 文件")
        return None
    except (SyntaxError, ValueError) as e:
        print(f"错误：文件内容解析失败 - {e}")
        return None

global_results = load_and_parse_results()  # 初始化为None，后续由load_medicine()填充
print(global_results[1])