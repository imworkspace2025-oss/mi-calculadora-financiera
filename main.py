import streamlit as st
import google.generativeai as genai
import math

st.set_page_config(page_title="Super-App Financiera Pro", layout="wide")

st.title("🧮 TU ASESOR FINANCIERO INTEGRAL + IA (Versión Mapa Estratégico)")
st.write("Modifica tus datos en la izquierda. El panel central simula el impacto de tus aportaciones y golpes de capital en tiempo real.")

# --- CONEXIÓN CON LA IA ---
st.sidebar.header("🔑 Configuración de IA")
api_key_input = st.sidebar.text_input("Introduce tu API Key de Gemini:", type="password")

# --- BARRA LATERAL SIMPLIFICADA ---
st.sidebar.markdown("---")
st.sidebar.header("📥 Tus Datos Mensuales")
ingresos_mensuales = st.sidebar.number_input("Tus ingresos mensuales netos (€)", value=2000, step=100)
ahorro_mensual_total = st.sidebar.number_input("Tu ahorro neto total al mes (€)", value=500, step=50)
capital_inicial = st.sidebar.number_input("Dinero total acumulado actualmente (€)", value=5000, step=500)

st.sidebar.markdown("---")
st.sidebar.header("🏠 Datos de tu Hipoteca")
tipo_hipoteca = st.sidebar.selectbox("Tipo de Hipoteca", ["Fija", "Variable", "Mixta"])
capital_pendiente = st.sidebar.number_input("Capital pendiente actual por pagar (€)", value=120000, step=5000)
interes_anual_actual = st.sidebar.number_input("Interés anual actual (%)", value=3.5, step=0.1)

st.sidebar.markdown("**⚡ Estrategias Extraordinarias:**")
amortizacion_extra = st.sidebar.number_input("Amortización mensual extra (€/mes)", value=0, step=50)
inyeccion_capital_unica = st.sidebar.number_input("Inyección de capital única/puntual (€)", value=0, step=1000)

# --- MOTOR DE CÁLCULO INTERNO ---
gastos_mensuales_calculados = ingresos_mensuales - ahorro_mensual_total
gastos_anuales_estimados = gastos_mensuales_calculados * 12

# --- PANEL PRINCIPAL ---
col1, col2 = st.columns(2)

with col1:
    # 1. REGLA 50/30/20
    st.subheader("📊 1. Presupuesto Ideal Recomendado (50/30/20)")
    nec = ingresos_mensuales * 0.5
    cap = ingresos_mensuales * 0.3
    aho = ingresos_mensuales * 0.2
    st.info(f"Para tus ingresos de **{ingresos_mensuales:,.2f} €**, la regla ideal dice:\n\n"
            f"**🏠 Necesidades básicas (50%):** {nec:,.2f} €/mes\n\n"
            f"**🎉 Caprichos y Ocio (30%):** {cap:,.2f} €/mes\n\n"
            f"**🐷 Ahorro óptimo recomendado (20%):** {aho:,.2f} €/mes\n\n"
            f"*(Tu tasa de ahorro actual es del {((ahorro_mensual_total/ingresos_mensuales)*100):.1f}%, destinando {ahorro_mensual_total:,.2f} € al ahorro)*")
    
    # 2. INTERÉS COMPUESTO (CON DOS BARRAS: PORCENTAJE Y AÑOS)
    st.subheader("📈 2. Proyección de Inversión Personalizada")
    pct_inversion = st.slider("¿Qué porcentaje de tu ahorro mensual quieres invertir?", 10, 100, 50, step=5)
    anos_inversion = st.slider("¿A cuántos años quieres proyectar tu inversión?", 1, 40, 15, step=1)
    
    ahorro_disponible_para_invertir = ahorro_mensual_total - amortizacion_extra
    if ahorro_disponible_para_invertir < 0:
        st.error("⚠️ Estás amortizando más dinero extra de lo que logras ahorrar al mes. Ajusta los números.")
        ahorro_disponible_para_invertir = 0
        
    aportacion_mensual_calculada = ahorro_disponible_para_invertir * (pct_inversion / 100)
    st.markdown(f"💵 El **{pct_inversion}%** de tu ahorro libre equivale a: **{aportacion_mensual_calculada:,.2f} € al mes** para inversión.")
    
    tasa_inv = 0.07  # 7% medio mercado indexado mundial
    
    # Si el usuario NO inyecta el capital en la hipoteca, simulamos que lo inyecta AQUÍ en la inversión
    capital_inicial_inversion = capital_inicial
    st.caption("*(Nota: Si no usas tu dinero extra para amortizar hipoteca, la IA simulará meterlo aquí de inicio)*")
    
    total = capital_inicial_inversion
    for _ in range(anos_inversion):
        total = (total + (aportacion_mensual_calculada * 12)) * (1 + tasa_inv)
        
    st.success(f"Invirtiendo esos **{aportacion_mensual_calculada:,.2f} €/mes** durante **{anos_inversion} años** "
               f"empezando con tus {capital_inicial_inversion:,.2f} € actuales a un 7% anual, tendrás:\n\n"
               f"**🚀 {total:,.2f} €**")

with col2:
    # 3. AMORTIZACIÓN HIPOTECA CON INYECCIÓN A SUMA ALZADA
    st.subheader("🏠 3. Análisis Real de tu Hipoteca")
    anos_hipoteca_restantes = st.slider("¿Cuántos años te quedan por contrato de hipoteca?", 1, 40, 20, step=1)
    
    tasa_m = (interes_anual_actual / 100) / 12
    num_meses_contrato = anos_hipoteca_restantes * 12
    
    # Cálculo automático de la cuota base normal
    if tasa_m > 0:
        cuota_base_calculada = capital_pendiente * (tasa_m * (1 + tasa_m)**num_meses_contrato) / ((1 + tasa_m)**num_meses_contrato - 1)
    else:
        cuota_base_calculada = capital_pendiente / num_meses_contrato
        
    intereses_totales_normal = (cuota_base_calculada * num_meses_contrato) - capital_pendiente

    st.warning(f"**Tu cuota mensual contratada:** {cuota_base_calculada:,.2f} €/mes\n\n"
               f"**Intereses totales que te quedan por pagar (sin extras):** {intereses_totales_normal:,.2f} €")
    
    # Cálculo del impacto de las estrategias combinadas (Mensual + Única)
    capital_pendiente_neto = capital_pendiente - inyeccion_capital_unica
    
    if inyeccion_capital_unica >= capital_pendiente:
        st.success("🎉 ¡BRUTAL! Con esa inyección de capital liquidas la hipoteca por completo hoy mismo. Adiós banco.")
    else:
        cuota_con_extra = cuota_base_calculada + amortizacion_extra
        
        if (amortizacion_extra > 0 or inyeccion_capital_unica > 0) and cuota_con_extra > (capital_pendiente_neto * tasa_m):
            # Calculamos los nuevos meses restantes aplicando el hachazo del capital único y la cuota mensual extra
            meses_restantes_extra = -math.log(1 - (capital_pendiente_neto * tasa_m) / cuota_con_extra) / math.log(1 + tasa_m)
            anos_extra = meses_restantes_extra / 12
            
            # Dinero total que saldrá del bolsillo en el plan extra (Inyección + cuotas mensuales)
            total_pagado_extra = inyeccion_capital_unica + (cuota_con_extra * meses_restantes_extra)
            intereses_totales_extra = total_pagado_extra - capital_pendiente
            
            anos_ahorrados = anos_hipoteca_restantes - anos_extra
            dinero_ahorrado_interes = intereses_totales_normal - intereses_totales_extra

            st.markdown(f"### 🔥 MAPA DE IMPACTO DE TUS EXTRAS:")
            texto_estrategia = "Aplicando tus aceleradores financieros:\n\n"
            if inyeccion_capital_unica > 0:
                texto_estrategia += f"• Metes un hachazo único de **{inyeccion_capital_unica:,.2f} €** a la deuda.\n\n"
            if amortizacion_extra > 0:
                texto_estrategia += f"• Sumas **{amortizacion_extra:,.2f} €** extra cada mes.\n\n"
                
            st.info(f"{texto_estrategia}"
                    f"⏱️ **Te independizas del banco:** {anos_ahorrados:.1f} años antes (Tu hipoteca se reduce a {anos_extra:.1f} años).\n\n"
                    f"💰 **Dinero neto que salvas en intereses:** {dinero_ahorrado_interes:,.2f} € que te quedan a ti.")

    # 4. LIBERTAD FINANCIERA
    st.subheader("🕊️ 4. Tu Libertad Financiera (Regla del 4%)")
    num_libertad = gastos_anuales_estimados * 25
    st.error(f"Con un estilo de vida de {gastos_mensuales_calculados:,.2f} € al mes en gastos, "
             f"necesitas acumular un capital invertido de:\n\n"
             f"**🎯 {num_libertad:,.2f} €**\n\n"
             f"Al llegar a esta cifra, podrías vivir de rentas de forma indefinida sin agotar tu dinero.")

# --- BOTÓN DE IA: EL DICTAMEN ESTRATÉGICO ---
st.markdown("---")
st.subheader("🧠 🤖 CONSULTORÍA ESTRATÉGICA E ITINERARIO DE INVERSIÓN")

if st.button("🚀 Solicitar Informe y Destinos de Inversión Concretos"):
    if not api_key_input:
        st.error("Por favor, introduce tu API Key en la barra lateral izquierda para activar la IA.")
    else:
        try:
            genai.configure(api_key=api_key_input)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Actúa como el mejor asesor financiero del mundo, experto en asignación de activos (Asset Allocation).
            Analiza estratégicamente este mapa financiero del usuario:
            - Ingresos mensuales netos: {ingresos_mensuales} €
            - Ahorro mensual total: {ahorro_mensual_total} € (Gastos mensuales calculados de {gastos_mensuales_calculados} €)
            - Capital líquido acumulado hoy: {capital_inicial} €
            - Dinero asignado a inversión mensual: {aportacion_mensual_calculada} € (Simulado a un horizonte de {anos_inversion} años)
            - Acelerador 1 (Amortización mensual extra hipoteca): {amortizacion_extra} €/mes
            - Acelerador 2 (Inyección de capital ÚNICA/PUNTUAL planteada): {inyeccion_capital_unica} €
            - Datos Hipoteca: Debe {capital_pendiente} € en una hipoteca tipo {tipo_hipoteca} al {interes_anual_actual}% de interés (Contrato restante de {anos_hipoteca_restantes} años).
            - Su meta de libertad financiera requiere: {num_libertad} €
            
            Redacta un dictamen impecable en español, directo y con viñetas claras estructurado en:
            1. **EL GRAN DILEMA (Amortizar vs Invertir):** Analiza específicamente si la inyección única de {inyeccion_capital_unica} € (y el ahorro mensual) rinde más quitándolo de la hipoteca al {interes_anual_actual}% o si es financieramente más inteligente meterlo en el mercado internacional al 7% estimado. Da una recomendación clara basada en matemáticas y en el tipo de hipoteca ({tipo_hipoteca}).
            2. **¿DÓNDE PONER EL DINERO EXACTAMENTE?:** Nombra vehículos financieros reales en España/Europa para este perfil:
               - Fondo de emergencia (Cuentas remuneradas de alta rentabilidad o fondos monetarios). Indica cuánto dinero exacto de su colchón debe quedarse quieto por seguridad.
               - Vehículos de inversión global y bajo coste: Explica Fondos Indexados (ej. Vanguard, Amundi que repliquen MSCI World o S&P 500) o Robo-advisors para automatizar las aportaciones mensuales de {aportacion_mensual_calculada} €.
            3. **ESTRATEGIA DE REEVALUACIÓN:** Explica al usuario cómo usar este dashboard en el futuro cuando acumule picos de ahorro para saber cuándo ejecutar nuevas inyecciones de capital.
            
            Sé muy específico, directo y aporta un valor consultivo brutal.
            """
            
            with st.spinner("Tu asesor financiero de IA está cruzando los datos para darte tu dictamen..."):
                response = model.generate_content(prompt)
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Hubo un problema con la IA: {e}")
