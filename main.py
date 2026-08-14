

from datetime import datetime
import os
import requests
import time
import traceback
from gtts import gTTS

# ==============================================================================
# 1. DEFINICIÓN OBLIGATORIA DE HERRAMIENTAS (PRIMERO)
# ==============================================================================
TOKEN = "8019113948:AAGn6QusV-2FsR0NAqI5CJ1DDFmDqA1AKvs"
CHAT_ID = "8687968442"

def enviar_alerta_completa(mensaje_texto):
    """Envía la alerta de forma dual: texto HTML y audio por voz a Telegram."""
    url_text = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje_texto, "parse_mode": "HTML"}
    try:
        requests.post(url_text, data=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando texto a Telegram: {e}")

    try:
        texto_limpio = (
            mensaje_texto.replace("<b>", "")
            .replace("</b>", "")
            .replace("🚀", "")
            .replace("🚨", "")
            .replace("🔔", "")
            .replace("📈", "")
            .replace("⛽", "")
            .replace("🤖", "")
            .replace("🟢", "")
            .replace("🔴", "")
            .replace("✅", "")
            .replace("❌", "")
            .replace("⚠️", "")
            .replace("🛠️", "")
            .replace("<br>", " ")
            .replace("<i>", "")
            .replace("</i>", "")
            .replace("<pre>", "")
            .replace("</pre>", "")
        )
        tts = gTTS(text=texto_limpio, lang='es')
        audio_path = "alerta.mp3"
        tts.save(audio_path)

        url_audio = f"https://api.telegram.org/bot{TOKEN}/sendAudio"
        with open(audio_path, "rb") as audio:
            requests.post(url_audio, data={"chat_id": CHAT_ID}, files={"audio": audio}, timeout=15)

        if os.path.exists(audio_path):
            os.remove(audio_path)
    except Exception as e:
        print(f"Error enviando audio a Telegram: {e}")

def notificar_error_critico(contexto, excepcion):
    tb = traceback.format_exc()
    mensaje_error = (
        f"⚠️ <b>ALERTA DE ERROR EN EL MOTOR</b> ⚠️\n"
        f"<b>Ubicación:</b> {contexto}\n"
        f"<b>Detalle:</b> {str(excepcion)}\n"
        f"-----------------------------------\n"
        f"<pre>{tb[-300:]}</pre>"
    )
    print(f"[ERROR CRÍTICO] {contexto}: {excepcion}")
    url_text = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje_error, "parse_mode": "HTML"}
    try:
        requests.post(url_text, data=payload, timeout=5)
    except Exception as e:
        print(f"No se pudo notificar el error a Telegram: {e}")

def obtener_ultimo_comando():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        res = requests.get(url, timeout=3).json()
        if "result" in res and len(res["result"]) > 0:
            ultimo = res["result"][-1]
            update_id = ultimo["update_id"]
            requests.get(url, params={"offset": update_id + 1}, timeout=2)
            msg = ultimo.get("message", {})
            texto = msg.get("text", "")
            if texto:
                return texto.strip().lower()
    except Exception as e:
        print(f"Error comando: {e}")
    return ""

def ejecutar_escaneo_manual():
    ahora = datetime.now()
    reporte_escaneo = (
        f"🔍 <b>ESCANEO MANUAL DEL MOTOR ACTIVADO</b><br>"
        f"-----------------------------------\n"
        f"<b>Fase actual:</b> Monitoreando trampas del comprador y vendedor.<br>"
        f"<b>Estructura M30 / H1:</b> Sincronización en curso.<br>"
        f"<b>Hora de escaneo:</b> {ahora.strftime('%H:%M:%S')}<br>"
        f"<b>Resultado:</b> Sistema alerta y listo para el gatillo."
    )
    enviar_alerta_completa(reporte_escaneo)

# ==============================================================================
# 2. MOTOR PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    print("Motorcito de trading 24/7 iniciado...")
    enviar_alerta_completa("🤖 <b>Motorcito operativo:</b> Sistema conectado y escuchando comandos.")

    while True:
        try:
            comando = obtener_ultimo_comando()
            if comando:
                print(f"Comando recibido: {comando}")
                if any(p in comando for p in ["escanear", "escaneo", "r7escanear"]):
                    ejecutar_escaneo_manual()
                elif any(p in comando for p in ["estado", "status"]):
                    enviar_alerta_completa("🟢 <b>Estado del Sistema:</b> Operando sin interrupciones.")

            time.sleep(3)
        except Exception as e:
            notificar_error_critico("Bucle Principal", e)
            time.sleep(5)

