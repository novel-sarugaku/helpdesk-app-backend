from fastapi import HTTPException


# Exceptionの中のUnauthorizedExceptionというエラー
# Exception > HTTPException > UnauthorizedException
# HTTPExceptionを使う際は、tatus_code=やdetail=messageを記載するのがお決まり
class UnauthorizedException(HTTPException):
    # self：クラス自身（＝UnauthorizedException）記載するのがお決まり
    def __init__(self, message:str = "認証エラー") -> None:
        # super：親クラス（＝HTTPException）
        super().__init__(status_code=401, detail=message)
