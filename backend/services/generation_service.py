import uuid
from typing import List, Dict, Optional
from openai import AzureOpenAI
from backend.utils.config import (
    AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION, AZURE_OPENAI_CHAT_DEPLOYMENT
)
from backend.utils.storage import save_result, load_result


class GenerationService:
    """文本生成服务，使用Azure OpenAI"""

    def __init__(self):
        self.client = None
        if AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT:
            self.client = AzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                api_version=AZURE_OPENAI_API_VERSION,
                azure_endpoint=AZURE_OPENAI_ENDPOINT
            )

    def generate_with_context(self, query: str, context_documents: List[str],
                              max_tokens: int = 500) -> Dict:
        """基于上下文生成文本
        
        Args:
            query: 用户查询
            context_documents: 上下文文档列表
            max_tokens: 最大生成token数
        
        Returns:
            生成结果
        """
        if not self.client:
            raise ValueError("Azure OpenAI未配置，请检查环境变量")

        # 构建上下文
        context = "\n\n".join([f"[文档{i + 1}]: {doc}" for i, doc in enumerate(context_documents)])

        # 构建提示词
        system_prompt = "你是一个有用的助手，基于提供的文档上下文回答问题。如果上下文中没有相关信息，请说明。"
        user_prompt = f"上下文：\n{context}\n\n问题：{query}\n\n请基于上下文回答："

        # 调用Azure OpenAI
        response = self.client.chat.completions.create(
            model=AZURE_OPENAI_CHAT_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )

        generated_text = response.choices[0].message.content

        # 保存结果
        generation_id = str(uuid.uuid4())
        result_data = {
            "generation_id": generation_id,
            "query": query,
            "context_count": len(context_documents),
            "generated_text": generated_text,
            "model": AZURE_OPENAI_CHAT_DEPLOYMENT,
            "max_tokens": max_tokens,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }

        save_result("generation", generation_id, result_data)

        return {
            "generation_id": generation_id,
            "status": "success",
            "query": query,
            "generated_text": generated_text,
            "model": AZURE_OPENAI_CHAT_DEPLOYMENT
        }

    def generate_from_filtered_results(self, filter_id: str, query: str,
                                       max_context_docs: int = 5,
                                       max_tokens: int = 500) -> Dict:
        """基于过滤后的搜索结果生成文本
        
        Args:
            filter_id: 过滤结果ID
            query: 用户查询
            max_context_docs: 最多使用的上下文文档数
            max_tokens: 最大生成token数
        
        Returns:
            生成结果
        """
        # 加载过滤结果
        filtering_result = load_result("filtering", filter_id)
        if not filtering_result:
            raise ValueError(f"未找到filter_id: {filter_id} 的过滤结果")

        # 提取文档
        filtered_results = filtering_result.get("filtered_results", [])
        context_documents = [
            result.get("document", "")
            for result in filtered_results[:max_context_docs]
            if result.get("document")
        ]

        return self.generate_with_context(query, context_documents, max_tokens)
