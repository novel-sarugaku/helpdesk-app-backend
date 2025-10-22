from fastapi import APIRouter

from helpdesk_app_backend.api.v1.account import router as account_router
from helpdesk_app_backend.api.v1.auth import router as auth_router
from helpdesk_app_backend.api.v1.healthcheck import router as healthcheck_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(healthcheck_router, prefix="/healthcheck", tags=["Healthcheck"])
router.include_router(account_router, prefix="/admin/account", tags=["Account"])
