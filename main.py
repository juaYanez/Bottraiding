import datetime
import os
import requests

# =====================================================================
# CONFIGURACIÓN DE TELEGRAM Y CONEXIÓN
# =====================================================================
TOKEN = "8819113948:AAGn6QUsM-ZFsROMBqi5CJ1DOFWDqA1AKvs"
CHAT_ID = "8687968442"

def enviar_alerta_completa(mensaje_texto):
    """
    Envía la alerta de forma dual: por texto formateado y por audio (voz)
    para que puedas escucharla mientras manejas.
    """
    # 1. Enviar mensaje de texto
    url_text = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje_texto, "parse_mode": "HTML"}
    try:
        requests.post(url_text, data=payload)
    except Exception as e:
        print(f"Error enviando texto a Telegram: {e}")
    
    # 2. Generar y enviar audio (Voz)
    try:
        texto_limpio = (
            mensaje_texto.replace("<b>", "")
                         .replace("</b>", "")
                         .replace("🚀", "")
                         .replace("📊", "")
                         .replace("<br>", " ")
        )
        tts = gTTS(text=texto_limpio, lang='es')
        audio_path = "alerta.mp3"
        tts.save(audio_path)
        
        url_audio = f"https://api.telegram.org/bot{TOKEN}/sendAudio"
        with open(audio_path, "rb") as audio:
            requests.post(url_audio, data={"chat_id": CHAT_ID}, files={"audio": audio})
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except Exception as e:
        print(f"Error enviando audio a Telegram: {e}")


# =====================================================================
# FASE 1: AVISO DE INICIO DE MES (ORDER BLOCK MENSUAL)
# =====================================================================
def verificar_inicio_de_mes():
    """
    Detecta el preciso instante en que cambia al día 1 del mes a las 00:01 UTC
    para avisarte que traces tu bloque de órdenes mensual.
    """
    ahora = datetime.datetime.utcnow()
    if ahora.day == 1 and ahora.hour == 0 and ahora.minute == 1:
        mensaje = f"🚀 <b>¡Comienzo de nuevo mes!</b> Día {ahora.day}. Es hora de trazar tu Order Block mensual."
        enviar_alerta_completa(mensaje)


# =====================================================================
# FASE 2: GATILLO DE LOS PRIMEROS 5 DÍAS (CASCADA M30)
# =====================================================================
def evaluar_gatillo_dias_iniciales(m1_cruzo, m5_cruzo, m15_cruzo, ema15_m30, ema50_m30, activo):
    """
    Durante los primeros 5 días del mes, valida la cascada (M1 -> M5 -> M15)
    y utiliza M30 como el gatillo definitivo cuando va a cruzar la EMA 50.
    """
    ahora = datetime.datetime.utcnow()
    if not (1 <= ahora.day <= 5):
        return  # Si pasan los 5 días, se desactiva esta búsqueda.

    menores_confirmadas = m1_cruzo and m5_cruzo and m15_cruzo
    distancia_m30 = abs(ema15_m30 - ema50_m30)
    umbral_proximidad = 0.0008  # Margen milimétrico antes del choque

    if menores_confirmadas and distancia_m30 <= umbral_proximidad and ema15_m30 < ema50_m30:
        mensaje = (
            f"🚀 <b>¡GATILLO MAESTRO ACTIVADO ({activo})!</b><br>"
            "M1, M5 y M15 ya cruzaron al alza. M30 está chocando para atravesar la EMA 50. "
            "<b>¡Comienza el verdadero movimiento alcista!</b>"
        )
        enviar_alerta_completa(mensaje)


# =====================================================================
# FASE 3: MAPA FRACTAL DE 6 TEMPORALIDADES Y GESTIÓN DE ENTRADA/PARCIALES
# =====================================================================
def evaluar_ciclo_fractal(temporalidad, activo, precio_actual, ema15_valor, en_la_cima=False, minutos_para_tocar_piso=None):
    """
    Monitorea el fractal en cualquier temporalidad (M30, H1, H4, Diaria, Semanal, Mensual)
    para los activos (Boom 500, Boom 1000, GBP USD):
    1. Avisa cuando llega arriba ('guatita' superior) para sacar parciales.
    2. Avisa exactamente media hora antes (30 min) de que el precio vuelva a tocar el piso de la EMA 15.
    """
    
    # Condición 1: El precio llegó arriba al cerro (Tomar Parciales)
    if en_la_cima:
        mensaje = f"📊 <b>TECHO DE FRACTAL ({activo} - {temporalidad}):</b> El precio hizo la guatita arriba. <b>¡Saca parciales!</b>"
        enviar_alerta_completa(mensaje)
        return

    # Condición 2: El precio viene de vuelta y avisar media hora antes de tocar el piso de la EMA 15
    if minutos_para_tocar_piso is not None and minutos_para_tocar_piso <= 30:
        mensaje = (
            f"📊 <b>AVISO DE ENTRADA PRÓXIMA ({activo} - {temporalidad}):</b><br>"
            f"Faltan aproximadamente {minutos_para_tocar_piso} minutos para que el precio toque el piso de la EMA 15. "
            "<b>Prepárate para colocar tu nueva entrada alcista.</b>"
        )
        enviar_alerta_completa(mensaje)


# =====================================================================
# MOTOR PRINCIPAL DE EJECUCIÓN
# =====================================================================
if __name__ == "__main__":
    print("Motorcito de trading optimizado y conectado à Telegram iniciado correctamente.")
    enviar_alerta_completa("<b>Motorcito operativo:</b> Sistema actualizado con Telegram, voz y reglas matemáticas listo en Render.")
