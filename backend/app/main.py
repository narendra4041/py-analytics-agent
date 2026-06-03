from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.chats import router as chats_router
from backend.app.routes.agent import router as agent_router
from backend.app.routes.databricks import router as databricks_router

app = FastAPI(title="py-analytics-agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chats_router)
app.include_router(agent_router)
app.include_router(databricks_router)


@app.get("/health")
def health():
    return {"status": "ok"}