from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径，支持从backend目录或项目根目录运行
backend_dir = Path(__file__).parent
project_root = backend_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.routers import loading, chunking, parsing, embedding, indexing, filtering, generation

app = FastAPI(title="RAG Practical Camp API", version="1.0.0")

# CORS配置，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(loading.router, prefix="/api/loading", tags=["文档加载"])
app.include_router(chunking.router, prefix="/api/chunking", tags=["文档分块"])
app.include_router(parsing.router, prefix="/api/parsing", tags=["文档解析"])
app.include_router(embedding.router, prefix="/api/embedding", tags=["向量嵌入"])
app.include_router(indexing.router, prefix="/api/indexing", tags=["向量索引"])
app.include_router(filtering.router, prefix="/api/filtering", tags=["结果过滤和排序"])
app.include_router(generation.router, prefix="/api/generation", tags=["文本生成"])

# 静态文件服务（前端页面 - Vue构建后的dist目录）
frontend_dist_path = os.path.join(project_root, "frontend", "dist")
if os.path.exists(frontend_dist_path):
    app.mount("/static", StaticFiles(directory=frontend_dist_path), name="static")
    # 提供前端页面
    @app.get("/")
    async def read_root():
        """返回前端主页"""
        frontend_index = os.path.join(frontend_dist_path, "index.html")
        if os.path.exists(frontend_index):
            return FileResponse(frontend_index)
        return {"message": "RAG Practical Camp API - 请先构建前端: cd frontend && npm run build"}
else:
    # 如果dist不存在，尝试使用旧的静态文件
    frontend_static_path = os.path.join(project_root, "frontend", "static")
    if os.path.exists(frontend_static_path):
        app.mount("/static", StaticFiles(directory=frontend_static_path), name="static")
    
    @app.get("/")
    async def read_root():
        """返回API信息"""
        return {"message": "RAG Practical Camp API - 请先构建前端: cd frontend && npm install && npm run build"}

if __name__ == "__main__":
    import uvicorn
    # 使用字符串形式的模块路径以支持reload功能
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

