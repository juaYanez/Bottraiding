from datetime import datetime
import os
import requests
import time
from gtts import gTTS

# ==============================================================================
# CONFIGURACIÓN DE TELEGRAM Y CONEXIÓN
# ==============================================================================
TOKEN = "8819113948:AAGn6QUsM-ZFsR0NBqi5CJ1DOFWDqA1AKvs"
CHAT_ID = "8687968442"

def enviar_alerta_completa(mensaje_texto):
    """
    Envía la alerta de forma dual: por texto formateado y por audio (voz).
    """
    # 1. Enviar mensaje de texto
    url_text = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje_texto, "parse_mode": "HTML"}
    try:
        requests.post(url_text, data=payload, timeout=10)
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
                         .replace("<i>", "")
                         .replace("</i>", "")
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


# ==============================================================================
# MÓDULO ESCÁNER DE AUDITORÍA CIEGA
# ==============================================================================
ultimo_update_id = None

def obtener_ultimo_comando():
    """Revisa si enviaste un mensaje desde Telegram sin romper el bot."""
    global ultimo_update_id
    
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 1, "limit": 1}
    if ultimo_update_id is not None:
        params["offset"] = ultimo_update_id + 1

    try:
        res = requests.get(url, params=params, timeout=5).json()
        if 'result' in res and len(res['result']) > 0:
            last_update = res['result'][0]
            ultimo_update_id = last_update['update_id']
            
            msg = last_update.get('message', {})
            chat_id = msg.get('chat', {}).get('id')
            
            if str(chat_id) == str(CHAT_ID):
                texto = msg.get('text', '')
                return texto.strip().lower() if texto else ""
    except Exception as e:
        print(f"Error leyendo comandos: {e}")
    return ""


def ejecutar_escanear_auditoria(activo="Boom / USD", ema15_m30=0.0, ema50_m30=0.0, m1_cruzo=False, m5_cruzo=False, m15_cruzo=False, umbral=0.0008):
    ahora = datetime.utcnow()
    distancia_m30 = abs(ema15_m30 - ema50_m30)

    regla_dias = 1 <= ahora.day <= 5
    regla_distancia = distancia_m30 <= umbral
    regla_menores = m1_cruzo and m5_cruzo and m15_cruzo

    reporte = (
        f"<b>AUDITORÍA MATEMÁTICA EN VIVO ({activo})</b>\n"
        f"<i>Fecha/Hora Servidor: {ahora.strftime('%Y-%m-%d %H:%M:%S')} UTC</i>\n"
        f"----------------------------------------\n"
        f"<b>1. FILTRO DÍAS INICIALES (1 al 5):</b>\n"
        f"Día actual del servidor: {ahora.day}\n"
        f"¿Aprobado?: {'✅ SÍ' if regla_dias else '❌ NO (Frena evaluación)'}\n\n"
        f"<b>2. DISTANCIA M30:</b>\n"
        f"Resta |EMA15 - EMA50|: {distancia_m30:.6f}\n"
        f"Umbral exigido: <= {umbral}\n"
        f"¿Aprobado?: {'✅ SÍ' if regla_distancia else '❌ NO (Supera umbral)'}\n\n"
        f"<b>3. CRUCE MENORES (M1, M5, M15):</b>\n"
        f"M1: {'✅' if m1_cruzo else '❌'} | M5: {'✅' if m5_cruzo else '❌'} | M15: {'✅' if m15_cruzo else '❌'}\n"
        f"¿Aprobado?: {'✅ SÍ' if regla_menores else '❌ NO (Falta confirmar)'}\n"
        f"----------------------------------------\n"
        f"<b>DIAGNÓSTICO DEL MOTOR:</b>\n"
    )

    if regla_dias and regla_distancia and regla_menores:
        reporte += "🟢 Toda la matemática fue CUMPLIDA. El gatillo debe sonar."
    else:
        reporte += "🔴 El motor evaluó la fórmula, pero una condición no se cumple."

    enviar_alerta_completa(reporte)


# ==============================================================================
# FASE 1: AVISO DE INICIO DE MES
# ==============================================================================
def verificar_inicio_de_mes():
    ahora = datetime.utcnow()
    if ahora.day == 1 and ahora.hour == 0 and ahora.minute == 1:
        mensaje = f"🚀 <b>Comienzo de nuevo mes!</b> Día {ahora.day}. Evalúa el Order Block Mensual."
        enviar_alerta_completa(mensaje)


# ==============================================================================
# FASE 2: GATILLO DE LOS PRIMEROS 5 DÍAS
# ==============================================================================
def evaluar_gatillo_dias_iniciales(m1_cruzo, m5_cruzo, m15_cruzo, ema15_m30, ema50_m30, activo="Boom / USD"):
    ahora = datetime.utcnow()
    if not (1 <= ahora.day <= 5):
        return

    menores_confirmadas = m1_cruzo and m5_cruzo and m15_cruzo
    distancia_m30 = abs(ema15_m30 - ema50_m30)
    umbral_proximidad = 0.0008

    if menores_confirmadas and distancia_m30 <= umbral_proximidad:
        mensaje = (
            f"🚀 <b>GATILLO MAESTRO ACTIVADO ({activo})!</b><br>"
            f"M1, M5 y M15 ya cruzaron al alza. M30 está chocando para atrapar.<br>"
            f"<b>¡Comienza el verdadero movimiento alcista!</b>"
        )
        enviar_alerta_completa(mensaje)


# ==============================================================================
# FASE 3: MAPA FRACTAL Y GESTIÓN DE ENTRADA
# ==============================================================================
def evaluar_ciclo_fractal(temporalidad, activo, precio_actual, ema15_val, ema50_val, en_la_cima=False, minutos_para_tocar_piso=None):
    if en_la_cima:
        mensaje = f"📊 <b>TECHO DE FRACTAL ({activo} - {temporalidad}):</b> Precio en la cima."
        enviar_alerta_completa(mensaje)
        return

    if minutos_para_tocar_piso is not None and minutos_para_tocar_piso <= 5:
        mensaje = (
            f"📊 <b>AVISO DE ENTRADA PRÓXIMA ({activo} - {temporalidad})</b><br>"
            f"Faltan aproximadamente {minutos_para_tocar_piso} minutos para tocar el piso de la EMA.<br>"
            f"<b>Prepárate para colocar tu nueva entrada alcista.</b>"
        )
        enviar_alerta_completa(mensaje)


# ==============================================================================
# MOTOR PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    print("Motorcito de trading completo iniciado...")
    enviar_alerta_completa("<b>Motorcito operativo:</b> Sistema completo y escuchando comandos.")

    contador_rutina = 0
    activo_actual = "Boom 1000 / USD"
    ema15_m30_actual = 0.0
    ema50_m30_actual = 0.0
    m1_cruzo_actual = False
    m5_cruzo_actual = False
    m15_cruzo_actual = False

    while True:
        try:
            # 1. Escucha rápida a Telegram (cada 3 segundos)
            comando = obtener_ultimo_comando()
            
            if comando and any(palabra in comando for palabra in ["escanear", "scanear", "scanner", "escaneo"]):
                ejecutar_escanear_auditoria(
                    activo=activo_actual,
                    ema15_m30=ema15_m30_actual,
                    ema50_m30=ema50_m30_actual,
                    m1_cruzo=m1_cruzo_actual,
                    m5_cruzo=m5_cruzo_actual,
                    m15_cruzo=m15_cruzo_actual
                )

            # 2. Rutinas secundarias periódicas
            contador_rutina += 1
            if contador_rutina >= 100:
                verificar_inicio_de_mes()
                contador_rutina = 0

            time.sleep(3)

        except Exception as e:
            print(f"Error en el bucle principal: {e}")
            time.sleep(5)
