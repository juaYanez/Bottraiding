
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except Exception as e:
        print(f"Error enviando audio a Telegram: {e}")


# =====================================================================
# FASE 1: AVISO DE INICIO DE MES (ORDER BLOCK MENSUAL)
# =====================================================================
def verificar_inicio_de_mes():
    ahora = datetime.datetime.utcnow()
    if ahora.day == 1 and ahora.hour == 0 and ahora.minute == 1:
        mensaje = f"🚀 <b>¡Comienzo de nuevo mes!</b> Día {ahora.day}. Es hora de trazar tu Order Block mensual."
        enviar_alerta_completa(mensaje)


# =====================================================================
# FASE 2: GATILLO DE LOS PRIMEROS 5 DÍAS (CASCADA M30)
# =====================================================================
def evaluar_gatillo_dias_iniciales(m1_cruzo, m5_cruzo, m15_cruzo, ema15_m30, ema50_m30, activo):
    ahora = datetime.datetime.utcnow()
    if not (1 <= ahora.day <= 5):
        return

    menores_confirmadas = m1_cruzo and m5_cruzo and m15_cruzo
    distancia_m30 = abs(ema15_m30 - ema50_m30)
    umbral_proximidad = 0.0008

    if menores_confirmadas and distancia_m30 <= umbral_proximidad and ema15_m30 < ema50_m30:
        mensaje = (
            f"🚀 <b>¡GATILLO MAESTRO ACTIVADO ({activo})!</b><br>"
            "M1, M5 y M15 ya cruzaron al alza. M30 está chocando para atravesar la EMA 50. "
            "<b>¡Comienza el verdadero movimiento alcista!</b>"
        )
        enviar_alerta_completa(mensaje)


# =====================================================================
# FASE 3: MAPA FRACTAL Y GESTIÓN DE ENTRADA/PARCIALES
# =====================================================================
def evaluar_ciclo_fractal(temporalidad, activo, precio_actual, ema15_valor, en_la_cima=False, minutos_para_tocar_piso=None):
    if en_la_cima:
        mensaje = f"📊 <b>TECHO DE FRACTAL ({activo} - {temporalidad}):</b> El precio hizo la guatita arriba. <b>¡Saca parciales!</b>"
        enviar_alerta_completa(mensaje)
        return

    if minutos_para_tocar_piso is not None and minutos_para_tocar_piso <= 30:
        mensaje = (
            f"📊 <b>AVISO DE ENTRADA PRÓXIMA ({activo} - {temporalidad}):</b><br>"
            f"Faltan aproximadamente {minutos_para_tocar_piso} minutos para que el precio toque el piso de la EMA 15. "
            "<b>Prepárate para colocar tu nueva entrada alcista.</b>"
        )
        enviar_alerta_completa(mensaje)


# =====================================================================
# MOTOR PRINCIPAL (Con el bucle de seguridad para Render)
# =====================================================================
if __name__ == "__main__":
    print("Motorcito de trading completo y optimizado iniciado correctamente.")
    enviar_alerta_completa("<b>Motorcito operativo:</b> Sistema completo en línea y sincronizado.")
    
    # Bucle infinito para que el servidor no se apague ni se reinicie en bucle
    while True:
        verificar_inicio_de_mes()
        time.sleep(300) # Pausa de 5 minutos entre verificaciones
