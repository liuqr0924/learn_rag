from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from backend.services.generation_service import GenerationService
from backend.utils.storage import list_results, load_result

router = APIRouter()
generation_service = GenerationService()


class GenerateRequest(BaseModel):
    query: str
    context_documents: Optional[List[str]] = None
    filter_id: Optional[str] = None
    max_context_docs: int = 5
    max_tokens: int = 500


@router.post("/generate")
async def generate_text(request: GenerateRequest):
    """生成文本"""
    try:
        if request.filter_id:
            # 从过滤结果生成
            result = generation_service.generate_from_filtered_results(
                request.filter_id,
                request.query,
                request.max_context_docs,
                request.max_tokens
            )
        elif request.context_documents:
            # 从提供的上下文生成
            result = generation_service.generate_with_context(
                request.query,
                request.context_documents,
                request.max_tokens
            )
        else:
            raise ValueError("必须提供context_documents或filter_id")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_generation_history():
    """获取历史生成记录列表"""
    try:
        results = list_results("generation")
        history = []

        for item in results:
            generation_id = item["file_id"]
            result_data = load_result("generation", generation_id)

            if result_data:
                file_path = item["file_path"]
                file_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0

                history.append({
                    "generation_id": result_data.get("generation_id", generation_id),
                    "query": result_data.get("query", ""),
                    "filter_id": result_data.get("filter_id", ""),
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


@router.get("/history/{generation_id}")
async def get_generation_detail(generation_id: str):
    """获取指定生成记录的详细信息"""
    try:
        result = load_result("generation", generation_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到generation_id: {generation_id}的记录")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
