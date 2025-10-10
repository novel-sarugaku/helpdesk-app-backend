from fastapi import APIRouter

from helpdesk_app_backend.api.v1.auth import router as auth_router
from helpdesk_app_backend.api.v1.healthcheck import router as healthcheck_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(healthcheck_router, prefix="/healthcheck", tags=["Healthcheck"])
