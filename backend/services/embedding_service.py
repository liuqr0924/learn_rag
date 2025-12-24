import uuid
from typing import List, Dict

from openai import AzureOpenAI
# 导入本地embedding库
from sentence_transformers import SentenceTransformer

from backend.utils.config import (
    AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    LOCAL_EMBEDDING_MODEL
)
from backend.utils.storage import save_result, load_result


class EmbeddingService:
    _instance = None
    _initialized = False

    def __new__(cls):
        """单例模式：确保整个应用只有一个实例"""
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 如果已经初始化过，直接返回
        if EmbeddingService._initialized:
            return
        
        EmbeddingService._initialized = True
        self.client = None
        self.local_model = None
        

        try:
            local_model_name = LOCAL_EMBEDDING_MODEL
            self.local_model = SentenceTransformer(local_model_name)
            print(f"✓ 已加载本地embedding模型: {local_model_name}")
        except Exception as e:
            print(f"警告: 本地embedding模型加载失败: {e}")
            self.local_model = None
            print("错误: 已启用本地模型但加载失败，请检查sentence-transformers是否正确安装")
        
        # 初始化Azure OpenAI客户端（作为备选）
        if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
            try:
                self.client = AzureOpenAI(
                    api_key=AZURE_OPENAI_API_KEY,
                    api_version=AZURE_OPENAI_API_VERSION,
                    azure_endpoint=AZURE_OPENAI_ENDPOINT
                )
            except Exception as e:
                print(f"警告: Azure OpenAI客户端初始化失败: {e}")

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """创建文本嵌入向量（批量处理）
        
        Args:
            texts: 文本列表
        
        Returns:
            嵌入向量列表
        """
        if not texts:
            return []

        # 使用本地模型
        if not self.local_model:
            raise ValueError(
                "本地embedding模型未加载。请检查：\n"
                "1. 是否已安装sentence-transformers: pip install sentence-transformers\n"
                "2. 模型名称是否正确（当前配置: {})\n"
                "3. 网络连接是否正常（首次使用需要从Hugging Face下载模型）".format(LOCAL_EMBEDDING_MODEL)
            )

        try:
            # 使用 convert_to_numpy=True 确保返回 numpy 数组，然后转换为列表
            """
                这里的 local_model 是一个 SentenceTransformer 实例。
                encode 方法将文本转换为固定长度的向量，用于后续的相似度计算和检索，返回的向量用于构建向量数据库中的索引。
            """
            embeddings = self.local_model.encode(texts, convert_to_numpy=True)
            # 转换为 Python 列表（支持 JSON 序列化）
            if hasattr(embeddings, 'tolist'):
                return embeddings.tolist()
            # 如果是列表，直接返回
            return list(embeddings) if not isinstance(embeddings, list) else embeddings
        except Exception as e:
            raise ValueError(f"本地模型生成embedding失败: {str(e)}")

    def embed_chunks(self, chunk_id: str) -> Dict:
        """对分块后的文档创建嵌入向量
        
        Args:
            chunk_id: 分块阶段生成的chunk_id
        
        Returns:
            包含嵌入结果的字典
        """
        # 清理 chunk_id，去除首尾空白字符（包括制表符、换行符等）
        chunk_id = chunk_id.strip() if chunk_id else chunk_id
        
        # 从分块结果中获取chunks
        chunking_result = load_result("chunking", chunk_id)
        if not chunking_result:
            # 提供更详细的错误信息，包括可用的 chunk_id 列表
            from backend.utils.storage import list_results
            available_chunks = list_results("chunking")
            available_ids = [item["file_id"] for item in available_chunks]
            raise ValueError(
                f"未找到chunk_id: '{chunk_id}' 的分块结果。\n"
                f"可用的chunk_id列表: {available_ids}"
            )

        chunks = chunking_result["chunks"]
        texts = [chunk["text"] for chunk in chunks]

        # 创建嵌入向量
        embeddings = self.create_embeddings(texts)
        
        # 确定实际使用的模型名称
        if not self.local_model:
            raise ValueError("本地embedding模型未加载")
        
        model_name = LOCAL_EMBEDDING_MODEL
        dim = self.local_model.get_sentence_embedding_dimension() if hasattr(self.local_model, 'get_sentence_embedding_dimension') else len(embeddings[0]) if embeddings else 'unknown'
        actual_model = f"local:{model_name.split('/')[-1]}({dim}维)"

        # 准备结果数据
        embedded_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            embedded_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "embedding": embedding,
                "embedding_dim": len(embedding),
                "metadata": {
                    "start": chunk.get("start"),
                    "end": chunk.get("end"),
                    "length": chunk.get("length")
                }
            })

        # 保存结果
        embedding_id = str(uuid.uuid4())
        result_data = {
            "embedding_id": embedding_id,
            "chunk_id": chunk_id,
            "file_id": chunking_result["file_id"],
            "embedding_model": actual_model,
            "total_chunks": len(embedded_chunks),
            "embedding_dim": len(embeddings[0]) if embeddings else 0,
            "embedded_chunks": embedded_chunks
        }

        save_result("embedding", embedding_id, result_data)

        # 准备预览数据（不包含embedding向量）
        preview_chunks = []
        for chunk in embedded_chunks[:3]:
            preview_chunks.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
                "embedding_dim": chunk["embedding_dim"],
                "metadata": chunk["metadata"]
            })

        return {
            "embedding_id": embedding_id,
            "chunk_id": chunk_id,
            "status": "success",
            "total_chunks": len(embedded_chunks),
            "embedding_dim": len(embeddings[0]) if embeddings else 0,
            "model": actual_model,
            "preview": preview_chunks
        }
