from fastapi import FastAPI

from routes import tasks, auth

app = FastAPI()
app.include_router(tasks.router)
app.include_router(auth.router)
