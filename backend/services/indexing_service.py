import uuid
import chromadb
from typing import List, Dict, Optional
from chromadb.config import Settings
from backend.utils.config import CHROMA_DB_PATH
from backend.utils.storage import load_result, save_result


class IndexingService:
    """向量索引服务，使用Chroma数据库"""

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )

    def create_collection(self, collection_name: str, embedding_dim: int = 768) -> Dict:
        """创建或获取集合"""
        try:
            collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"embedding_dim": embedding_dim}
            )
            return {
                "collection_name": collection_name,
                "status": "success",
                "count": collection.count()
            }
        except Exception as e:
            raise ValueError(f"创建集合失败: {str(e)}")

    def index_embeddings(self, embedding_id: str, collection_name: str) -> Dict:
        """将嵌入向量索引到Chroma数据库
        
        Args:
            embedding_id: 嵌入阶段生成的embedding_id
            collection_name: Chroma集合名称
        
        Returns:
            包含索引结果的字典
        """
        # 从嵌入结果中获取数据
        embedding_result = load_result("embedding", embedding_id)
        if not embedding_result:
            raise ValueError(f"未找到embedding_id: {embedding_id} 的嵌入结果")

        embedded_chunks = embedding_result["embedded_chunks"]

        # 获取或创建集合
        collection = self.client.get_or_create_collection(name=collection_name)

        # 准备数据
        ids = [f"chunk_{chunk['chunk_id']}" for chunk in embedded_chunks]
        embeddings = [chunk["embedding"] for chunk in embedded_chunks]
        documents = [chunk["text"] for chunk in embedded_chunks]
        metadatas = [
            {
                "chunk_id": str(chunk["chunk_id"]),
                "file_id": embedding_result["file_id"],
                "start": str(chunk["metadata"].get("start", "")),
                "end": str(chunk["metadata"].get("end", "")),
                "length": str(chunk["metadata"].get("length", ""))
            }
            for chunk in embedded_chunks
        ]

        # 添加到集合
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        # 保存索引信息
        index_id = str(uuid.uuid4())
        result_data = {
            "index_id": index_id,
            "embedding_id": embedding_id,
            "file_id": embedding_result["file_id"],
            "collection_name": collection_name,
            "total_documents": len(ids),
            "status": "indexed"
        }

        save_result("indexing", index_id, result_data)

        return {
            "index_id": index_id,
            "collection_name": collection_name,
            "status": "success",
            "total_documents": len(ids)
        }

    def similarity_search(self, collection_name: str, query_text: str,
                          query_embedding: List[float], n_results: int = 5) -> Dict:
        """相似度搜索
        
        Args:
            collection_name: 集合名称
            query_text: 查询文本
            query_embedding: 查询文本的嵌入向量
            n_results: 返回结果数量
        
        Returns:
            搜索结果
        """
        collection = self.client.get_collection(name=collection_name)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        # 格式化结果
        search_results = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i in range(len(results["ids"][0])):
                search_results.append({
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                    "metadata": results["metadatas"][0][i] if "metadatas" in results else {}
                })

        return {
            "query_text": query_text,
            "collection_name": collection_name,
            "results_count": len(search_results),
            "results": search_results
        }

    def list_collections(self) -> Dict:
        """列出所有集合"""
        collections = self.client.list_collections()
        collection_list = [
            {
                "name": col.name,
                "count": col.count(),
                "metadata": col.metadata
            }
            for col in collections
        ]
        return {
            "collections": collection_list,
            "total": len(collection_list)
        }

    def delete_collection(self, collection_name: str) -> Dict:
        """删除集合"""
        try:
            self.client.delete_collection(name=collection_name)
            return {
                "collection_name": collection_name,
                "status": "deleted"
            }
        except Exception as e:
            raise ValueError(f"删除集合失败: {str(e)}")
