from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from router.experiment import experiment_router
from router.user import register_user_routers


app = FastAPI()


# register router
register_user_routers(app)
app.include_router(experiment_router, prefix='/v1/experiment')

# mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    """
    on_startup
    :return:
    """
    from model import init_db

    await init_db()


@app.get("/")
async def index():
    return FileResponse('static/index.html')


"""
uvicorn server:app --host 127.0.0.1 --port 8000 --workers 1 --reload 
"""