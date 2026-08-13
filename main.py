import datetime
import os
import requests
import time
from gtts import gTTS

# ==============================================================================
# CONFIGURACIÓN DE TELEGRAM Y CONEXIÓN
# ==============================================================================
TOKEN = "8819113948:AAGn6QUsM-ZFsR0MBqi5CJ1DOFWDqA1AKvs"
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

# ==============================================================================
# MÓDULO ESCÁNER DE AUDITORÍA CIEGA (Escucha tu comando)
# ==============================================================================
def obtener_ultimo_comando():
    """Revisa si enviaste un mensaje desde Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1"
    try:
        res = requests.get(url).json()
        if 'result' in res and len(res['result']) > 0:
            msg = res['result'][0]['message']
            if str(msg['chat']['id']) == str(CHAT_ID):
                return msg.get('text', '').strip().lower()
    except Exception as e:
        print(f"Error leyendo comandos: {e}")
    return ""

def ejecutar_escaner_auditoria(activo="Boom / USD", ema15_m30=0, ema50_m30=0, m1_cruzo=False, m5_cruzo=False, m15_cruzo=False, umbral=0.0008):
    """
    Escáner de memoria en vivo: Muestra la radiografía matemática exacta
    para ver en qué punto de la lógica se detiene o si pasa de largo.
    """
    ahora = datetime.datetime.utcnow()
    distancia_m30 = abs(ema15_m30 - ema50_m30)
    
    regla_dias = 1 <= ahora.day <= 5
    regla_distancia = distancia_m30 <= umbral
    regla_menores = m1_cruzo and m5_cruzo and m15_cruzo

    reporte = (
        f"🧪 <b>AUDITORÍA MATEMÁTICA EN VIVO ({activo})</b>\n"
        f"<i>Fecha/Hora Servidor: {ahora.strftime('%Y-%m-%d %H:%M:%S')} UTC</i>\n"
        f"----------------------------------------\n"
        f"<b>1. FILTRO DÍAS INICIALES (1 al 5):</b>\n"
        f"• Día actual del servidor: {ahora.day}\n"
        f"• ¿Aprobado?: {'✅ SÍ' if regla_dias else '❌ NO (Frena evaluación aquí)'}\n\n"
        
        f"<b>2. DISTANCIA M30:</b>\n"
        f"• Resta |EMA15 - EMA50|: <b>{distancia_m30:.6f}</b>\n"
        f"• Umbral exigido: <= {umbral}\n"
        f"• ¿Aprobado?: {'✅ SÍ' if regla_distancia else '❌ NO (Supera umbral)'}\n\n"
        
        f"<b>3. CRUCE MENORES (M1, M5, M15):</b>\n"
        f"• M1: {'✅' if m1_cruzo else '❌'} | M5: {'✅' if m5_cruzo else '❌'} | M15: {'✅' if m15_cruzo else '❌'}\n"
        f"• ¿Aprobado?: {'✅ SÍ' if regla_menores else '❌ NO (Falta confirmación)'}\n\n"
        f"----------------------------------------\n"
        f"<b>DIAGNOSTICO DEL MOTOR:</b>\n"
    )

    if regla_dias and regla_distancia and regla_menores:
        reporte += "🟢 Toda la matemática fue CUMPLIDA. El gatillo debe disparar la alerta."
    else:
        reporte += "🔴 El motor evaluó la fórmula, pero una condición no se cumple. Pasa de largo intencionalmente."

    enviar_alerta_completa(reporte)

# ==============================================================================
# FASE 1: AVISO DE INICIO DE MES (ORDER BLOCK MENSUAL)
# ==============================================================================
def verificar_inicio_de_mes():
    ahora = datetime.datetime.utcnow()
    if ahora.day == 1 and ahora.hour == 0 and ahora.minute == 1:
        mensaje = f"🚀 <b>¡Comienzo de nuevo mes!</b> Día {ahora.day}. Es hora de trazar tu Order Block mensual."
        enviar_alerta_completa(mensaje)

# ==============================================================================
# FASE 2: GATILLO DE LOS PRIMEROS 5 DÍAS (CASCADA M30)
# ==============================================================================
def evaluar_gatillo_dias_iniciales(m1_cruzo, m5_cruzo, m15_cruzo, ema15_m30, ema50_m30, activo="Activo"):
    ahora = datetime.datetime.utcnow()
    if not (1 <= ahora.day <= 5):
        return

    menores_confirmadas = m1_cruzo and m5_cruzo and m15_cruzo
    distancia_m30 = abs(ema15_m30 - ema50_m30)
    umbral_proximidad = 0.0008

    if menores_confirmadas and distancia_m30 <= umbral_proximidad and ema15_m30 > ema50_m30:
        mensaje = (
            f"🚀 <b>¡GATILLO MAESTRO ACTIVADO ({activo})!</b><br>"
            "M1, M5 y M15 ya cruzaron al alza. M30 está chocando para atravesar la EMA 50.<br>"
            "<b>¡Comienza el verdadero movimiento alcista!</b>"
        )
        enviar_alerta_completa(mensaje)

# ==============================================================================
# FASE 3: MAPA FRACTAL Y GESTIÓN DE ENTRADA/PARCIALES
# ==============================================================================
def evaluar_ciclo_fractal(temporalidad, activo, precio_actual, ema15_valor, en_la_cima=False, minutos_para_tocar_piso=None):
    if en_la_cima:
        mensaje = f"📊 <b>TECHO DE FRACTAL ({activo} - {temporalidad}):</b> El precio hizo la guatita arriba. <b>¡Saca parciales!</b>"
        enviar_alerta_completa(mensaje)
        return

    if minutos_para_tocar_piso is not None and minutos_para_tocar_piso <= 30:
        mensaje = (
            f"📊 <b>AVISO DE ENTRADA PRÓXIMA ({activo} - {temporalidad}):</b><br>"
            f"Faltan aproximadamente {minutos_para_tocar_piso} minutos para que el precio toque el piso de la EMA 15.<br>"
            "<b>Prepárate para colocar tu nueva entrada alcista.</b>"
        )
        enviar_alerta_completa(mensaje)

# ==============================================================================
# MOTOR PRINCIPAL (Con bucle de seguridad para Render)
# ==============================================================================
if __name__ == "__main__":
    print("Motorcito de trading completo y optimizado iniciado correctamente.")
    enviar_alerta_completa("<b>Motorcito operativo:</b> Sistema completo en línea y sincronizado.")

    while True:
        # 1. Escucha pasiva: Revisa si le envías el comando 'escanear' desde Telegram
        comando = obtener_ultimo_comando()
        if comando == "escanear":
            ejecutar_escaner_auditoria()

        # 2. Rutina normal del motor
        verificar_inicio_de_mes()
        
        # Pausa de 5 minutos entre verificaciones
        time.sleep(300)
