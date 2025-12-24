import os
import uuid
from typing import List, Dict, Optional
import fitz  # PyMuPDF
from pypdf import PdfReader
from unstructured.partition.auto import partition
from backend.utils.storage import save_result


class LoadingService:
    """文档加载服务，支持PyMuPDF、PyPDF和Unstructured"""

    @staticmethod
    def load_with_pymupdf(file_path: str) -> Dict:
        """使用PyMuPDF加载PDF文档"""
        doc = fitz.open(file_path)
        pages = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "metadata": {
                    "width": page.rect.width,
                    "height": page.rect.height
                }
            })
        doc.close()
        return {
            "method": "pymupdf",
            "total_pages": len(pages),
            "pages": pages
        }

    @staticmethod
    def load_with_pypdf(file_path: str) -> Dict:
        """使用PyPDF加载PDF文档"""
        reader = PdfReader(file_path)
        pages = []
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "metadata": {
                    "media_box": page.mediabox if hasattr(page, 'mediabox') else None
                }
            })
        return {
            "method": "pypdf",
            "total_pages": len(pages),
            "pages": pages
        }

    @staticmethod
    def load_with_unstructured(file_path: str) -> Dict:
        """使用Unstructured加载文档"""
        elements = partition(filename=file_path)
        chunks = []
        for elem in elements:
            chunks.append({
                "type": elem.category if hasattr(elem, 'category') else "unknown",
                "text": str(elem),
                "metadata": elem.metadata.to_dict() if hasattr(elem, 'metadata') else {}
            })
        return {
            "method": "unstructured",
            "total_chunks": len(chunks),
            "chunks": chunks
        }

    @staticmethod
    def load_file(file_path: str, method: str = "pymupdf") -> Dict:
        """加载文件
        
        Args:
            file_path: 文件路径
            method: 加载方法 (pymupdf, pypdf, unstructured)
        
        Returns:
            包含加载结果的字典
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_id = str(uuid.uuid4())
        file_name = os.path.basename(file_path)

        if method == "pymupdf":
            result = LoadingService.load_with_pymupdf(file_path)
        elif method == "pypdf":
            result = LoadingService.load_with_pypdf(file_path)
        elif method == "unstructured":
            result = LoadingService.load_with_unstructured(file_path)
        else:
            raise ValueError(f"不支持的加载方法: {method}")

        # 保存结果
        result_data = {
            "file_id": file_id,
            "file_name": file_name,
            "file_path": file_path,
            "loading_method": method,
            "result": result
        }

        save_result("loading", file_id, result_data)

        return {
            "file_id": file_id,
            "file_name": file_name,
            "method": method,
            "status": "success",
            "result": result
        }
