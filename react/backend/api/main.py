from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import risk, network, metrics, simulator, agent, links

app = FastAPI(title="GNN Supply Chain Risk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics.router, prefix="/api")
app.include_router(risk.router, prefix="/api")
app.include_router(network.router, prefix="/api")
app.include_router(simulator.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(links.router, prefix="/api")

@app.get("/api/health")
def health():
    return {"status": "ok"}
