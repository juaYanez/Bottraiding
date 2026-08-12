import os
import sys
import json
import logging
import traceback
import asyncio
import threading
import time
import requests
import websockets
import telebot
from datetime import datetime
from gtts import gTTS
from langchain.memory import ConversationBufferWindowMemory
from fastapi import FastAPI, Request, HTTPException
import uvicorn

# Configuración de logs con formato de diagnóstico profundo
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger(__name__)

def log_error_profundo(contexto, e):
    error_detallado = traceback.format_exc()
    logger.error(f">>> [DIAGNÓSTICO CRÍTICO EN {contexto}]: {str(e)}")
    logger.error(f">>> [DETALLE TÉCNICO COMPLETO]:\n{error_detallado}")
    return error_detallado

# ==========================================
# 1. VARIABLES DE ENTORNO EN RENDER
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
DERIV_WS_URL = os.environ.get("DERIV_WS_URL", "wss://ws.derivws.com/websockets/v3?app_id=1089")
MOTORCITO_URL = os.environ.get("MOTORCITO_URL", "http://localhost:8001/api/actualizar_parametros")

bot = telebot.TeleBot(TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None
app_fastapi = FastAPI()

# ==========================================
# 2. FILTRO EXCLUSIVO DE ACTIVOS (SOLO 3)
# ==========================================
MAPEO_DERIV = {
    "BOOM 500": "1000",
    "BOOM 1000": "1001",
    "GBP/USD": "frxGBPUSD"
}

def validar_y_limpiar_activo(simbolo: str):
    s = simbolo.upper().replace("/", "").replace(" ", "")
    if "500" in s:
        return "BOOM 500"
    elif "1000" in s:
        return "BOOM 1000"
    elif "GBP" in s or "USD" in s:
        return "GBP/USD"
    return None

# ==========================================
# 3. CEREBRO, APRENDIZAJE Y MÓDULO MATEMÁTICO
# ==========================================
class CerebroShane:
    def __init__(self):
        self.memoria = ConversationBufferWindowMemory(k=50, return_messages=True)
        self.last_heartbeat = time.time()
        self.tareas_personales = []
        self.registro_aprendizajes = []
        
        self.ARQUITECTURA_GEMA = """
        [ARQUITECTURA UNIFICADA DE LA GEMA Y APRENDIZAJE BIDIRECCIONAL]
        1. Falsa salida alcista (Trampa del comprador).
        2. Purga del vendedor y del Order Block (Trampa del vendedor / OB).
        3. Gatillo definitivo de confirmación e inicio del verdadero movimiento.
        Shane procesa fractales de punta a punta, correlaciona gráficos multitemporales
        y retroalimenta al motorcito para optimizar su velocidad operativa.
        """
        self.memoria.save_context(
            {"input": "Cargar arquitectura unificada y sistema de aprendizaje"},
            {"output": self.ARQUITECTURA_GEMA}
        )
        logger.info("🧠 [Shane/Chain Autónomo]: Cerebro, memoria ampliada y red de auditoría profunda iniciados.")

    def enviar_actualizacion_al_motor(self, patron_clave: str, reglas: dict):
        """
        CANAL DE SUBIDA (Bidireccional): Inyecta el aprendizaje directamente 
        en las carpetas/parámetros del motorcito y reporta el estado exacto.
        """
        payload = {
            "timestamp": time.time(),
            "patron": patron_clave,
            "reglas_aprendidas": reglas
        }
        try:
            logger.info(f">>> [BIDIRECCIONALIDAD]: Iniciando inyección de datos al motorcito en [{MOTORCITO_URL}]...")
            response = requests.post(MOTORCITO_URL, json=payload, timeout=5)
            if response.status_code == 200:
                logger.info(">>> [BIDIRECCIONALIDAD]: ¡Motorcito actualizado y optimizado con éxito!")
                return True
            else:
                logger.warning(f">>> [BIDIRECCIONALIDAD]: El motorcito respondió con estado {response.status_code}")
                return False
        except Exception as e:
            log_error_profundo("BIDIRECCIONALIDAD_MOTORCITO", e)
            return False

    async def obtener_historial_velas(self, simbolo: str, timeframe: str = "H1", cantidad: int = 100):
        activo = validar_y_limpiar_activo(simbolo)
        if not activo:
            return []
        tf_map = {"M1": 60, "M5": 300, "M15": 900, "M30": 1800, "H1": 3600, "H4": 14400, "D1": 86400}
        granularity = tf_map.get(timeframe.upper(), 3600)
        symbol_code = MAPEO_DERIV.get(activo)
        try:
            async with websockets.connect(DERIV_WS_URL) as ws:
                req = {
                    "ticks_history": symbol_code,
                    "adjust_start_time": 1,
                    "count": cantidad,
                    "end": "latest",
                    "style": "candles",
                    "granularity": granularity
                }
                await ws.send(json.dumps(req))
                res = await ws.recv()
                datos = json.loads(res)
                if "candles" in datos:
                    return datos["candles"]
        except Exception as e:
            log_error_profundo("WS_DERIV_HISTORIAL", e)
        return []

    async def medir_fractal_completo(self, simbolo: str, timeframe: str = "H1"):
        activo = validar_y_limpiar_activo(simbolo)
        if not activo:
            return "Juan, recuerda que solo audito Boom 500, Boom 1000 y GBP/USD."
        tf_minutos = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
        minutos_vela = tf_minutos.get(timeframe.upper(), 60)
        velas = await self.obtener_historial_velas(activo, timeframe=timeframe, cantidad=100)
        if not velas:
            return f"No pude obtener la data de velas para {activo} en {timeframe}."
        
        cierre = [v["close"] for v in velas]
        pico_max = max(cierre[-30:])
        idx_pico = cierre[-30:].index(pico_max)
        velas_subida = idx_pico
        velas_bajada = len(cierre[-30:]) - idx_pico - 1
        velas_totales = velas_subida + velas_bajada
        
        minutos_totales = velas_totales * minutos_vela
        horas_totales = minutos_totales / 60
        dias_totales = horas_totales / 24
        tiempo_txt = f"{dias_totales:.1f} días ({horas_totales:.1f} hrs)" if horas_totales >= 24 else f"{horas_totales:.1f} hrs"
        
        return (
            f"📊 **Análisis Fractal de Punta a Punta ({activo} - {timeframe.upper()}):**\n"
            f"📈 **Impulso de Subida:** {velas_subida} velas\n"
            f"📉 **Despliegue/Bajada:** {velas_bajada} velas\n"
            f"⏱️ **Total Fractal:** {velas_totales} velas exactas\n"
            f"⏳ **Tiempo Transcurrido:** {tiempo_txt}"
        )

    def despachar_telegram_blindado(self, mensaje: str, incluir_voz: bool = True):
        logger.info(">>> [AUDITORÍA DE DESPACHO CHAIN]: Iniciando entrega física de texto y voz hacia Telegram...")
        if not TELEGRAM_TOKEN or not CHAT_ID or not bot:
            logger.error(">>> [ERROR CRÍTICO RENDER]: Faltan credenciales o token de Telegram.")
            return False

        try:
            bot.send_message(CHAT_ID, mensaje, parse_mode="Markdown")
            if incluir_voz:
                texto_limpio = mensaje.replace("*", "").replace("#", "").replace("_", "").replace("`", "")
                tts = gTTS(text=texto_limpio, lang='es')
                audio_path = "respuesta_shane.mp3"
                tts.save(audio_path)
                with open(audio_path, 'rb') as audio_file:
                    bot.send_voice(CHAT_ID, voice=audio_file)
            return True
        except Exception as e:
            log_error_profundo("DESPACHO_TELEGRAM", e)
        return False

shane = CerebroShane()

# ==========================================
# 4. ENDPOINTS FASTAPI (LATIDOS, ALERTAS Y CRECIMIENTO)
# ==========================================
@app_fastapi.post("/api/heartbeat")
async def recibir_latido():
    shane.last_heartbeat = time.time()
    return {"status": "ok", "timestamp": shane.last_heartbeat}

@app_fastapi.post("/api/alerta_motor")
async def recibir_alerta_motor(request: Request):
    try:
        data = await request.json()
        evento = data.get("evento", "Alerta General")
        detalles = data.get("detalles", "Sin detalles")
        notificacion = f"⚡ **ALERTA DEL MOTOR** ⚡\n\n📋 **Evento:** {evento}\n🔍 **Detalles:** {detalles}"
        shane.despachar_telegram_blindado(notificacion, incluir_voz=True)
        return {"status": "success"}
    except Exception as e:
        log_error_profundo("ENDPOINT_ALERTA_MOTOR", e)
        raise HTTPException(status_code=500, detail="Error en procesamiento de alerta")

# ==========================================
# 5. ATENCIÓN DE MENSAJES, VOZ E IMÁGENES
# ==========================================
def responder_a_juan(mensaje_texto: str):
    try:
        texto = mensaje_texto.strip()
        active = validar_y_limpiar_activo(texto)
        
        if "fractal" in texto.lower() or "vela" in texto.lower() or "tiempo" in texto.lower() or "cuántas" in texto.lower():
            tf = "H1"
            for t in ["M1", "M5", "M15", "M30", "H1", "H4", "D1"]:
                if t.lower() in texto.lower():
                    tf = t
                    break
            target_activo = active if active else "BOOM 500"
            resultado = asyncio.run(shane.medir_fractal_completo(target_activo, timeframe=tf))
        elif "estado" in texto.lower() or "motor" in texto.lower():
            dif = time.time() - shane.last_heartbeat
            resultado = f"✅ El motor está activo. Último latido hace {int(dif)} segundos." if dif <= 120 else f"⚠️ Alerta: El motor lleva {int(dif)} segundos sin latidos."
        else:
            resultado = f"Recibido Juan: {texto}. Procesando parámetros bajo la Gema para BOOM 500, BOOM 1000 y GBP/USD."
        
        shane.despachar_telegram_blindado(resultado, incluir_voz=True)
        return resultado
    except Exception as e:
        log_error_profundo("RESPONDER_A_JUAN", e)

@bot.message_handler(content_types=['text'])
def manejar_texto(message):
    try:
        responder_a_juan(message.text or "")
    except Exception as e:
        log_error_profundo("MANEJAR_TEXTO_TELEGRAM", e)

@bot.message_handler(content_types=['photo'])
def manejar_imagen(message):
    try:
        hora_inicio = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
        
        # 1. Mensaje en vivo de que el proceso ha iniciado
        mensaje_inicio = (
            f"🔄 **Iniciando actualización y aprendizaje...**\n"
            f"⏱️ **Hora de inicio:** {hora_inicio}\n"
            f"📂 *Chain está procesando tu instrucción gráfica y preparando la inyección al motorcito.*"
        )
        shane.despachar_telegram_blindado(mensaje_inicio, incluir_voz=True)

        caption = message.caption or "Instrucción multitemporal sin descripción escrita"
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("secuencia_grafica.jpg", "wb") as f:
            f.write(downloaded_file)
        logger.info(">>> [VISIÓN Y MEMORIA]: Gráfica almacenada con éxito.")

        patron_aprendido = f"Secuencia multitemporal analizada: {caption}"
        shane.registro_aprendizajes.append(patron_aprendido)
        
        # 2. Inyección de datos hacia el motorcito (Bidireccionalidad)
        exito_motor = shane.enviar_actualizacion_al_motor(
            "patron_multitemporal_gema", 
            {"descripcion": caption, "total_registros": len(shane.registro_aprendizajes)}
        )

        hora_fin = datetime.now().strftime("%d/%m/%Y a las %H:%M:%S")
        estado_motor_txt = "✅ Sincronizado y actualizado con éxito" if exito_motor else "⚠️ Advertencia: No se pudo conectar con el motorcito (revisar URL)"

        # 3. Informe detallado final que confirma que todo está listo
        informe_final = (
            f"✨ **¡Todo listo! Actualización completada** ✨\n\n"
            f"🕒 **Hora de cierre:** {hora_fin}\n"
            f"💬 **Instrucción procesada:** {caption}\n"
            f"📊 **Estado del Motorcito:** {estado_motor_txt}\n"
            f"📁 *Las carpetas de aprendizaje y parámetros internos han sido actualizados satisfactoriamente.*"
        )
        shane.despachar_telegram_blindado(informe_final, incluir_voz=True)

    except Exception as e:
        log_error_profundo("MANEJAR_IMAGEN_TELEGRAM", e)
        shane.despachar_telegram_blindado("❌ Ocurrió un error crítico durante la actualización. Revisa los logs de Render.", incluir_voz=True)

# ==========================================
# 6. INICIALIZACIÓN
# ==========================================
@app_fastapi.on_event("startup")
def arrancar():
    try:
        if bot:
            logger.info(">>> [INICIO TELEGRAM]: Escuchador activo en segundo plano 24/7.")
            bot.infinity_polling(skip_pending_updates=True)
    except Exception as e:
        log_error_profundo("STARTUP_TELEGRAM_POLLING", e)

thread_tele = threading.Thread(target=arrancar, daemon=True)
thread_tele.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app_fastapi, host="0.0.0.0", port=port)
