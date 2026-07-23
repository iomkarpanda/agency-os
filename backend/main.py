from fastapi import FastAPI
from routers.auth_router import auth_route
app = FastAPI()

app.include_router(auth_route)