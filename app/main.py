from fastapi import FastAPI

from config import settings
from db import Base, SessionLocal, engine
from routers import admin, auth, resources, users
from seed import seed_data

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_data(db)


@app.get("/")
def root():
    return {"message": "Custom authentication and authorization API is running"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(resources.router)