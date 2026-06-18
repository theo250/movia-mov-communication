# agent/brain.py — Cerveau de Movia : connexion Claude API
import os
import yaml
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("agentkit")

def _get_api_key() -> str:
    return os.environ.get("ANTHROPIC_API_KEY", "")


def cargar_config_prompts() -> dict:
    try:
        with open("config/prompts.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.error("config/prompts.yaml introuvable")
        return {}


def cargar_system_prompt() -> str:
    config = cargar_config_prompts()
    return config.get("system_prompt", "Vous êtes Movia, assistante de MOV Communication. Répondez en français.")


def obtener_mensaje_error() -> str:
    config = cargar_config_prompts()
    return config.get("error_message", "Je rencontre momentanément une difficulté technique. Merci de réessayer.")


def obtener_mensaje_fallback() -> str:
    config = cargar_config_prompts()
    return config.get("fallback_message", "Je n'ai pas bien compris votre message. Pourriez-vous le reformuler ?")


async def generar_respuesta(mensaje: str, historial: list[dict]) -> str:  # noqa: RUF029
    if not mensaje or len(mensaje.strip()) < 2:
        return obtener_mensaje_fallback()

    system_prompt = cargar_system_prompt()
    mensajes = [{"role": msg["role"], "content": msg["content"]} for msg in historial]
    mensajes.append({"role": "user", "content": mensaje})

    try:
        key = _get_api_key()
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-6",
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": mensajes,
                }
            )
        data = r.json()
        if r.status_code != 200:
            raise Exception(f"Error code: {r.status_code} - {data}")
        respuesta = data["content"][0]["text"]
        logger.info(f"Réponse générée (status={r.status_code})")
        return respuesta
    except Exception as e:
        logger.error(f"Erreur Claude API: {e}")
        return obtener_mensaje_error()
