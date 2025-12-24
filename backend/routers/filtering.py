from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from backend.services.filtering_service import FilteringService
from backend.utils.storage import list_results, load_result

router = APIRouter()

class FilterRequest(BaseModel):
    search_results: dict  # 搜索结果
    min_score: float = 0.0
    max_score: float = 1.0
    sort_order: str = "desc"  # asc, desc

@router.post("/filter")
async def filter_and_sort(request: FilterRequest):
    """过滤和排序搜索结果"""
    try:
        result = FilteringService.filter_and_sort(
            request.search_results,
            request.min_score,
            request.max_score,
            request.sort_order
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_filtering_history():
    """获取历史过滤记录列表"""
    try:
        results = list_results("filtering")
        history = []
        
        for item in results:
            filter_id = item["file_id"]
            result_data = load_result("filtering", filter_id)
            
            if result_data:
                file_path = item["file_path"]
                file_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0
                
                history.append({
                    "filter_id": result_data.get("filter_id", filter_id),
                    "total_results": result_data.get("total_results", 0),
                    "filtered_count": result_data.get("filtered_count", 0),
                    "min_score": result_data.get("min_score", 0),
                    "max_score": result_data.get("max_score", 1),
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

@router.get("/history/{filter_id}")
async def get_filtering_detail(filter_id: str):
    """获取指定过滤记录的详细信息"""
    try:
        result = load_result("filtering", filter_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到filter_id: {filter_id}的记录")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

