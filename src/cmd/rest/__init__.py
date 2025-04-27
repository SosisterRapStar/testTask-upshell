from fastapi.routing import APIRouter
from .bar import router as bar_router

router = APIRouter()


router.include_router(router=bar_router)
