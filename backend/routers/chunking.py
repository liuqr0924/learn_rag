from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from backend.services.chunking_service import ChunkingService
from backend.utils.storage import list_results, load_result

router = APIRouter()


class ChunkRequest(BaseModel):
    file_id: str
    chunking_strategy: str = "by_size"  # by_size, by_sentence, by_paragraph
    chunk_size: int = 1000
    overlap: int = 200


@router.post("/chunk")
async def chunk_document(request: ChunkRequest):
    """对文档进行分块"""
    try:
        result = ChunkingService.chunk_document(
            file_id=request.file_id,
            chunking_strategy=request.chunking_strategy,
            chunk_size=request.chunk_size,
            overlap=request.overlap
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_chunking_history():
    """获取历史分块记录列表"""
    try:
        results = list_results("chunking")
        history = []

        for item in results:
            chunk_id = item["file_id"]
            result_data = load_result("chunking", chunk_id)

            if result_data:
                file_path = item["file_path"]
                file_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0

                history.append({
                    "chunk_id": result_data.get("chunk_id", chunk_id),
                    "file_id": result_data.get("file_id", ""),
                    "chunking_strategy": result_data.get("strategy", result_data.get("chunking_strategy", "")),
                    "total_chunks": result_data.get("total_chunks", 0),
                    "created_at": file_mtime,
                    "status": result_data.get("status", "unknown")
                })

        history.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "total": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{chunk_id}")
async def get_chunking_detail(chunk_id: str):
    """获取指定分块记录的详细信息"""
    try:
        result = load_result("chunking", chunk_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到chunk_id: {chunk_id}的记录")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
