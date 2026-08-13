
    


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
