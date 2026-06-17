# agent/tools.py — Outils spécifiques MOV Communication
import os
import yaml
import logging

logger = logging.getLogger("agentkit")


def cargar_info_negocio() -> dict:
    try:
        with open("config/business.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("config/business.yaml introuvable")
        return {}


def obtener_horario() -> dict:
    info = cargar_info_negocio()
    return {"horario": info.get("negocio", {}).get("horario", "24h/24 — 7j/7"), "esta_abierto": True}


def buscar_en_knowledge(consulta: str) -> str:
    resultados = []
    knowledge_dir = "knowledge"
    if not os.path.exists(knowledge_dir):
        return "Aucun fichier de connaissance disponible."
    for archivo in os.listdir(knowledge_dir):
        ruta = os.path.join(knowledge_dir, archivo)
        if archivo.startswith(".") or not os.path.isfile(ruta):
            continue
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
                if consulta.lower() in contenido.lower():
                    resultados.append(f"[{archivo}]: {contenido[:500]}")
        except (UnicodeDecodeError, IOError):
            continue
    if resultados:
        return "\n---\n".join(resultados)
    return "Aucune information spécifique trouvée dans les fichiers."


def qualifier_prospect(secteur: str, budget: str, urgence: str) -> str:
    """Détermine si un prospect correspond à la cible MOV Communication."""
    secteurs_cibles = ["médical", "esthétique", "immobilier", "conseil", "coaching", "luxe", "dentaire", "clinique"]
    est_cible = any(s in secteur.lower() for s in secteurs_cibles)
    if est_cible:
        return "QUALIFIÉ — proposer un rendez-vous de découverte gratuit de 30 min"
    return "À ÉVALUER — demander plus d'informations sur le secteur et les objectifs"


def router_demande(message: str) -> str:
    """Route la demande vers le bon service interne."""
    message_lower = message.lower()
    if any(mot in message_lower for mot in ["facture", "paiement", "comptabilité", "virement"]):
        return "comptabilité"
    elif any(mot in message_lower for mot in ["vidéo", "créatif", "contenu", "tournage", "montage"]):
        return "production"
    elif any(mot in message_lower for mot in ["stratégie", "campagne", "résultats", "performance", "ads"]):
        return "consultant"
    elif any(mot in message_lower for mot in ["technique", "application", "accès", "connexion", "bug"]):
        return "support technique"
    return "équipe générale"
