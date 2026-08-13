
            else:
                tipo_movimiento = "Haciendo la contra desde abajo (Picada Bajista)"

            # REGLA ÚNICA: AVISAR EXACTAMENTE 1 HORA ANTES A SHANE
            if 50 <= minutos_para_tocar <= 70 and not self.alarma_enviada[activo][t]:
                self.alarma_enviada[activo][t] = True
                msg = (
                    f"⏰ **[ALERTA NUBE - JUAN TRECH]**\n\n"
                    f"📌 **Activo:** {activo}\n"
                    f"📍 **Temporalidad:** {t}\n"
                    f"📉 **Movimiento:** {tipo_movimiento}\n"
                    f"🎯 **Análisis:** Falta **1 HORA** para llegar a tocar la EMA 15"
                )
                reportar_evento_a_shane("ALERTA NUBE EMA 15", msg)

            # Reset cuando el precio se aleja de la zona de toma de bencina
            if distancia_pips > 30:
                self.alarma_enviada[activo][t] = False

motor_fractal = MotorFractalJuanTrech()

# ==========================================
# 3. NÚCLEO ESPECIALIZADO: EMAS Y ZAMBULLIDAS
# ==========================================
class NucleoFractalEMAs:
    def __init__(self):
        self.temporalidades = ["M30", "H1", "H4", "DIARIO", "SEMANAL", "MENSUAL"]
        self.memoria_ciclos = {tf: {"velas_subida": 0, "velas_bajada": 0, "zambullidas": 0} for tf in self.temporalidades}

    def actualizar_conteo_velas(self, timeframe: str, es_subida: bool, zambullida_detectada: bool = False):
        if timeframe in self.memoria_ciclos:
            if es_subida:
                self.memoria_ciclos[timeframe]["velas_subida"] += 1
            else:
                self.memoria_ciclos[timeframe]["velas_bajada"] += 1

            if zambullida_detectada:
                self.memoria_ciclos[timeframe]["zambullidas"] += 1

    def evaluar_cruce_y_vueltas_emas(self, activo: str, timeframe: str, ema1: float, ema5: float, ema15: float):
        datos_tf = self.memoria_ciclos.get(timeframe, {"velas_subida": 0, "zambullidas": 0})
        diferencia_rapida = abs(ema1 - ema5)
        diferencia_lenta = abs(ema5 - ema15)

        if diferencia_rapida > diferencia_lenta * 1.5:
            mensaje = (
                f"🚨 MATRIZ FRACTAL - EMA Y CICLOS [{activo}]\n"
                f"Temporalidad clave: {timeframe}\n"
                f"Conteo actual -> Subidas: {datos_tf['velas_subida']}\n"
                f"Zambullidas acumuladas: {datos_tf['zambullidas']}\n"
                f"⚠️ *Análisis de Vueltas:* La EMA rápida lidera el ciclo."
            )
            reportar_evento_a_shane("CRUCE EMAs DETECTADO", mensaje)

cerebro_fractal = NucleoFractalEMAs()

# ==========================================
# 4. CONEXIÓN EN TIEMPO REAL CON DERIV Y BUCLE
# ==========================================
async def iniciar_sistema_matriz():
    logging.info("🚀 Iniciando motor con especialización de EMAs (EMA 15 Punto de Bencina) y conexión limpia a Shane.")
    ultimo_latido = 0

    while True:
        try:
            async with websockets.connect(DERIV_WS_URL) as websocket:
                logging.info("Conectado al WebSocket de Deriv.")
                suscripcion = {"ticks": "R_100", "subscribe": 1}
                await websocket.send(json.dumps(suscripcion))

                while True:
                    # Enviar el latido de 60 segundos a Shane
                    ahora = time.time()
                    if ahora - ultimo_latido >= 60:
                        enviar_latido_a_shane()
                        ultimo_latido = ahora

                    respuesta = await websocket.recv()
                    datos = json.loads(respuesta)

                    if "tick" in datos:
                        precio = datos["tick"]["quote"]
                        simbolo = datos["tick"]["symbol"]
                        # Procesamiento continuo de fractales
                        await motor_fractal.evaluar_fractalidad_completa(simbolo, precio)

        except Exception as e:
            logging.error(f"Error de conexión: {e}. Reintentando en 5 segundos...")
            await asyncio.sleep(5)

# ==========================================
# 5. EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    try:
        asyncio.run(iniciar_sistema_matriz())
    except KeyboardInterrupt:
        logging.info("Sistema detenido.")
