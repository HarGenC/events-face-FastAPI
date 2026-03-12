import os
import sys

import uvicorn
from fastapi import FastAPI

from app.api.endpoints import router

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = FastAPI(title="events-face")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=True)
