from fastapi import HTTPException


# Exceptionの中のForbiddenExceptionというエラー
# Exception > HTTPException > ForbiddenException
# HTTPExceptionを使う際は、tatus_code=やdetail=messageを記載するのがお決まり
class ForbiddenException(HTTPException):
    # self：クラス自身（＝ForbiddenException）記載するのがお決まり
    def __init__(self, message: str = "権限エラー") -> None:
        # super：親クラス（＝HTTPException）
        super().__init__(status_code=403, detail=message)
