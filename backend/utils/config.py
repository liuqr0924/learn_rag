import os
from dotenv import load_dotenv

# 从backend目录加载.env文件
backend_dir = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(backend_dir, ".env")
load_dotenv(dotenv_path=env_path)

# Azure OpenAI配置
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-5-chat-2025-08-07")

# 本地embedding模型配置
LOCAL_EMBEDDING_MODEL = os.getenv("LOCAL_EMBEDDING_MODEL", "bert-base-uncased")

# 数据存储路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

