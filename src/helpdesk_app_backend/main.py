from fastapi import FastAPI

from helpdesk_app_backend.api import router
from helpdesk_app_backend.handlers.server_exception_handler import handler

app = FastAPI()

# FastAPI本体 (app) に、上で読み込んだ集約済みのルーター一式を登録
app.include_router(router, prefix="/api")

# 引数；反応してほしいもの, 反応した際の処理
app.add_exception_handler(Exception, handler)
