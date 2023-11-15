from fastapi import FastAPI
from app.routers import ads, auth, comments, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(ads.router)
app.include_router(comments.router)
