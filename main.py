# =====================================================================
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
        self.activos = ACTIVOS_MONITOREADOS
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
