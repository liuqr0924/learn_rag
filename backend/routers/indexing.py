import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.embedding_service import EmbeddingService
from backend.services.indexing_service import IndexingService
from backend.utils.storage import list_results, load_result

router = APIRouter()
indexing_service = IndexingService()
embedding_service = EmbeddingService()


class IndexRequest(BaseModel):
    embedding_id: str
    collection_name: str


class SearchRequest(BaseModel):
    collection_name: str
    query_text: str
    n_results: int = 5


@router.post("/create-collection")
async def create_collection(collection_name: str, embedding_dim: int = 768):
    """创建集合"""
    try:
        result = indexing_service.create_collection(collection_name, embedding_dim)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index")
async def index_embeddings(request: IndexRequest):
    """索引嵌入向量"""
    try:
        result = indexing_service.index_embeddings(request.embedding_id, request.collection_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def similarity_search(request: SearchRequest):
    """相似度搜索"""
    try:
        # 先创建查询文本的嵌入向量（使用默认模型）
        query_embedding = embedding_service.create_embeddings([request.query_text])[0]
        result = indexing_service.similarity_search(
            request.collection_name,
            request.query_text,
            query_embedding,
            request.n_results
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections")
async def list_collections():
    """列出所有集合"""
    try:
        result = indexing_service.list_collections()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/collection/{collection_name}")
async def delete_collection(collection_name: str):
    """删除集合"""
    try:
        result = indexing_service.delete_collection(collection_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_indexing_history():
    """获取历史索引记录列表"""
    try:
        results = list_results("indexing")
        history = []

        for item in results:
            index_id = item["file_id"]
            result_data = load_result("indexing", index_id)

            if result_data:
                file_path = item["file_path"]
                file_mtime = os.path.getmtime(file_path) if os.path.exists(file_path) else 0

                history.append({
                    "index_id": result_data.get("index_id", index_id),
                    "embedding_id": result_data.get("embedding_id", ""),
                    "collection_name": result_data.get("collection_name", ""),
                    "total_documents": result_data.get("total_documents", 0),
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


@router.get("/history/{index_id}")
async def get_indexing_detail(index_id: str):
    """获取指定索引记录的详细信息"""
    try:
        result = load_result("indexing", index_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到index_id: {index_id}的记录")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
