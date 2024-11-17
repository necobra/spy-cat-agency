from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from cat_spy_agency_app.routers.cats import router as cat_router
from cat_spy_agency_app.routers.missions import router as mission_router
from database import init_db


async def lifespan(app: FastAPI):
    await init_db()
    print("Startup complete")
    yield
    print("Shutting down resources")


app = FastAPI(
    title="Spy Cat Agency",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [
    "http://localhost",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cat_router)
app.include_router(mission_router)


@app.get("/")
async def root():
    return {"message": "Spy Cat Agency API"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
