
from dotenv import load_dotenv
load_dotenv()

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from helpers.ai_helper import AIHelper
from fastapi import FastAPI
from controller.access_control_controller import router as access_control_router
from controller.user_controller import router as user_router
from controller.history_controller import router as history_router
from controller.payment_controller import router as payment_router


sys.path.append(str(Path(__file__).parent.resolve()))


@asynccontextmanager
async def lifespan(app: FastAPI):
    AIHelper.load_models()
    yield

app = FastAPI(title="Smart Gate API", lifespan=lifespan)

app.include_router(access_control_router, prefix="/smart-gate/v1")
app.include_router(user_router, prefix="/smart-gate/v1")
app.include_router(history_router, prefix="/smart-gate/v1")
app.include_router(payment_router, prefix= "/smart-gate/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)