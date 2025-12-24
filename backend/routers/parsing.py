from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from backend.services.parsing_service import ParsingService
from backend.utils.storage import list_results, load_result

router = APIRouter()


class ParseRequest(BaseModel):
    file_id: str
    parse_type: str  # full_text, by_page, by_title, mixed


@router.post("/parse")
async def parse_document(request: ParseRequest):
    """解析文档"""
    try:
        if request.parse_type == "full_text":
            result = ParsingService.parse_full_text(request.file_id)
        elif request.parse_type == "by_page":
            result = ParsingService.parse_by_page(request.file_id)
        elif request.parse_type == "by_title":
            result = ParsingService.parse_by_title(request.file_id)
        elif request.parse_type == "mixed":
            result = ParsingService.parse_mixed_tables_text(request.file_id)
        else:
            raise ValueError(f"不支持的解析类型: {request.parse_type}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_parsing_history():
    """获取历史解析记录列表"""
    try:
        results = list_results("parsing")
        history = []

        for item in results:
            parse_id = item["file_id"]
            result_data = load_result("parsing", parse_id)

            if result_data:
                file_path = item["file_path"]
                file_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0

                history.append({
                    "parse_id": result_data.get("parse_id", parse_id),
                    "file_id": result_data.get("file_id", ""),
                    "parse_type": result_data.get("parse_type", ""),
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


@router.get("/history/{parse_id}")
async def get_parsing_detail(parse_id: str):
    """获取指定解析记录的详细信息"""
    try:
        result = load_result("parsing", parse_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到parse_id: {parse_id}的记录")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
