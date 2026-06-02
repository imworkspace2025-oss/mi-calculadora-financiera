import streamlit as st
import google.generativeai as genai
import math

st.set_page_config(page_title="Super-App Financiera Pro", layout="wide")

st.title("🧮 TU ASESOR FINANCIERO INTEGRAL + IA (Análisis de Coste Real)")
st.write("Modifica tus datos en la izquierda. El panel central calculará plazos, ahorros e intereses en tiempo real.")

# --- CONEXIÓN CON LA IA ---
st.sidebar.header("🔑 Configuración de IA")
api_key_input = st.sidebar.text_input("Introduce tu API Key de Gemini:", type="password")

# --- BARRA LATERAL ---
st.sidebar.markdown("---")
st.sidebar.header("📥 Tus Datos Mensuales")
ingresos_mensuales = st.sidebar.number_input("Tus ingresos mensuales netos (€)", value=2000, step=100)
ahorro_mensual_total = st.sidebar.number_input("Tu ahorro neto total al mes (€)", value=500, step=50)
capital_inicial = st.sidebar.number_input("Dinero total acumulado actualmente (€)", value=5000, step=500)

st.sidebar.markdown("---")
st.sidebar.header("🏠 Datos Reales de tu Hipoteca")
tipo_hipoteca = st.sidebar.selectbox("Tipo de Hipoteca", ["Fija", "Variable", "Mixta"])
capital_original = st.sidebar.number_input("¿De cuánto fue el préstamo hipotecario original? (€)", value=150000, step=5000)
capital_pendiente = st.sidebar.number_input("Capital pendiente actual por pagar (€)", value=120000, step=5000)
cuota_mensual_actual = st.sidebar.number_input("Tu cuota mensual actual (€)", value=600, step=50)
interes_anual_actual = st.sidebar.number_input("Interés anual actual (%)", value=3.5, step=0.1)

st.sidebar.markdown("**🛡️ Vinculaciones y Seguros Obligatorios:**")
seguros_anuales_banco = st.sidebar.number_input("Coste TOTAL ANUAL de seguros vinculados al banco (Vida, Hogar, etc.) (€)", value=400, step=50)

st.sidebar.markdown("**⚡ Estrategias Extraordinarias:**")
amortizacion_extra = st.sidebar.number_input("Amortización mensual extra (€/mes)", value=0, step=50)
inyeccion_capital_unica = st.sidebar.number_input("Inyección de capital única/puntual (€)", value=0, step=1000)

# --- MOTOR DE CÁLCULO INTERNO ---
gastos_mensuales_calculados = ingresos_mensuales - ahorro_mensual_total
gastos_anuales_estimados = gastos_mensuales_calculados * 12
coste_mensual_seguros = seguros_anuales_banco / 12
cuota_real_total = cuota_mensual_actual + coste_mensual_seguros

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
    
    # 2. INTERÉS COMPUESTO
    st.subheader("📈 2. Proyección de Inversión Personalizada")
    pct_inversion = st.slider("¿Qué porcentaje de tu ahorro mensual quieres invertir?", 10, 100, 50, step=5)
    anos_inversion = st.slider("¿A cuántos años quieres proyectar tu inversión?", 1, 40, 15, step=1)
    
    ahorro_disponible_para_invertir = ahorro_mensual_total - amortizacion_extra
    if ahorro_disponible_para_invertir < 0:
        st.error("⚠️ Estás amortizando más dinero extra de lo que logras ahorrar al mes. Ajusta los números.")
        ahorro_disponible_para_invertir = 0
        
    aportacion_mensual_calculada = ahorro_disponible_para_invertir * (pct_inversion / 100)
    st.markdown(f"💵 El **{pct_inversion}%** de tu ahorro libre equivale a: **{aportacion_mensual_calculada:,.2f} € al mes** para inversión.")
    
    tasa_inv = 0.07
    total = capital_inicial
    for _ in range(anos_inversion):
        total = (total + (aportacion_mensual_calculada * 12)) * (1 + tasa_inv)
        
    st.success(f"Invirtiendo esos **{aportacion_mensual_calculada:,.2f} €/mes** durante **{anos_inversion} años** "
               f"empezando con tus {capital_inicial:,.2f} € actuales a un 7% anual, tendrás:\n\n"
               f"**🚀 {total:,.2f} €**")

with col2:
    # 3. AMORTIZACIÓN HIPOTECA CON COSTE REAL DE VINCULACIONES
    st.subheader("🏠 3. Análisis Real y Costes de tu Hipoteca")
    
    tasa_m = (interes_anual_actual / 100) / 12
    interes_este_mes = capital_pendiente * tasa_m
    capital_este_mes = cuota_mensual_actual - interes_este_mes
    
    if cuota_mensual_actual <= interes_este_mes:
        st.error("⚠️ Tu cuota mensual es demasiado baja para cubrir los intereses.")
    else:
        pagado_ya = capital_original - capital_pendiente
        porcentaje_pagado = (pagado_ya / capital_original) * 100 if capital_original > 0 else 0
        
        st.markdown(f"📈 **Progreso de tu propiedad:** Ya has pagado el **{porcentaje_pagado:.1f}%** del préstamo original.")
        
        # Alerta de Coste Real Integrado
        st.error(f"💸 **TU CUOTA REAL MENSUAL ES DE: {cuota_real_total:,.2f} €**\n\n"
                 f"• **Recibo del préstamo:** {cuota_mensual_actual:,.2f} €/mes\n\n"
                 f"• **Prorrateo de seguros obligatorios:** {coste_mensual_seguros:,.2f} €/mes *({seguros_anuales_banco:,.2f} € al año)*")
        
        pct_capital = (capital_este_mes / cuota_real_total) * 100
        pct_interes = (interes_este_mes / cuota_real_total) * 100
        pct_seguros = (coste_mensual_seguros / cuota_real_total) * 100
        
        st.info(f"🔍 **¿A dónde va cada euro de tu cuota real de {cuota_real_total:,.2f} €?**\n\n"
                f"• **🏠 Capital (Tu casa):** {capital_este_mes:,.2f} € ({pct_capital:.1f}%)\n\n"
                f"• **🏦 Intereses (Para el banco):** {interes_este_mes:,.2f} € ({pct_interes:.1f}%)\n\n"
                f"• **🛡️ Seguros vinculados:** {coste_mensual_seguros:,.2f} € ({pct_seguros:.1f}%)")

        # Cálculos de tiempo
        meses_restantes_normal = -math.log(1 - (capital_pendiente * tasa_m) / cuota_mensual_actual) / math.log(1 + tasa_m)
        anos_normal = meses_restantes_normal / 12
        total_pagado_normal = cuota_mensual_actual * meses_restantes_normal
        intereses_totales_normal = total_pagado_normal - capital_pendiente

        st.warning(f"⏱️ **Tiempo restante para liquidarla:** {anos_normal:.1f} años.\n\n"
                   f"💰 **Intereses del préstamo pendientes:** {intereses_totales_normal:,.2f} €")
        
        # Efecto extras
        capital_pendiente_neto = capital_pendiente - inyeccion_capital_unica
        
        if inyeccion_capital_unica >= capital_pendiente:
            st.success("🎉 ¡BRUTAL! Con esa inyección liquidas la hipoteca hoy por completo.")
        elif amortizacion_extra > 0 or inyeccion_capital_unica > 0:
            cuota_con_extra = cuota_mensual_actual + amortizacion_extra
            
            if cuota_con_extra > (capital_pendiente_neto * tasa_m):
                meses_restantes_extra = -math.log(1 - (capital_pendiente_neto * tasa_m) / cuota_con_extra) / math.log(1 + tasa_m)
                anos_extra = meses_restantes_extra / 12
                
                total_pagado_extra = inyeccion_capital_unica + (cuota_con_extra * meses_restantes_extra)
                intereses_totales_extra = total_pagado_extra - capital_pendiente
                
                anos_ahorrados = anos_normal - anos_extra
                dinero_ahorrado_interes = intereses_totales_normal - intereses_totales_extra

                st.markdown(f"### 🔥 EFECTO DE TUS ACELERADORES:")
                st.success(f"⏱️ **Te independizas del banco:** {anos_ahorrados:.1f} años antes (Se reduce a {anos_extra:.1f} años).\n\n"
                           f"💰 **Dinero que salvas en intereses puros:** {dinero_ahorrado_interes:,.2f} €")

    # 4. LIBERTAD FINANCIERA
    st.subheader("🕊️ 4. Tu Libertad Financiera (Regla del 4%)")
    num_libertad = gastos_anuales_estimados * 25
    st.error(f"Con un estilo de vida de {gastos_mensuales_calculados:,.2f} € al mes en gastos, "
             f"necesitas acumular un capital invertido de:\n\n"
             f"**🎯 {num_libertad:,.2f} €**")

# --- BOTÓN DE IA ---
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
            Actúa como el mejor asesor financiero. Analiza este mapa completo:
            - Ingresos mensuales netos: {ingresos_mensuales} € | Ahorro total: {ahorro_mensual_total} €
            - Capital acumulado hoy: {capital_inicial} € | Dinero asignado a inversión mensual: {aportacion_mensual_calculada} € (Simulado a {anos_inversion} años)
            - Aceleradores: Mensual extra de {amortizacion_extra} €/mes e Inyección única de {inyeccion_capital_unica} €
            - Préstamo Hipotecario original: {capital_original} € | Deuda actual: {capital_pendiente} € en {tipo_hipoteca} al {interes_anual_actual}%.
            - Cuota del recibo: {cuota_mensual_actual} €/mes.
            - GASTO EN SEGUROS DEL BANCO: {seguros_anuales_banco} € al año (añade {coste_mensual_seguros:.2f} €/mes ocultos haciendo una cuota real de {cuota_real_total:.2f} €/mes).
            - Desglose de cuota base: {capital_este_mes:.2f} € van a casa y {interes_este_mes:.2f} € a intereses puros.
            - Tiempo restante estimado: {anos_normal:.1f} años.
            - Meta libertad financiera: {num_libertad} €
            
            Redacta tu dictamen estructurado en:
            1. **EL IMPACTO DE LAS VINCULACIONES (Alerta de sobrecoste):** Analiza el peso de los seguros ({seguros_anuales_banco} €/año). Explica si le conviene mantenerlos para tener bonificado el tipo de interés o si habitualmente compensa perder la bonificación bancaria (ej. que le suban un 0.25% el interés) a cambio de contratar seguros libres más baratos en el mercado.
            2. **ESTRATEGIA OPTIMIZADA DE DESAPALANCAMIENTO VS INVERSIÓN:** Con los números en la mano, calcula si el capital de las inyecciones rinde más matando esta estructura de hipoteca+seguros o en fondos indexados globales al 7%.
            3. **HOJA DE RUTA DE VEHÍCULOS DE INVERSIÓN:** Nombra opciones reales (Cuentas remuneradas, Fondos Indexados de bajo coste de Vanguard/Amundi o Robo-advisors) ideales para este perfil.
            """
            
            with st.spinner("Tu asesor financiero de IA está desgranando los costes ocultos..."):
                response = model.generate_content(prompt)
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Hubo un problema con la IA: {e}")
