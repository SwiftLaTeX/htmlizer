import os
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
APIKEY = os.getenv("APIKEY", "0000111122223333")
PDF2HTMLEX_ASSETS_URL = os.path.join(os.path.split(os.path.realpath(__file__))[0], "pdf2htmlex")
TICKING_ACCURARCY = 0.005
TASK_TIMEOUT = 10
WORKPLACE_DIR = os.path.join(os.path.split(os.path.realpath(__file__))[0], "workplace")
FONT_DIR = os.path.join(os.path.split(os.path.realpath(__file__))[0], "font")
FILE_STORAGE_TIME = 3600
