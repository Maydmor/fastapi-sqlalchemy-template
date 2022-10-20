from fastapi import FastAPI
from pip import List
from pydantic import BaseModel
from database.models import setup
from routers import user_router, auth_router
from fastapi.middleware.cors import CORSMiddleware

setup()
app = FastAPI()

allowed_origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix='/users', tags=['User'])
app.include_router(auth_router, tags=['Security'])


class IndexResponse(BaseModel):
    version: str

@app.get('/', response_model=IndexResponse)
def index():
    return IndexResponse(version='v1')