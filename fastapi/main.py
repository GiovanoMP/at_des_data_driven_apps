from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import matches, players, narratives

app = FastAPI(
    title="API de Análise de Futebol",
    description="API para análise de partidas de futebol usando dados do StatsBomb",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluindo os routers
app.include_router(matches.router, prefix="/api/v1/matches", tags=["matches"])
app.include_router(players.router, prefix="/api/v1/players", tags=["players"])
app.include_router(narratives.router, prefix="/api/v1/narratives", tags=["narratives"])

@app.get("/")
async def root():
    return {
        "message": "Bem-vindo à API de Análise de Futebol",
        "docs": "/docs",
        "version": "1.0.0"
    }
