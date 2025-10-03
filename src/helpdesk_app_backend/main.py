from fastapi import FastAPI

from helpdesk_app_backend.api import router

app = FastAPI()

# FastAPI本体 (app) に、上で読み込んだ集約済みのルーター一式を登録
app.include_router(router, prefix="/api")
