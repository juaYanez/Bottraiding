import os
import sys
import json
import logging
import asyncio
import threading
import time
import requests
import websockets
import telebot
import speech_recognition as sr
from gtts import gTTS
from langchain.memory import ConversationBufferWindowMemory
from fastapi import FastAPI, Request

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ==========================================
# 1. VARIABLES DE ENTORNO EN RENDER
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
DERIV_WS_URL = os.environ.get("DERIV_WS_URL", "wss://ws.derivws.com/websockets/v3?app_id=1089")

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
    """
    Filtra estrictamente para que Shane solo consuma datos
    y procese las matemáticas de los 3 activos permitidos.
    """
    s = simbolo.upper().replace("/", "").replace(" ", "")
    if "500" in s:
        return "BOOM 500"
    elif "1000" in s:
        return "BOOM 1000"
    elif "GBP" in s or "USD" in s:
        return "GBP/USD"
    return None

# ==========================================
# 3. CEREBRO Y MÓDULO MATEMÁTICO DE SHANE
# ==========================================
class CerebroShane:
    def __init__(self):
        # Memoria persistente para evitar amnesia
        self.memoria = ConversationBufferWindowMemory(k=30, return_messages=True)
        self.last_heartbeat = time.time()
        self.tareas_personales = []  # Agenda de encargos independientes

        # Arquitectura de La Gema gravada en memoria
        self.ARQUITECTURA_GEMA = """
        [ARQUITECTURA UNIFICADA DE LA GEMA]
        1. Falsa salida alcista (Trampa del comprador).
        2. Purga del vendedor y del Order Block (Trampa del vendedor / OB).
        3. Gatillo definitivo de confirmación e inicio del verdadero movimiento.
        """
        self.memoria.save_context(
            {"input": "Cargar arquitectura unificada de La Gema"},
            {"output": self.ARQUITECTURA_GEMA}
        )
        logging.info("🧠 [Shane]: Cerebro, memoria, túnel a Deriv y motor matemático iniciados.")

    # ---------------------------------------------------------
    # TÚNEL DIRECTO A DERIV (PARA NO MOLESTAR AL MOTOR)
    # ---------------------------------------------------------
    async def consultar_precio_directo(self, simbolo: str):
        activo = validar_y_limpiar_activo(simbolo)
        if not activo:
            return None, "Solo puedo consultar Boom 500, Boom 1000 y GBP/USD."

        symbol_code = MAPEO_DERIV.get(activo)
        try:
            async with websockets.connect(DERIV_WS_URL) as ws:
                await ws.send(json.dumps({"ticks": symbol_code}))
                res = await ws.recv()
                datos = json.loads(res)
                if "tick" in datos:
                    return datos["tick"]["quote"], activo
        except Exception as e:
            logging.error(f"Error en túnel directo de Shane: {e}")
        return None, activo

    async def obtener_historial_velas(self, simbolo: str, timeframe: str = "H1", cantidad: int = 100):
        """Descarga el historial de velas desde Deriv para investigación matemática."""
        activo = validar_y_limpiar_activo(simbolo)
        if not activo:
            return []

        # Mapeo de temporalidades a segundos
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
            logging.error(f"Error obteniendo historial de velas: {e}")
        return []

    # ---------------------------------------------------------
    # MATEMÁTICA Y DIAGNÓSTICO DE FRACTALES Y TIEMPOS
    # ---------------------------------------------------------
    async def medir_fractal_completo(self, simbolo: str, timeframe: str = "H1"):
        """
        Mide el fractal en la temporalidad solicitada:
        - Cantidad de velas en impulso, cima y bajada.
        - Tiempo total transcurrido en horas y días.
        """
        activo = validar_y_limpiar_activo(simbolo)
        if not activo:
            return "Juan, recuerda que solo audito Boom 500, Boom 1000 y GBP/USD."

        tf_minutos = {"M1": 1, "M5": 5, "M15": 15, "M30": 30, "H1": 60, "H4": 240, "D1": 1440}
        minutos_vela = tf_minutos.get(timeframe.upper(), 60)

        velas = await self.obtener_historial_velas(activo, timeframe=timeframe, cantidad=100)
        if not velas:
            return f"No pude obtener la data de velas para {activo} en {timeframe}."

        # Algoritmo de medición matemática de picos y recorridos
        cierre = [v["close"] for v in velas]
        pico_max = max(cierre[-30:])
        idx_pico = cierre[-30:].index(pico_max)
        
        velas_subida = idx_pico
        velas_bajada = len(cierre[-30:]) - idx_pico - 1
        velas_totales = velas_subida + velas_bajada

        minutos_totales = velas_totales * minutos_vela
        horas_totales = minutos_totales / 60
        dias_totales = horas_totales / 24

        tiempo_txt = f"{dias_totales:.1f} días ({horas_totales:.1f} hrs)" if horas_totales >= 24 else f"{horas_totales:.1f} horas"

        return (
            f"📊 **Análisis Fractal en {activo} ({timeframe.upper()}):**\n"
            f"• **Impulso de Subida:** {velas_subida} velas\n"
            f"• **Despliegue/Bajada:** {velas_bajada} velas\n"
            f"• **Total Fractal:** {velas_totales} velas exactas\n"
            f"• **Tiempo Transcurrido:** **{tiempo_txt}**\n\n"
            f"💡 Data matemática procesada directamente desde el historial de Deriv."
        )

    async def diagnosticar_cruces_y_zambullidas(self, simbolo: str, timeframe: str = "M30"):
        """
        Analiza las 'zambullidas' (falsos cruces de limpieza) de las EMAs
        y evalúa la mecha/absorción de la vela Diaria (D1) anterior.
        """
        activo = validar_y_limpiar_activo(simbolo)
        if not activo:
            return "Solo trabajo con Boom 500, Boom 1000 y GBP/USD."

        velas_tf = await self.obtener_historial_velas(activo, timeframe=timeframe, cantidad=50)
        velas_d1 = await self.obtener_historial_velas(activo, timeframe="D1", cantidad=5)

        if not velas_tf or not velas_d1:
            return f"No hay suficiente información técnica en Deriv para auditar {activo}."

        # Lectura de la vela Diaria D1 (Verificar si se 'chupó'/dejó mecha)
        ultima_d1 = velas_d1[-2] if len(velas_d1) >= 2 else velas_d1[-1]
        cuerpo_d1 = abs(ultima_d1["close"] - ultima_d1["open"])
        mecha_inferior_d1 = min(ultima_d1["open"], ultima_d1["close"]) - ultima_d1["low"]
        se_chupo = mecha_inferior_d1 > (cuerpo_d1 * 1.2)

        # Conteo simplificado de fluctuaciones sobre la media (Zambullidas)
        precios = [v["close"] for v in velas_tf]
        ema_rapida = sum(precios[-15:]) / 15
        zambullidas = sum(1 for p in precios[-20:] if abs(p - ema_rapida) / ema_rapida < 0.0005)

        d1_analisis = "La vela Diaria D1 se 'chupó' (gran absorción en mecha inferior)." if se_chupo else "La vela Diaria D1 no muestra absorción extrema."

        return (
            f"🔎 **Auditoría de Cruces y Zambullidas en {activo} ({timeframe}):**\n"
            f"🌊 **Zambullidas/Falsos engaños:** Detectadas {zambullidas} compresiones de limpieza.\n"
            f"🕯️ **Análisis D1:** {d1_analisis}\n\n"
            f"🎯 **Conclusión de Shane:** {'Zona madura. Limpieza efectuada, listo para validar el cruce de toma de tendencia.' if se_chupo else 'Aún evaluando desarrollo de la estructura.'}"
        )

    # ---------------------------------------------------------
    # GESTIÓN DE TAREAS Y COMUNICACIÓN CON TELEGRAM
    # ---------------------------------------------------------
    def registrar_tarea(self, activo: str, instruccion: str):
        act_val = validar_y_limpiar_activo(activo)
        if not act_val:
            return "Solo acepto encargos para Boom 500, Boom 1000 y GBP/USD."
        
        tarea = {"activo": act_val, "instruccion": instruccion, "hora": time.time()}
        self.tareas_personales.append(tarea)
        return f"Anotado Juan. Guardé la tarea de monitoreo para {act_val}: '{instruccion}'."

    def despachar_telegram(self, mensaje: str):
        if bot and CHAT_ID:
            try:
                bot.send_message(CHAT_ID, mensaje, parse_mode="Markdown")
            except Exception as e:
                logging.error(f"Error al enviar mensaje por Telegram: {e}")

shane = CerebroShane()

# ==========================================
# 4. ENDPOINTS FASTAPI (LATIDO 60s Y ALERTAS)
# ==========================================
@app_fastapi.post("/api/heartbeat")
async def recibir_latido():
    """
    Recibe el pulso del motor cada 60 segundos para no quedarse dormido en Render.
    """
    shane.last_heartbeat = time.time()
    num_tareas = len(shane.tareas_personales)
    if num_tareas > 0:
        logging.info(f"Latido de 60s recibido: Shane despierto. Auditando {num_tareas} tarea(s) en agenda.")
    return {"status": "ok", "timestamp": shane.last_heartbeat, "tareas_activas": num_tareas}

@app_fastapi.post("/api/alerta_motor")
async def recibir_alerta_motor(request: Request):
    data = await request.json()
    evento = data.get("evento", "Alerta General")
    detalles = data.get("detalles", "Sin detalle")
    
    shane.memoria.save_context({"input": "ALERTA_MOTOR"}, {"output": f"{evento}: {detalles}"})
    
    notificacion = (
        f"⚡ **ALERTA DEL MOTOR DE TRADING** ⚡\n\n"
        f"📌 **Evento:** {evento}\n"
        f"📊 **Detalles:** {detalles}\n\n"
        f"🤖 *Shane:* Procesado y guardado en memoria."
    )
    shane.despachar_telegram(notificacion)
    return {"status": "recibido"}

# ==========================================
# 5. ATENCIÓN DE MENSANJES Y AUDIO DE JUAN
# ==========================================
def responder_a_juan(mensaje_texto: str):
    texto = mensaje_texto.strip()
    activo = validar_y_limpiar_activo(texto)

    # Identificación de la intención de la consulta
    if "fractal" in texto.lower() or "vela" in texto.lower() or "tiempo" in texto.lower():
        tf = "H1"
        for t in ["M5", "M15", "M30", "H1", "H4", "D1"]:
            if t.lower() in texto.lower():
                tf = t
                break
        target_activo = activo if activo else "BOOM 500"
        return asyncio.run(shane.medir_fractal_completo(target_activo, timeframe=tf))

    elif "zambullida" in texto.lower() or "cruce" in texto.lower() or "ema" in texto.lower():
        tf = "M30"
        for t in ["M5", "M15", "M30", "H1", "H4"]:
            if t.lower() in texto.lower():
                tf = t
                break
        target_activo = activo if activo else "BOOM 500"
        return asyncio.run(shane.diagnosticar_cruces_y_zambullidas(target_activo, timeframe=tf))

    elif "avísame" in texto.lower() or "alerta" in texto.lower() or "tarea" in texto.lower():
        target_activo = activo if activo else "BOOM 500"
        return shane.registrar_tarea(target_activo, texto)

    elif "estado" in texto.lower() or "motor" in texto.lower():
        dif = time.time() - shane.last_heartbeat
        if dif > 120:
            return f"⚠️ Juan, hace {int(dif)} segundos que no recibo el latido del motor. Podría estar desconectado."
        return "✅ El motor principal está corriendo activamente y enviando latidos cada 60 segundos."

    
    else:
        respuesta_final = (
            f"Recibido Juan: {texto}.\n"
            f"Estoy enfocado exclusivamente en BOOM 500, BOOM 1000 y GBP/USD.\n"
            f"Puedes pedirme medir fractales, auditar zambullidas de EMA o registrar tareas."
        )
        
        # Despacho físico blindado (Texto y Voz)
        try:
            if bot and CHAT_ID:
                # 1. Envío físico del texto
                bot.send_message(CHAT_ID, respuesta_final, parse_mode="Markdown")
                
                # 2. Generación y envío físico del audio (Voz) limpio de símbolos
                texto_limpio = respuesta_final.replace("*", "").replace("#", "").replace("_", "")
                tts = gTTS(text=texto_limpio, lang='es')
                audio_path = "respuesta_shane.mp3"
                tts.save(audio_path)
                
                with open(audio_path, 'rb') as audio_file:
                    bot.send_voice(CHAT_ID, voice=audio_file)
                    
                logging.info("Shane respondió físicamente con texto y voz de forma exitosa.")
        except Exception as e:
            logging.error(f"Error crítico en el despacho físico de Shane: {e}")
            
        return respuesta_final

        
            
        
        

# ==========================================
# 6. INICIALIZACIÓN DEL BOT Y SERVIDOR
# ==========================================
# 1. Registrar el evento de arranque en FastAPI
@app_fastapi.on_event("startup")
def iniciar_escucha_telegram():
    def arrancar():
        if bot:
            logging.info("Shane: Escuchador de Telegram activado en segundo plano 24/7.")
            bot.infinity_polling(skip_pending_updates=True)

    thread_tele = threading.Thread(target=arrancar, daemon=True)
    thread_tele.start()

# 2. Inicialización limpia del servidor
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app_fastapi, host="0.0.0.0", port=port)
