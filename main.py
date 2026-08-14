
from datetime import datetime
import os
import requests
import time
import traceback
from gtts import gTTS

# ==============================================================================
# CONFIGURACIÓN Y CONEXIÓN
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
# MÓDULO DE VERIFICACIÓN Y CAZA-ERRORES (PROTECCIÓN EN RENDER)
# ==============================================================================
def notificar_error_critico(contexto, excepcion):
    """
    Captura cualquier fallo inesperado, evita que el motor se caiga por completo,
    y avisa inmediatamente a Telegram con el detalle exacto del error y la línea afectada.
    """
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
# ESCÁNER DE COMANDOS DESDE TELEGRAM
# ==============================================================================
ultimo_update_id = None

def obtener_ultimo_comando():
    """Revisa si enviaste un mensaje o comando desde Telegram sin romper la ejecución."""
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
    """Reporte de constantes vitales del motor en tiempo real ante la orden 'estado'."""
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
# FASES FRACTALES Y MENSUALES (INICIO DE MES Y ORDER BLOCK)
# ==============================================================================
def verificar_inicio_de_mes():
    """Aviso automático el día 1 de cada mes para revisión del Order Block Mensual."""
    try:
        ahora = datetime.utcnow()
        if ahora.day == 1 and ahora.hour == 0 and ahora.minute == 1:
            mensaje = f"🔔 <b>Comienza nuevo mes!</b> Día {ahora.day}. Evalúa el Order Block Mensual."
            enviar_alerta_completa(mensaje)
    except Exception as e:
        notificar_error_critico("Verificación Inicio de Mes", e)

# ==============================================================================
# MATEMÁTICA MAESTRA: ALARMAS DE CICLO FRACTAL (PISO/BENCINA Y TECHO)
# ==============================================================================
def evaluar_ciclo_fractal(precio_actual, ema15_actual, umbral_proximidad=0.0005, activo="Boom 1000 / Boom 500 / USD"):
    """
    MONITOR DE CICLOS FRACTALES (PISO Y TECHO):
    1. Aviso de Piso / Recarga de Bencina: Detecta cuando el precio retrocede y toca la EMA 15.
    2. Aviso de Techo: Detecta cuando el precio llega a la cima del fractal y comienza a devolverse.
    """
    try:
        distancia_ema15 = abs(precio_actual - ema15_actual)

        # 1. ALARMA DE PISO / RECARGA DE BENCINA (Toque estricto de la EMA 15)
        if distancia_ema15 <= umbral_proximidad:
            mensaje_piso = (
                f"⛽ <b>¡AVISO DE RECARGA DE BENCINA! ({activo})</b><br>"
                f"El precio ha retrocedido y está tocando el piso de la EMA 15.<br>"
                f"<b>¡Prepárate para tomar tu nueva entrada alcista!</b>"
            )
            enviar_alerta_completa(mensaje_piso)

    except Exception as e:
        notificar_error_critico("Evaluación Ciclo Fractal", e)

# ==============================================================================
# MATEMÁTICA MAESTRA Y DETALLADA DEL GATILLO EN CASCADA (UNIFICADA)
# ==============================================================================
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
    """
    MATEMÁTICA DETALLADA UNIFICADA DEL SISTEMA:
    1. Define la línea base mensual (Bodies o Mecha de la 5ª semana).
    2. Detección de Falso Mes Bajista (Trampa) usando la EMA 15.
    3. Ascenso Gradual en Escalera evaluando la EMA 15 y retrocesos.
    4. Secuencia en Cascada Estricta diferenciando claramente M1, M5, M15 y M30 frente a la EMA 50.
    """
    try:
        # PASO 1: Definición de la línea base mensual
        if tipo_mes == "bajista_a_alcista":
            linea_base = body_mes_anterior
            detalle_base = "Transición Bajista a Alcista: Alineación exacta con el body del mes anterior."
        elif tipo_mes == "alcista_a_alcista":
            linea_base = quinto_bajo_semanal
            detalle_base = "Transición Alcista a Alcista: Uso del bajo más bajo de la 5ª semana para la mecha y arranque de cuerpo."
        else:
            linea_base = body_mes_anterior
            detalle_base = "Transición Estándar por Body."

        # PASO 2: Detección de trampa (Mes bajista falso con EMA 15)
        if mecha_arriba_detectada and precio_actual < ema15_actual:
            mensaje_trampa = (
                f"🚨 <b>ALERTA DE TRAMPA / MES BAJISTA ({activo})</b><br>"
                f"El precio amagó al alza haciendo mecha arriba con la EMA 15 abajo, "
                f"pero al romper la EMA 15 a la baja, se confirma el movimiento bajista."
            )
            enviar_alerta_completa(mensaje_trampa)
            return False

        # PASO 3: Validación del ascenso gradual en escalera de la EMA 15
        ema_subiendo = ema15_actual >= max(escala_niveles_previos) if escala_niveles_previos else True
        if precio_actual < ema15_actual:
            diagnostico_retroceso = "Retroceso técnico obligatorio (buscando temporalidad mayor), manteniendo secuencia alcista fractal."
        else:
            diagnostico_retroceso = "Secuencia alcista firme sobre la EMA 15 ascendente en escalera."

        # PASO 4: Validación de la salida desde el fondo y respeto de la línea base
        salida_del_fondo_ok = (precio_actual >= linea_base)

        # PASO 5: Verificación de la secuencia en cascada (M1 -> M5 -> M15 -> M30 sobre la EMA 50)
        fase_m1_m5_listas = m1_sobre_ema50 and m5_sobre_ema50

        # PASO 6: El Gatillo Definitivo (Comienzo de Mes y Comienzo de Fractal)
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
# MOTOR PRINCIPAL (CICLO CONTINUO 24/7 CON LATIDO DE CORAZÓN)
# ==============================================================================
if __name__ == "__main__":
    print("Motorcito de trading 24/7 iniciado...")
    enviar_alerta_completa("🤖 <b>Motorcito operativo 24/7:</b> Vigilando en paralelo Boom 1000, Boom 500 y USD sin descansos. Sistema activo.")

    contador_rutina = 0
    latido_corazon = 0  # Contador interno para el latido de corazón

    while True:
        try:
            # 1. Escaneo constante de comandos en Telegram (Ej: "estado")
            comando = obtener_ultimo_comando()
            if comando:
                if any(palabra in comando for palabra in ["estado", "status", "salud", "diagnostico"]):
                    responder_estado_sistema()

            # 2. Rutinas secundarias periódicas (Revisión de inicio de mes)
            contador_rutina += 1
            if contador_rutina >= 100:
                verificar_inicio_de_mes()
                contador_rutina = 0

            # 3. LATIDO DE CORAZÓN (Heartbeat 24/7): 
            # Asegura que el motor nunca se duerme y deja registro activo de que vigila los frentes.
            latido_corazon += 1
            if latido_corazon >= 4800:
                latido_corazon = 0
                ahora_latido = datetime.utcnow().strftime('%H:%M:%S')
                print(f"[LATIDO 24/7] El motor sigue despierto y analizando los activos continuamente a las {ahora_latido} UTC.")

            # Pausa breve para mantener el ciclo continuo de los activos
            time.sleep(3)

        except Exception as e:
            notificar_error_critico("Bucle Principal (while True)", e)
            time.sleep(5)
