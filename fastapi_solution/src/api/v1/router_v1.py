from fastapi import APIRouter

from api.v1.films_router import router as films_router
from api.v1.genres_router import router as genres_router
from api.v1.persons_router import router as persons_router
from api.v1.auth_router import router as auth_router

router = APIRouter()

router.include_router(films_router, prefix='/films', tags=['films'])
router.include_router(persons_router, prefix='/persons', tags=['persons'])
router.include_router(genres_router, prefix='/genres', tags=['genres'])
router.include_router(auth_router, prefix='/auth', tags=['auth'])
