import uuid
from typing import List, Dict, Optional
from backend.utils.storage import save_result, load_result


class ChunkingService:
    """文档分块服务，支持多种分块策略"""

    @staticmethod
    def chunk_by_size(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
        """按固定大小分块"""
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text,
                "start": start,
                "end": min(end, len(text)),
                "length": len(chunk_text)
            })

            chunk_id += 1
            start = end - overlap

            if start >= len(text):
                break

        return chunks

    @staticmethod
    def chunk_by_sentence(text: str, max_chunk_size: int = 1000) -> List[Dict]:
        """按句子分块"""
        import re
        sentences = re.split(r'[.!?。！？]\s+', text)
        chunks = []
        current_chunk = ""
        chunk_id = 0
        start_pos = 0

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += sentence + "。"
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "text": current_chunk.strip(),
                        "start": start_pos,
                        "end": start_pos + len(current_chunk),
                        "length": len(current_chunk)
                    })
                    chunk_id += 1
                    start_pos += len(current_chunk)
                current_chunk = sentence + "。"

        if current_chunk:
            chunks.append({
                "chunk_id": chunk_id,
                "text": current_chunk.strip(),
                "start": start_pos,
                "end": start_pos + len(current_chunk),
                "length": len(current_chunk)
            })

        return chunks

    @staticmethod
    def chunk_by_paragraph(text: str) -> List[Dict]:
        """按段落分块"""
        paragraphs = text.split('\n\n')
        chunks = []
        start_pos = 0

        for chunk_id, para in enumerate(paragraphs):
            if para.strip():
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": para.strip(),
                    "start": start_pos,
                    "end": start_pos + len(para),
                    "length": len(para)
                })
                start_pos += len(para) + 2  # +2 for \n\n

        return chunks

    @staticmethod
    def chunk_document(file_id: str, chunking_strategy: str = "by_size",
                       chunk_size: int = 1000, overlap: int = 200) -> Dict:
        """对文档进行分块
        
        Args:
            file_id: 加载阶段生成的文件ID
            chunking_strategy: 分块策略 (by_size, by_sentence, by_paragraph)
            chunk_size: 分块大小（用于by_size策略）
            overlap: 重叠大小（用于by_size策略）
        
        Returns:
            包含分块结果的字典
        """
        # 从加载结果中获取文档内容
        loading_result = load_result("loading", file_id)
        if not loading_result:
            raise ValueError(f"未找到文件ID: {file_id} 的加载结果")

        # 提取文本内容
        text_content = ""
        if loading_result["result"]["method"] in ["pymupdf", "pypdf"]:
            # 合并所有页面的文本
            for page in loading_result["result"]["pages"]:
                text_content += page["text"] + "\n"
        elif loading_result["result"]["method"] == "unstructured":
            # 合并所有chunks的文本
            for chunk in loading_result["result"]["chunks"]:
                text_content += chunk["text"] + "\n"

        # 根据策略进行分块
        if chunking_strategy == "by_size":
            chunks = ChunkingService.chunk_by_size(text_content, chunk_size, overlap)
        elif chunking_strategy == "by_sentence":
            chunks = ChunkingService.chunk_by_sentence(text_content, chunk_size)
        elif chunking_strategy == "by_paragraph":
            chunks = ChunkingService.chunk_by_paragraph(text_content)
        else:
            raise ValueError(f"不支持的分块策略: {chunking_strategy}")

        # 保存结果
        chunk_id = str(uuid.uuid4())
        result_data = {
            "chunk_id": chunk_id,
            "file_id": file_id,
            "original_file": loading_result["file_name"],
            "chunking_strategy": chunking_strategy,
            "total_chunks": len(chunks),
            "chunks": chunks,
            "parameters": {
                "chunk_size": chunk_size,
                "overlap": overlap
            }
        }

        save_result("chunking", chunk_id, result_data)

        return {
            "chunk_id": chunk_id,
            "file_id": file_id,
            "strategy": chunking_strategy,
            "total_chunks": len(chunks),
            "status": "success",
            "chunks": chunks[:10]  # 只返回前10个chunks作为预览
        }
