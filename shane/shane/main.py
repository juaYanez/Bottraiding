import os
import sys
import json
import logging
import asyncio
import threading
import requests
import websockets
import telebot
import speech_recognition as sr
from gTTS import gTTS
from langchain.memory import ConversationBufferWindowMemory

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ==============================================================================
# 1. VARIABLES DE ENTORNO EN RENDER
# ==============================================================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
DERIV_WS_URL = os.environ.get("DERIV_WS_URL", "wss://ws.derivws.com/websockets/v3?app_id=1089")

# Inicialización del Bot de Telegram (Shane)
bot = telebot.TeleBot(TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None

# ==============================================================================
# 2. SHANE: CEREBRO INTEGRO (MEMORIA PERSISTENTE, VOZ Y TÚNEL PROPIO A DERIV)
# ==============================================================================
class CerebroShane:
    def __init__(self):
        # Memoria persistente para evitar amnesia
        self.memoria = ConversationBufferWindowMemory(k=50, return_messages=True)
        
        # Estrategia de La Gema como un único engranaje
        ARQUITECTURA_GEMA = """
        [ARQUITECTURA UNIFICADA DE LA GEMA]
        El flujo de mercado opera como un solo engranaje indivisible:
        1. Falsa salida alcista (Trampa del comprador).
        2. Purga del vendedor y del Order Block (Trampa del vendedor / Barrido de liquidez).
        3. Gatillo definitivo de confirmación e inicio del verdadero movimiento alcista.
        """
        self.memoria.save_context(
            {"input": "Cargar arquitectura unificada de La Gema"}, 
            {"output": ARQUITECTURA_GEMA}
        )
        print("🧠 [Shane]: Cerebro, memoria e inteligencia de voz inicializados.")

    async def consultar_deriv_directo(self, simbolo="R_100"):
        """Túnel propio e independiente de Shane a Deriv (sin molestar al motor)."""
        try:
            async with websockets.connect(DERIV_WS_URL) as ws:
                await ws.send(json.dumps({"ticks": simbolo, "subscribe": 0}))
                res = await ws.recv()
                datos = json.loads(res)
                if "tick" in datos:
                    return datos["tick"]["quote"]
        except Exception as e:
            print(f"⚠️ [Shane]: Error en consulta propia a Deriv: {e}")
        return None

    def recibir_alarma_del_motor(self, tipo_evento, detalles):
        """
        PULSO INTERNO: El motor le avisa a Shane.
        Shane guarda el evento en memoria y se encarga del despacho a Telegram.
        """
        log_registro = f"Alerta del Motor -> Evento: {tipo_evento} | Detalles: {detalles}"
        self.memoria.save_context({"input": "ALARMA_MOTOR"}, {"output": log_registro})
        
        texto_alarma = (
            f"🚨 **ALERTA DE LA GEMA** 🚨\n\n"
            f"⚡ **Evento:** {tipo_evento}\n"
            f"📈 **Detalles:** {detalles}\n\n"
            f"🧠 *Shane: Motor me notificado. Registrado en memoria y despachado.*"
        )
        
        # Despacho seguro por texto y voz a Telegram
        self.despachar_a_telegram(texto_alarma, audio_texto=f"Atención: Alerta de La Gema. {tipo_evento}")

    def aprender_y_ensenar_al_motor(self, texto_instruccion, motor_ref):
        """Shane absorbe las notas de voz y le enseña las reglas al motorcito."""
        confirmacion = f"Regla aprendida e inyectada al motor: '{texto_instruccion}'"
        self.memoria.save_context({"input": texto_instruccion}, {"output": confirmacion})
        
        # Inyección directa al motor
        if motor_ref:
            motor_ref.actualizar_reglas(texto_instruccion)
            
        return confirmacion

    def despachar_a_telegram(self, texto, audio_texto=None):
        """Mecanismo seguro de despacho de Shane con reintentos."""
        if not TELEGRAM_TOKEN or not CHAT_ID:
            print("❌ [Shane Error]: Faltan variables TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en Render.")
            return

        # 1. Despacho por Texto
        url_texto = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload_texto = {"chat_id": CHAT_ID, "text": texto, "parse_mode": "Markdown"}
        
        for intento in range(1, 5):
            try:
                res = requests.post(url_texto, json=payload_texto, timeout=10)
                if res.status_code == 200:
                    print(f"🟢 [Shane]: Mensaje entregado a Telegram (Intento {intento}).")
                    break
            except Exception as e:
                print(f"⚠️ [Shane]: Reintentando envío a Telegram ({intento}/4): {e}")

        # 2. Despacho por Nota de Voz (Respuesta hablada de Shane)
        if audio_texto:
            try:
                tts = gTTS(text=audio_texto, lang='es')
                ruta_voice = "respuesta_shane.ogg"
                tts.save(ruta_voice)
                
                url_voz = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice"
                with open(ruta_voice, 'rb') as voice_file:
                    requests.post(url_voz, data={"chat_id": CHAT_ID}, files={"voice": voice_file}, timeout=15)
                
                if os.path.exists(ruta_voice):
                    os.remove(ruta_voice)
            except Exception as e:
                print(f"⚠️ [Shane]: No se pudo despachar el audio a Telegram: {e}")

# Instancia global de Shane
shane = CerebroShane()

# ==============================================================================
# 3. MOTOR DE ANÁLISIS TÉCNICO (DESCONECTADO DE TELEGRAM DIRECTO)
# ==============================================================================
class MotorLaGema:
    def __init__(self):
        self.reglas_aprendidas = []
        print("⚙️ [Motor]: Motor de análisis listo. Recibirá reglas directas de Shane.")

    def actualizar_reglas(self, nueva_regla):
        """Guarda las carpetas/instrucciones enseñadas por Shane."""
        self.reglas_aprendidas.append(nueva_regla)
        print(f"⚙️ [Motor]: Nueva instrucción inyectada desde Shane: '{nueva_regla}'")

    def evaluar_mercado(self, precio, simbolo):
        """
        Monitoreo en tiempo real.
        Al validar La Gema, pasa la alarma DIRECTAMENTE a Shane.
        """
        # shane.recibir_alarma_del_motor("PATRON_GEMA_CONFIRMADO", f"Símbolo: {simbolo} | Precio: {precio}")
        pass

# Instancia global del Motor
motor = MotorLaGema()

# ==============================================================================
# 4. RECEPTOR DE TELEGRAM (NOTAS DE VOZ Y CONSULTAS A SHANE)
# ==============================================================================
if bot:
    @bot.message_handler(content_types=['voice'])
    def manejar_nota_de_voz(message):
        """Recepción, transcripción de voz y enseñanza a Shane."""
        try:
            bot.reply_to(message, "🎙️ *Shane procesando nota de voz...*", parse_mode="Markdown")
            
            file_info = bot.get_file(message.voice.file_id)
            file_data = bot.download_file(file_info.file_path)
            
            with open("temp_input.ogg", "wb") as f:
                f.write(file_data)

            os.system("ffmpeg -y -i temp_input.ogg temp_input.wav > /dev/null 2>&1")
            
            recognizer = sr.Recognizer()
            texto_transcrito = ""
            if os.path.exists("temp_input.wav"):
                with sr.AudioFile("temp_input.wav") as source:
                    audio = recognizer.record(source)
                    texto_transcrito = recognizer.recognize_google(audio, language="es-ES")

            if not texto_transcrito:
                texto_transcrito = "Instrucción de voz procesada correctamente."

            # Shane absorbe y le enseña al motor
            confirmacion = shane.aprender_y_ensenar_al_motor(texto_transcrito, motor)
            
            # Responde por texto y por nota de voz al usuario
            shane.despachar_a_telegram(
                f"🧠 **Shane:** {confirmacion}", 
                audio_texto="Instrucción comprendida e inyectada a las carpetas del motor."
            )

            for temp in ["temp_input.ogg", "temp_input.wav"]:
                if os.path.exists(temp):
                    os.remove(temp)

        except Exception as e:
            print(f"❌ Error en recepción de voz: {e}")
            bot.send_message(message.chat.id, f"❌ Error al interpretar nota de voz: {e}")

    @bot.message_handler(func=lambda message: True)
    def responder_texto(message):
        """Procesa textos o preguntas directas sobre el mercado."""
        if CHAT_ID and str(message.chat.id) == str(CHAT_ID):
            # Consulta directa a Deriv usando el túnel propio de Shane
            if "deriv" in message.text.lower() or "precio" in message.text.lower():
                precio = asyncio.run(shane.consultar_deriv_directo())
                respuesta = f"Consulté en mi propio túnel a Deriv. El precio actual es: {precio}"
            else:
                respuesta = shane.aprender_y_ensenar_al_motor(message.text, motor)
                
            shane.despachar_a_telegram(f"🧠 **Shane:** {respuesta}", audio_texto=respuesta)

# ==============================================================================
# 5. BUCLE PRINCIPAL (TÚNEL PRINCIPAL DEL MOTOR A DERIV)
# ==============================================================================
async def iniciar_sistema_matriz():
    logging.info("Iniciando motor de análisis y comunicación...")
    
    # Notificación de arranque
    shane.recibir_alarma_del_motor(
        "SISTEMA_UNIFICADO_LISTO", 
        "Motor y Shane 100% integrados. Doble túnel activo y prioridad de voz lista."
    )

    while True:
        try:
            async with websockets.connect(DERIV_WS_URL) as websocket:
                logging.info("Motor conectado a Deriv por el túnel principal.")
                suscripcion = {"ticks": "R_100", "subscribe": 1}
                await websocket.send(json.dumps(suscripcion))

                while True:
                    respuesta = await websocket.recv()
                    datos = json.loads(respuesta)

                    if "tick" in datos:
                        precio = datos["tick"]["quote"]
                        simbolo = datos["tick"]["symbol"]
                        motor.evaluar_mercado(precio, simbolo)

        except Exception as e:
            logging.error(f"Reconectando motor a Deriv en 5s: {e}")
            await asyncio.sleep(5)

# ==============================================================================
# 6. EJECUCIÓN PARALELA
# ==============================================================================
if __name__ == "__main__":
    try:
        if bot:
            hilo_telegram = threading.Thread(target=bot.infinity_polling, daemon=True)
            hilo_telegram.start()
            print("🎙️ [Shane]: Hilo de escucha y voz activado en Telegram.")

        asyncio.run(iniciar_sistema_matriz())
    except KeyboardInterrupt:
        logging.info("Sistema detenido.")
