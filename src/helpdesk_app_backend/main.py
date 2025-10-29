from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from helpdesk_app_backend.api import router
from helpdesk_app_backend.handlers.server_exception_handler import handler

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # どこ（誰）からのアクセスを許すか（住所＝オリジン）を列挙
        # 開発中のフロントエンドのURL（Viteのデフォルト）
        "http://localhost:5173",
        "http://127.0.0.1:5173",  # localhost の別表記も許可
    ],
    allow_credentials=True,  # Cookieを使ったログイン情報のやり取りを許可する（JWTをCookieで使う場合は必須）
    allow_methods=["*"],  # どのHTTPメソッドを許すか。* は全部（GET/POST/PUT/DELETE…）
    allow_headers=["*"],  # どのHTTPヘッダを許すか。* は全部（Authorizationなども含む）
)

# FastAPI本体 (app) に、上で読み込んだ集約済みのルーター一式を登録
app.include_router(router, prefix="/api")

# 引数；反応してほしいもの, 反応した際の処理（上記の CORS設定 が効いていなため handler 内で別途設定）
app.add_exception_handler(Exception, handler)
