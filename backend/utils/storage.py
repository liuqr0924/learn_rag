import json
import os
from pathlib import Path
from backend.utils.config import DATA_DIR


def save_result(module_name: str, file_id: str, result: dict):
    """保存功能模块的处理结果到JSON文件"""
    module_dir = os.path.join(DATA_DIR, module_name)
    os.makedirs(module_dir, exist_ok=True)

    file_path = os.path.join(module_dir, f"{file_id}.json")
    
    # 使用临时文件先写入，确保原子性操作
    temp_path = f"{file_path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 写入成功后再重命名，确保文件完整性
        if os.path.exists(file_path):
            os.remove(file_path)
        os.rename(temp_path, file_path)
    except Exception as e:
        # 如果写入失败，删除临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise ValueError(f"保存文件失败: {file_path}\n错误信息: {str(e)}")

    return file_path


def load_result(module_name: str, file_id: str) -> dict:
    """从JSON文件加载功能模块的处理结果"""
    file_path = os.path.join(DATA_DIR, module_name, f"{file_id}.json")
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        # JSON 解析错误，可能是文件损坏
        raise ValueError(
            f"JSON文件解析失败: {file_path}\n"
            f"错误位置: 第 {e.lineno} 行，第 {e.colno} 列\n"
            f"错误信息: {str(e)}\n"
            f"文件可能已损坏，建议删除该文件后重新生成。"
        )
    except Exception as e:
        raise ValueError(f"加载文件失败: {file_path}\n错误信息: {str(e)}")


def list_results(module_name: str) -> list:
    """列出指定模块的所有结果文件"""
    module_dir = os.path.join(DATA_DIR, module_name)
    if not os.path.exists(module_dir):
        return []

    results = []
    for file in os.listdir(module_dir):
        if file.endswith(".json"):
            file_id = file.replace(".json", "")
            results.append({
                "file_id": file_id,
                "file_path": os.path.join(module_dir, file)
            })

    return results
