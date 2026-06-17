# tests/test_local.py — Simulateur de chat en terminal
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.brain import generar_respuesta
from agent.memory import inicializar_db, guardar_mensaje, obtener_historial, limpiar_historial

TELEFONO_TEST = "test-local-001"


async def main():
    await inicializar_db()
    print()
    print("=" * 55)
    print("   Movia — MOV Communication | Test Local")
    print("=" * 55)
    print()
    print("  Écrivez comme si vous étiez un prospect ou client.")
    print("  Commandes spéciales:")
    print("    'effacer'  — efface l'historique")
    print("    'quitter'  — termine le test")
    print()
    print("-" * 55)
    print()

    while True:
        try:
            mensaje = input("Vous: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nTest terminé.")
            break

        if not mensaje:
            continue
        if mensaje.lower() == "quitter":
            print("\nTest terminé.")
            break
        if mensaje.lower() == "effacer":
            await limpiar_historial(TELEFONO_TEST)
            print("[Historique effacé]\n")
            continue

        historial = await obtener_historial(TELEFONO_TEST)
        print("\nMovia: ", end="", flush=True)
        respuesta = await generar_respuesta(mensaje, historial)
        print(respuesta)
        print()
        await guardar_mensaje(TELEFONO_TEST, "user", mensaje)
        await guardar_mensaje(TELEFONO_TEST, "assistant", respuesta)


if __name__ == "__main__":
    asyncio.run(main())
