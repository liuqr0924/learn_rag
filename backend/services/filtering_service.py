import uuid
import json
from typing import List, Dict, Optional
from backend.utils.storage import save_result


class FilteringService:
    """结果过滤和排序服务"""

    @staticmethod
    def filter_by_score(results: List[Dict], min_score: float = 0.0, max_score: float = 1.0) -> List[Dict]:
        """根据分数过滤结果"""
        filtered = []
        for result in results:
            # distance越小，相似度越高，所以需要转换
            if "distance" in result and result["distance"] is not None:
                score = 1.0 - result["distance"]  # 转换为相似度分数
                if min_score <= score <= max_score:
                    filtered.append(result)
            else:
                # 如果没有distance，默认保留
                filtered.append(result)
        return filtered

    @staticmethod
    def sort_by_score(results: List[Dict], ascending: bool = False) -> List[Dict]:
        """根据分数排序（默认降序，相似度高的在前）"""
        # 添加score字段
        for result in results:
            if "distance" in result and result["distance"] is not None:
                result["score"] = 1.0 - result["distance"]
            else:
                result["score"] = 0.0

        sorted_results = sorted(results, key=lambda x: x.get("score", 0.0), reverse=not ascending)
        return sorted_results

    @staticmethod
    def filter_and_sort(search_results: Dict, min_score: float = 0.0,
                        max_score: float = 1.0, sort_order: str = "desc") -> Dict:
        """过滤和排序搜索结果
        
        Args:
            search_results: 搜索结果字典
            min_score: 最小分数阈值
            max_score: 最大分数阈值
            sort_order: 排序顺序 (asc/desc)
        
        Returns:
            过滤和排序后的结果
        """
        results = search_results.get("results", [])

        # 过滤
        filtered_results = FilteringService.filter_by_score(results, min_score, max_score)

        # 排序
        ascending = (sort_order == "asc")
        sorted_results = FilteringService.sort_by_score(filtered_results, ascending)

        # 保存结果
        filter_id = str(uuid.uuid4())
        result_data = {
            "filter_id": filter_id,
            "original_results": search_results,
            "filtered_count": len(sorted_results),
            "min_score": min_score,
            "max_score": max_score,
            "sort_order": sort_order,
            "filtered_results": sorted_results
        }

        save_result("filtering", filter_id, result_data)

        return {
            "filter_id": filter_id,
            "status": "success",
            "original_count": len(results),
            "filtered_count": len(sorted_results),
            "results": sorted_results
        }
