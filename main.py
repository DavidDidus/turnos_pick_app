from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from propuesta_turnos_picking import (
    optimizar_tiempos_dotacion_variable_con_paridad,
    normaliza_demanda,
    escalar_demanda,
    construir_ft_horas_por_dia,
    construir_pt_horas,
)

app = FastAPI()

# CORS (igual lo dejamos por si acaso)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELO
# =========================
class InputData(BaseModel):
    factor: float
    iceo: float
    jornada: str
    ft_colacion: bool
    pt_colacion: bool
    ft_total: int
    pt_total: int
    demanda: Dict[str, float]

# =========================
# API
# =========================
@app.post("/optimizar")
def optimizar(data: InputData):

    dem_base = normaliza_demanda(data.demanda)
    demanda = escalar_demanda(dem_base, data.factor)

    ft_horas = construir_ft_horas_por_dia(data.jornada, data.ft_colacion)
    pt_horas = construir_pt_horas(data.pt_colacion)

    resumen, detalle = optimizar_tiempos_dotacion_variable_con_paridad(
        demanda=demanda,
        ft_horas_por_dia=ft_horas,
        pt_horas_dia=pt_horas,
        ft_total=data.ft_total,
        pt_total=data.pt_total,
        cajas_por_hora=data.iceo
    )

    return {
        "resumen": resumen,
        "detalle": detalle
    }

# =========================
# FRONTEND
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend", "dist")

# Archivos estáticos
app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")),
    name="assets"
)

# Home
@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# SPA (MUY IMPORTANTE)
@app.get("/{full_path:path}")
def serve_spa(full_path: str):
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))