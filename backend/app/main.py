from fastapi import FastAPI

from backend.app.routes.chats import router as chats_router
from backend.app.routes.agent import router as agent_router
from backend.app.routes.databricks import router as databricks_router

app = FastAPI(title="py-analytics-agent")

app.include_router(chats_router)
app.include_router(agent_router)
app.include_router(databricks_router)


@app.get("/health")
def health():
    return {"status": "ok"}