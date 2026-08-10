# 
import asyncio
# 2. EL CORAZÓN DEL SISTEMA: ALARMA 1 HORA ANTES (EMA 15 / 15.5)
# =====================================================================
class MotorFractalJuanTrech:
    """
    SISTEMA FRACTAL BIDIRECCIONAL - JUAN TRECH
    
    Regla Maestra:
    - Alcista: Sube el cerro y baja (hace la contra) a buscar la EMA 15 (15.5).
    - Bajista: Va en picada abajo y sube (hace la contra) a buscar la EMA 15 (15.5) que viene atrás.
    
    El motor envía la alarma exclusivamente cuando falta 1 HORA para el toque de bencina
    en las 6 temporalidades: Mensual, Semanal, Diario, H4, H1, M30.
    """
    def __init__(self):
        self.temporalidades = ["Mensual", "Semanal", "Diario", "H4", "H1", "M30"]
        self.activos = os.envron.get("ACTIVOS").split(",")
        self.ultimos_precios = {activo: 0.0 for activo in self.activos}
        
        # Historial de precios por activo y temporalidad
        self.historico_precios = {activo: {t: [] for t in self.temporalidades} for activo in self.activos}

        # Control de disparo único de alarma por activo y temporalidad
        self.alarma_enviada = {
            activo: {t: False for t in self.temporalidades} for activo in self.activos
        }

    def calcular_ema(self, precios, periodo):
        """ Cálculo dinámico de la EMA 15.5 """
        if len(precios) < int(periodo):
            return None
        k = 2 / (periodo + 1)
        ema = sum(precios[:int(periodo)]) / int(periodo)
        for precio in precios[int(periodo):]:
            ema = (precio * k) + (ema * (1 - k))
        return ema

    async def evaluar_fractalidad_completa(self, bot: Bot, activo, precio_actual):
        self.ultimos_precios[activo] = precio_actual

        for t in self.temporalidades:
            precios_t = self.historico_precios[activo][t]
            precios_t.append(precio_actual)
            if len(precios_t) > 100:
                precios_t.pop(0)

            # Cálculo de la EMA 15.5 (Punto de bencina)
            ema15_5 = self.calcular_ema(precios_t, 15.5)

            if not ema15_5:
                continue

            # Distancia absoluta en pips (funciona igual si el precio está arriba o abajo)
            distancia_pips = abs(precio_actual - ema15_5) * 10000
            
            # Estimación de tiempo a la EMA (1 hora = 60 min aprox)
            minutos_para_tocar = distancia_pips / 0.5

            # DETERMINAR LA DIRECCIÓN DE LA CONTRA
            if precio_actual > ema15_5:
                tipo_movimiento = "Buscando bencina desde arriba (Cerro Alcista)"
            else:
                tipo_movimiento = "Haciendo la contra desde abajo (Picada Bajista)"

            # REGLA ÚNICA: AVISAR EXACTAMENTE 1 HORA ANTES
            if 50 <= minutos_para_tocar <= 70 and not self.alarma_enviada[activo][t]:
                self.alarma_enviada[activo][t] = True
                msg = (
                    f"⏰ **[ALERTA NUBE - JUAN TRECH]**\n\n"
                    f"📊 **Activo:** `{activo}`\n"
                    f"📍 **Temporalidad:** `{t}`\n"
                    f"🔄 **Movimiento:** {tipo_movimiento}\n"
                    f"⛽ **Análisis:** Falta **1 HORA** para llegar a tomar bencina a la **EMA 15 (15.5)**."
                )
                await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

            # Reset cuando el precio se aleja de la zona de toma de bencina
            if distancia_pips > 30:
                self.alarma_enviada[activo][t] = False

motor_fractal = MotorFractalJuanTrech()
import json
import logging
import os
import requests
import websockets
from datetime import datetime
from gtts import gTTS

# ==============================================================================
# 1. CONFIGURACIÓN DE CREDENCIALES Y ENTORNO
# ==============================================================================
TELEGRAM_TOKEN = "8819113948:AAGn6QUsM-ZFsROMBqi5CJ1DOFWDqA1AKvs"
TELEGRAM_CHAT_ID = "8687968442"

DERIV_APP_ID = os.getenv("DERIV_APP_ID", "1089")
DERIV_WS_URL = f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ==============================================================================
# 2. MÓDULO DE COMUNICACIÓN POR VOZ Y TEXTO (TELEGRAM)
# ==============================================================================
def enviar_telegram_texto(mensaje: str):
    """Envía mensaje de texto a Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando texto a Telegram: {e}")

def enviar_telegram_voz(texto_mensaje: str):
    """Convierte el mensaje a voz (.ogg) y lo envía a Telegram para manos libres"""
    archivo_audio = "alerta_voz.ogg"
    try:
        texto_limpio = (
            texto_mensaje.replace("*", "")
            .replace("`", "")
            .replace("🚨", "")
            .replace("📌", "")
            .replace("⚠️", "")
        )
        
        tts = gTTS(text=texto_limpio, lang='es')
        tts.save(archivo_audio)

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVoice"
        with open(archivo_audio, 'rb') as audio:
            payload = {"chat_id": TELEGRAM_CHAT_ID}
            files = {"voice": audio}
            requests.post(url, data=payload, files=files, timeout=15)
            
    except Exception as e:
        print(f"Error enviando voz a Telegram: {e}")
    finally:
        if os.path.exists(archivo_audio):
            os.remove(archivo_audio)

def enviar_alerta_completa(mensaje: str):
    """Función unificada para enviar tanto texto como nota de voz a tu Telegram"""
    enviar_telegram_texto(mensaje)
    enviar_telegram_voz(mensaje)

# ==============================================================================
# 3. NÚCLEO ESPECIALIZADO: EMAs, ZAMBULLIDAS Y CICLOS FRACTALES
# ==============================================================================
class NucleoFractalEMAs:
    def __init__(self):
        # Registro de velocidad de vueltas y conteo de velas por temporalidad
        self.temporalidades = ["M30", "H1", "H4", "DIARIO", "SEMANAL", "MENSUAL"]
        self.memoria_ciclos = {tf: {"velas_subida": 0, "velas_bajada": 0, "zambullidas": 0} for tf in self.temporalidades}

    def actualizar_conteo_velas(self, timeframe: str, es_subida: bool, zambullida_detectada: bool):
        """
        Cuenta las velas que suben el cerro y las que bajan, midiendo 
        las zambullidas específicas de la temporalidad.
        """
        if timeframe in self.memoria_ciclos:
            if es_subida:
                self.memoria_ciclos[timeframe]["velas_subida"] += 1
            else:
                self.memoria_ciclos[timeframe]["velas_bajada"] += 1
            
            if zambullida_detectada:
                self.memoria_ciclos[timeframe]["zambullidas"] += 1

    def evaluar_cruce_y_vueltas_emas(self, activo: str, timeframe: str, ema1: float, ema5: float, ema15: float):
        """
        Compara las vueltas relativas entre EMA 1, EMA 5 y EMA 15, 
        evaluando la fuerza de la tendencia y el cruce clave de M30 directo a H1.
        """
        datos_tf = self.memoria_ciclos.get(timeframe, {"velas_subida": 0, "velas_bajada": 0, "zambullidas": 0})
        
        # Análisis de velocidad: EMA 1 da más vueltas que la EMA 5, y la EMA 5 más que la EMA 15
        diferencia_rapida = abs(ema1 - ema5)
        diferencia_lenta = abs(ema5 - ema15)

        if diferencia_rapida > diferencia_lenta * 1.5:
            mensaje = (
                f"🚨 MATRIZ FRACTAL - EMA Y CICLOS [{activo}]\n"
                f"Temporalidad clave: {timeframe}\n"
                f"Conteo actual -> Subidas: {datos_tf['velas_subida']} | Bajadas: {datos_tf['velas_bajada']}\n"
                f"Zambullidas acumuladas: {datos_tf['zambullidas']}\n"
                f"⚠️ *Análisis de Vueltas:* La EMA rápida lidera el ciclo. Evaluando purga, falsa salida y consolidación hacia H1."
            )
            enviar_alerta_completa(mensaje)

# Instancia del núcleo fractal avanzado
cerebro_fractal = NucleoFractalEMAs()

# ==============================================================================
# 4. CONEXIÓN EN TIEMPO REAL CON DERIV
# ==============================================================================
async def iniciar_sistema_matriz():
    logging.info("Iniciando motor con especialización de EMAs y ciclos fractales...")

    enviar_alerta_completa(
        "Sistema fractal de EMAs y conteo de velas iniciado en la nube. Monitoreando ciclos desde M30 hasta mensual."
    )

    while True:
        try:
            async with websockets.connect(DERIV_WS_URL) as websocket:
                logging.info("Conectado al WebSocket de Deriv.")
                suscripcion = {"ticks": "R_100", "subscribe": 1}
                await websocket.send(json.dumps(suscripcion))

                while True:
                    respuesta = await websocket.recv()
                    datos = json.loads(respuesta)

                    if "tick" in datos:
                        precio = datos["tick"]["quote"]
                        simbolo = datos["tick"]["symbol"]
                        # Procesamiento continuo de las EMAs y fractalidad

        except Exception as e:
            logging.error(f"Error de conexión: {e}. Reintentando en 5 segundos...")
            await asyncio.sleep(5)

# ==============================================================================
# 5. EJECUCIÓN PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    try:
        asyncio.run(iniciar_sistema_matriz())
    except KeyboardInterrupt:
        logging.info("Sistema detenido.")
