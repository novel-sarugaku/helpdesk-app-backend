import os

from dotenv import load_dotenv

load_dotenv()

# os.getenv= 環境変数を見てね
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
