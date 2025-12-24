import uuid
from typing import List, Dict, Optional
from backend.utils.storage import save_result, load_result


class ParsingService:
    """文档解析服务，支持全文、分页、按标题等解析方式"""

    @staticmethod
    def parse_full_text(file_id: str) -> Dict:
        """全文解析"""
        loading_result = load_result("loading", file_id)
        if not loading_result:
            raise ValueError(f"未找到文件ID: {file_id} 的加载结果")

        full_text = ""
        if loading_result["result"]["method"] in ["pymupdf", "pypdf"]:
            for page in loading_result["result"]["pages"]:
                full_text += page["text"] + "\n"
        elif loading_result["result"]["method"] == "unstructured":
            for chunk in loading_result["result"]["chunks"]:
                full_text += chunk["text"] + "\n"

        parse_id = str(uuid.uuid4())
        result_data = {
            "parse_id": parse_id,
            "file_id": file_id,
            "parse_type": "full_text",
            "full_text": full_text,
            "length": len(full_text)
        }

        save_result("parsing", parse_id, result_data)

        return {
            "parse_id": parse_id,
            "parse_type": "full_text",
            "status": "success",
            "preview": full_text[:500] + "..." if len(full_text) > 500 else full_text
        }

    @staticmethod
    def parse_by_page(file_id: str) -> Dict:
        """按页解析"""
        loading_result = load_result("loading", file_id)
        if not loading_result:
            raise ValueError(f"未找到文件ID: {file_id} 的加载结果")

        if loading_result["result"]["method"] not in ["pymupdf", "pypdf"]:
            raise ValueError("按页解析仅支持PDF文档")

        pages = []
        for page_data in loading_result["result"]["pages"]:
            pages.append({
                "page_number": page_data["page_number"],
                "text": page_data["text"],
                "metadata": page_data.get("metadata", {})
            })

        parse_id = str(uuid.uuid4())
        result_data = {
            "parse_id": parse_id,
            "file_id": file_id,
            "parse_type": "by_page",
            "total_pages": len(pages),
            "pages": pages
        }

        save_result("parsing", parse_id, result_data)

        return {
            "parse_id": parse_id,
            "parse_type": "by_page",
            "status": "success",
            "total_pages": len(pages),
            "pages_preview": pages[:3]  # 预览前3页
        }

    @staticmethod
    def parse_by_title(file_id: str) -> Dict:
        """按标题解析（简单实现，可根据需要扩展）"""
        loading_result = load_result("loading", file_id)
        if not loading_result:
            raise ValueError(f"未找到文件ID: {file_id} 的加载结果")

        # 提取文本
        text = ""
        if loading_result["result"]["method"] in ["pymupdf", "pypdf"]:
            for page in loading_result["result"]["pages"]:
                text += page["text"] + "\n"
        elif loading_result["result"]["method"] == "unstructured":
            for chunk in loading_result["result"]["chunks"]:
                text += chunk["text"] + "\n"

        # 简单的标题识别（根据行首的特殊格式）
        import re
        lines = text.split('\n')
        sections = []
        current_title = "前言"
        current_content = []

        for line in lines:
            # 识别标题（行首可能是数字、中文编号等）
            if re.match(r'^[\d一二三四五六七八九十]+[、\.]\s*', line) or \
                    re.match(r'^第[一二三四五六七八九十\d]+[章节部分]\s*', line) or \
                    len(line) < 50 and line.strip():
                if current_content:
                    sections.append({
                        "title": current_title,
                        "content": "\n".join(current_content)
                    })
                current_title = line.strip()
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections.append({
                "title": current_title,
                "content": "\n".join(current_content)
            })

        parse_id = str(uuid.uuid4())
        result_data = {
            "parse_id": parse_id,
            "file_id": file_id,
            "parse_type": "by_title",
            "total_sections": len(sections),
            "sections": sections
        }

        save_result("parsing", parse_id, result_data)

        return {
            "parse_id": parse_id,
            "parse_type": "by_title",
            "status": "success",
            "total_sections": len(sections),
            "sections_preview": sections[:5]  # 预览前5个章节
        }

    @staticmethod
    def parse_mixed_tables_text(file_id: str) -> Dict:
        """混合解析（表格和文本）"""
        loading_result = load_result("loading", file_id)
        if not loading_result:
            raise ValueError(f"未找到文件ID: {file_id} 的加载结果")

        # 使用unstructured的方法，它可以更好地识别表格
        if loading_result["result"]["method"] == "unstructured":
            elements = loading_result["result"]["chunks"]
            tables = []
            texts = []

            for elem in elements:
                if elem.get("type") == "Table":
                    tables.append(elem)
                else:
                    texts.append(elem)

            parse_id = str(uuid.uuid4())
            result_data = {
                "parse_id": parse_id,
                "file_id": file_id,
                "parse_type": "mixed",
                "tables_count": len(tables),
                "text_chunks_count": len(texts),
                "tables": tables,
                "texts": texts
            }
        else:
            # 对于PDF，简单处理
            parse_id = str(uuid.uuid4())
            result_data = {
                "parse_id": parse_id,
                "file_id": file_id,
                "parse_type": "mixed",
                "tables_count": 0,
                "text_chunks_count": 1,
                "tables": [],
                "texts": [{"text": "PDF文档，表格提取需要使用专门的工具"}]
            }

        save_result("parsing", parse_id, result_data)

        return {
            "parse_id": parse_id,
            "parse_type": "mixed",
            "status": "success",
            "tables_count": result_data["tables_count"],
            "text_chunks_count": result_data["text_chunks_count"]
        }
