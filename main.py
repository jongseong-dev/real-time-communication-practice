from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.communicate import router

app = FastAPI()
app.include_router(router)
app.mount("/static", StaticFiles(directory="templates"), name="templates")