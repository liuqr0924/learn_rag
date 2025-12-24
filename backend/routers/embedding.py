from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from backend.services.embedding_service import EmbeddingService
from backend.utils.storage import list_results, load_result

router = APIRouter()
embedding_service = EmbeddingService()


class EmbedRequest(BaseModel):
    chunk_id: str


@router.post("/embed")
async def embed_chunks(request: EmbedRequest):
    """创建嵌入向量（使用配置的本地模型）
    
    Args:
        chunk_id: 分块ID
    """
    try:
        result = embedding_service.embed_chunks(request.chunk_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_embedding_history():
    """获取历史嵌入记录列表"""
    try:
        results = list_results("embedding")
        history = []
        errors = []

        for item in results:
            embedding_id = item["file_id"]
            try:
                result_data = load_result("embedding", embedding_id)

                if result_data:
                    file_path = item["file_path"]
                    file_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0

                    history.append({
                        "embedding_id": result_data.get("embedding_id", embedding_id),
                        "chunk_id": result_data.get("chunk_id", ""),
                        "model": result_data.get("embedding_model", result_data.get("model", "")),
                        "embedding_dim": result_data.get("embedding_dim", 0),
                        "total_embeddings": result_data.get("total_embeddings", result_data.get("total_chunks", 0)),
                        "created_at": file_mtime,
                        "status": result_data.get("status", "unknown")
                    })
            except Exception as e:
                # 跳过损坏的文件，记录错误但不中断整个流程
                errors.append(f"跳过损坏的文件 {embedding_id}: {str(e)}")
                continue

        history.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "total": len(history),
            "history": history,
            "errors": errors if errors else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{embedding_id}")
async def get_embedding_detail(embedding_id: str):
    """获取指定嵌入记录的详细信息"""
    try:
        result = load_result("embedding", embedding_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到embedding_id: {embedding_id}的记录")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
