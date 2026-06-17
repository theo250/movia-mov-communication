# agent/main.py — Serveur FastAPI + Webhook WhatsApp
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

from agent.brain import generar_respuesta
from agent.memory import inicializar_db, guardar_mensaje, obtener_historial
from agent.providers import obtener_proveedor

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
log_level = logging.DEBUG if ENVIRONMENT == "development" else logging.INFO
logging.basicConfig(level=log_level)
logger = logging.getLogger("agentkit")

proveedor = obtener_proveedor()
PORT = int(os.getenv("PORT", 8000))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await inicializar_db()
    logger.info("Base de données initialisée")
    logger.info(f"Serveur AgentKit sur le port {PORT}")
    logger.info(f"Fournisseur WhatsApp: {proveedor.__class__.__name__}")
    yield


app = FastAPI(title="Movia — MOV Communication WhatsApp Agent", version="1.0.0", lifespan=lifespan)


@app.get("/")
async def health_check():
    return {"status": "ok", "agent": "Movia", "service": "MOV Communication"}


@app.get("/webhook")
async def webhook_verificacion(request: Request):
    resultado = await proveedor.validar_webhook(request)
    if resultado is not None:
        return PlainTextResponse(str(resultado))
    return {"status": "ok"}


@app.post("/webhook")
async def webhook_handler(request: Request):
    try:
        mensajes = await proveedor.parsear_webhook(request)
        for msg in mensajes:
            if msg.es_propio or not msg.texto:
                continue
            logger.info(f"Message de {msg.telefono}: {msg.texto}")
            historial = await obtener_historial(msg.telefono)
            respuesta = await generar_respuesta(msg.texto, historial)
            await guardar_mensaje(msg.telefono, "user", msg.texto)
            await guardar_mensaje(msg.telefono, "assistant", respuesta)
            await proveedor.enviar_mensaje(msg.telefono, respuesta)
            logger.info(f"Réponse à {msg.telefono}: {respuesta}")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Erreur webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
