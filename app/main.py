from fastapi import FastAPI
from app.routes.upload_routes import router as upload_router
from app.routes.chat_routes import router as chat_router

app = FastAPI()
app.include_router(upload_router)


# uv run uvicorn app.main:app --reload
