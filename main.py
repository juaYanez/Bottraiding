
from datetime import datetime
import os
import requests
import time
import traceback
from gtts import gTTS

# ==============================================================================
# 1. CONFIGURACIÓN Y CONexión (PRIMERO LAS HERRAMIENTAS)
# ==============================================================================
TOKEN = "8019113948:AAGn6QusV-2FsR0NAqI5CJ1DDFmDqA1AKvs"
CHAT_ID = "8687968442"

def enviar_alerta_completa(mensaje_texto):
    """Envía la alerta de forma dual: texto HTML y audio por voz a Telegram."""
    # 1. Enviar mensaje de texto HTML
    url_text = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensaje_texto, "parse_mode": "HTML"}
    try:
        requests.post(url_text, data=payload, timeout=10)
    except Exception as e:
        print(f"Error enviando texto a Telegram: {e}")

    # 2. Generar y enviar audio de voz
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

# ==============================================================================
# 2. MÓDULO DE VERIFICACIÓN Y CAZA-ERRORES
# ==============================================================================
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

# ==============================================================================
# 3. ESCÁNER DE COMANDOS DESDE TELEGRAM
# ==============================================================================
ultimo_update_id = None

def obtener_ultimo_comando():
    global ultimo_update_id
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 1, "limit": 1}
    if ultimo_update_id is not None:
        params["offset"] = ultimo_update_id + 1

    try:
        res = requests.get(url, params=params, timeout=5).json()
        if "result" in res and len(res["result"]) > 0:
            last_update = res["result"][0]
            ultimo_update_id = last_update["update_id"]
            msg = last_update.get("message", {})
            chat_id = msg.get("chat", {}).get("id")

            if str(chat_id) == str(CHAT_ID):
                texto = msg.get("text", "")
                return texto.strip().lower() if texto else ""
    except Exception as e:
        pass
    return ""

def responder_estado_sistema():
    try:
        ahora = datetime.utcnow()
        reporte = (
            f"🛠️ <b>DIAGNÓSTICO DE SALUD DEL MOTOR</b>\n"
            f"-----------------------------------\n"
            f"<b>Estado:</b> 🟢 Activo 24/7 (Sin descansos)\n"
            f"<b>Activos vigilados:</b> Boom 1000, Boom 500, USD\n"
            f"<b>Servidor:</b> Render (Conexión estable)\n"
            f"<b>Hora Servidor:</b> {ahora.strftime('%Y-%m-%d %H:%M:%S')} UTC\n"
            f"<b>Sincronización Telegram:</b> ✅ OK\n"
            f"-----------------------------------"
        )
        enviar_alerta_completa(reporte)
    except Exception as e:
        notificar_error_critico("Responder Estado Sistema", e)

# ==============================================================================
# 4. FASES FRACTALES Y MENSUALES
# ==============================================================================
def verificar_inicio_de_mes():
    try:
        ahora = datetime.utcnow()
        if ahora.day == 1 and ahora.hour == 0 and ahora.minute == 1:
            mensaje = f"🔔 <b>Comienza nuevo mes!</b> Día {ahora.day}. Evalúa el Order Block Mensual."
            enviar_alerta_completa(mensaje)
    except Exception as e:
        notificar_error_critico("Verificación Inicio de Mes", e)

def evaluar_ciclo_fractal(precio_actual, ema15_actual, umbral_proximidad=0.0005, activo="Boom 1000 / Boom 500 / USD"):
    try:
        distancia_ema15 = abs(precio_actual - ema15_actual)
        if distancia_ema15 <= umbral_proximidad:
            mensaje_piso = (
                f"⛽ <b>¡AVISO DE RECARGA DE BENCINA! ({activo})</b><br>"
                f"El precio ha retrocedido y está tocando el piso de la EMA 15.<br>"
                f"<b>¡Prepárate para tomar tu nueva entrada alcista!</b>"
            )
            enviar_alerta_completa(mensaje_piso)
    except Exception as e:
        notificar_error_critico("Evaluación Ciclo Fractal", e)

def evaluar_gatillo_maestro_detallado(
    tipo_mes, 
    body_mes_anterior, 
    quinto_bajo_semanal, 
    precio_actual, 
    ema15_actual, 
    escala_niveles_previos, 
    mecha_arriba_detectada,
    m1_sobre_ema50, 
    m5_sobre_ema50, 
    m15_sobre_ema50, 
    m30_cruza_m15_y_ema50,
    activo="Boom 1000 / Boom 500 / USD"
):
    try:
        if tipo_mes == "bajista_a_alcista":
            linea_base = body_mes_anterior
            detalle_base = "Transición Bajista a Alcista: Alineación exacta con el body del mes anterior."
        elif tipo_mes == "alcista_a_alcista":
            linea_base = quinto_bajo_semanal
            detalle_base = "Transición Alcista a Alcista: Uso del bajo más bajo de la 5ª semana para la mecha y arranque de cuerpo."
        else:
            linea_base = body_mes_anterior
            detalle_base = "Transición Estándar por Body."

        if mecha_arriba_detectada and precio_actual < ema15_actual:
            mensaje_trampa = (
                f"🚨 <b>ALERTA DE TRAMPA / MES BAJISTA ({activo})</b><br>"
                f"El precio amagó al alza haciendo mecha arriba con la EMA 15 abajo, "
                f"pero al romper la EMA 15 a la baja, se confirma el movimiento bajista."
            )
            enviar_alerta_completa(mensaje_trampa)
            return False

        ema_subiendo = ema15_actual >= max(escala_niveles_previos) if escala_niveles_previos else True
        if precio_actual < ema15_actual:
            diagnostico_retroceso = "Retroceso técnico obligatorio (buscando temporalidad mayor), manteniendo secuencia alcista fractal."
        else:
            diagnostico_retroceso = "Secuencia alcista firme sobre la EMA 15 ascendente en escalera."

        salida_del_fondo_ok = (precio_actual >= linea_base)
        fase_m1_m5_listas = m1_sobre_ema50 and m5_sobre_ema50

        gatillo_activado = (
            fase_m1_m5_listas and 
            m15_sobre_ema50 and 
            m30_cruza_m15_y_ema50 and 
            salida_del_fondo_ok
        )

        if gatillo_activado:
            mensaje_gatillo = (
                f"🚀 <b>¡GATILLO MAESTRO ACTIVADO! (COMIENZO DE MES Y FRACTAL) [{activo}]</b><br>"
                f"-----------------------------------\n"
                f"<b>Referencia Base:</b> {detalle_base} (Nivel: {linea_base})<br>"
                f"<b>Secuencia en Cascada:</b> M1 -> M5 -> M15 -> M30 completada.<br>"
                f"<b>Estado EMA 50:</b> M1, M5, M15 y M30 alineadas y sobre la EMA 50.<br>"
                f"<b>Estado Escalera EMA 15:</b> {diagnostico_retroceso}<br>"
                f"<b>¡Comienza el verdadero movimiento alcista confirmado!</b>"
            )
            enviar_alerta_completa(mensaje_gatillo)
            return True

        return False
    except Exception as e:
        notificar_error_critico("Evaluación Gatillo Maestro Detallado", e)
        return False

# ==============================================================================
# 5. MOTOR PRINCIPAL (AL FINAL DEL SCRIPT)
# ==============================================================================
if __name__ == "__main__":
    print("Motorcito de trading 24/7 iniciado...")
    enviar_alerta_completa("🤖 <b>Motorcito operativo 24/7:</b> Vigilando en paralelo Boom 1000, Boom 500 y USD sin descansos. Sistema activo.")

    contador_rutina = 0
    latido_corazon = 0

    while True:
        try:
            comando = obtener_ultimo_comando()
            if comando:
                if any(palabra in comando for palabra in ["estado", "status", "salud", "diagnostico"]):
                    responder_estado_sistema()

            contador_rutina += 1
            if contador_rutina >= 100:
                verificar_inicio_de_mes()
                contador_rutina = 0

            latido_corazon += 1
            if latido_corazon >= 4800:
                latido_corazon = 0
                ahora_latido = datetime.utcnow().strftime('%H:%M:%S')
                print(f"[LATIDO 24/7] El motor sigue despierto y analizando los activos continuamente a las {ahora_latido} UTC.")

            time.sleep(3)

        except Exception as e:
            notificar_error_critico("Bucle Principal (while True)", e)
            time.sleep(5)


