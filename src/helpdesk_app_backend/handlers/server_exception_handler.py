from fastapi.requests import Request
from fastapi.responses import JSONResponse


# リクエストの型はRequest（Exceptionが発生した際に）で、レスポンスはJSONResponse（JSON形式）で返すよう指定
def handler(request: Request, exc: Exception) -> JSONResponse:
    # CORS設定
    response = JSONResponse(status_code=500, content={"detail": "システムエラーが発生しました"})
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response
