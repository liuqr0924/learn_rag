from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
from pathlib import Path
from backend.services.loading_service import LoadingService
from backend.utils.storage import list_results, load_result

router = APIRouter()


def get_default_method_by_extension(filename: str) -> str:
    """根据文件扩展名自动选择默认的加载方法"""
    if not filename:
        return "unstructured"

    ext = os.path.splitext(filename)[1].lower()

    # PDF文件默认使用pymupdf（也可以手动指定pypdf）
    if ext == ".pdf":
        return "pymupdf"
    # 其他格式（docx, doc, txt, html, pptx, xlsx等）使用unstructured
    else:
        return "unstructured"


class LoadFileRequest(BaseModel):
    file_path: Optional[str] = None
    method: str = "pymupdf"  # pymupdf, pypdf, unstructured


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), method: Optional[str] = None):
    """上传并加载文件
    
    Args:
        file: 上传的文件
        method: 加载方法，可选。如果不指定，会根据文件扩展名自动选择：
            - PDF文件 -> "pymupdf"（默认）
            - DOCX/DOC/TXT/HTML/PPTX/XLSX等 -> "unstructured"（默认）
    """
    try:
        # 如果没有指定method，根据文件扩展名自动选择
        if method is None:
            method = get_default_method_by_extension(file.filename)

        # 创建上传文件保存目录
        backend_dir = Path(__file__).parent.parent
        upload_dir = os.path.join(str(backend_dir), "data", "upload")
        os.makedirs(upload_dir, exist_ok=True)

        # 生成唯一文件名：UUID + 原文件扩展名
        file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
        file_id = str(uuid.uuid4())
        saved_filename = f"{file_id}{file_ext}"
        file_path = os.path.join(upload_dir, saved_filename)

        # 保存上传的文件到项目目录
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 加载文件
        result = LoadingService.load_file(str(file_path), method)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load")
async def load_file(request: LoadFileRequest):
    """加载指定路径的文件"""
    try:
        if not request.file_path:
            raise ValueError("file_path不能为空")
        result = LoadingService.load_file(request.file_path, request.method)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_loading_history():
    """获取历史加载记录列表"""
    try:
        results = list_results("loading")
        history = []

        for item in results:
            file_id = item["file_id"]
            result_data = load_result("loading", file_id)

            if result_data:
                # 获取文件修改时间
                file_path = item["file_path"]
                file_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0

                history.append({
                    "file_id": file_id,
                    "file_name": result_data.get("file_name", ""),
                    "file_path": result_data.get("file_path", ""),
                    "loading_method": result_data.get("loading_method", ""),
                    "total_pages": result_data.get("result", {}).get("total_pages", 0),
                    "total_chunks": result_data.get("result", {}).get("total_chunks", 0),
                    "created_at": file_mtime,
                    "status": result_data.get("status", "unknown")
                })

        # 按创建时间倒序排列（最新的在前）
        history.sort(key=lambda x: x["created_at"], reverse=True)

        return {
            "total": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{file_id}")
async def get_loading_detail(file_id: str):
    """获取指定加载记录的详细信息"""
    try:
        result = load_result("loading", file_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到file_id: {file_id}的记录")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
