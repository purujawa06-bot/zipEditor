import asyncio
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import BASE_DIR, PORT
from cleanup import cleanup_old_sessions
from routes import router

# ==========================================
# APLIKASI FASTAPI
# ==========================================
app = FastAPI(title="PuruAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
async def startup_event():
    os.makedirs(BASE_DIR, exist_ok=True)
    asyncio.create_task(cleanup_old_sessions())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
