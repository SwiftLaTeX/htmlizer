import os
DB_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/htmlizer")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
PDF2HTMLEX_ASSETS_URL = os.path.join(os.path.split(os.path.realpath(__file__))[0], "pdf2htmlex")
TICKING_ACCURARCY = 0.05
TASK_TIMEOUT = 10
WORKPLACE_DIR = os.path.join(os.path.split(os.path.realpath(__file__))[0], "workplace")
ALLOWED_TOKEN = ['12345678123456781234567812345678']