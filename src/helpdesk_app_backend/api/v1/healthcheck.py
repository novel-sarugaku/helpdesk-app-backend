from fastapi import APIRouter

router = APIRouter()

# テスト用のエンドポイント
@router.get("")
def healthcheck() -> str:
    return "テストOK"
