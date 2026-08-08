# Bottraiding - Estrategia M30 / H1

def analizar_mercado(df_m30, df_h1):
    # Detección de trampa de compradores y purga de vendedores (Order Block)
    falsa_salida = df_m30['high'].iloc[-2] > df_m30['high'].iloc[-3]
    purga_ob = df_m30['low'].iloc[-1] < df_m30['low'].iloc[-2]
    
    # Confirmación de cruce M30 directo a H1
    cruce_m30 = df_m30['ema_rapida'].iloc[-1] > df_m30['ema_lenta'].iloc[-1]
    tendencia_h1 = df_h1['ema_rapida'].iloc[-1] > df_h1['ema_lenta'].iloc[-1]
    
    if purga_ob and cruce_m30 and tendencia_h1:
        return "ENTRADA_COMPRA"
    
    return "ESPERAR"
