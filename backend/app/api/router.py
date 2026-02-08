from fastapi import APIRouter

from app.api.routes import admin, auth, categories, interactions, prompts

api_router = APIRouter()
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(categories.router, prefix='/categories', tags=['categories'])
api_router.include_router(prompts.router, prefix='/prompts', tags=['prompts'])
api_router.include_router(interactions.router, prefix='/interactions', tags=['interactions'])
api_router.include_router(admin.router, prefix='/admin', tags=['admin'])
