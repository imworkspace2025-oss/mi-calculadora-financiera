import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Super-App Financiera", layout="wide")

st.title("🧮 TU ASESOR FINANCIERO INTEGRAL + IA")
st.write("Modifica tus datos básicos en la izquierda. El panel central se recalcula al instante.")

# --- CONEXIÓN CON LA IA (Caja segura para tu clave) ---
st.sidebar.header("🔑 Configuración de IA")
api_key_input = st.sidebar.text_input("Introduce tu API Key de Gemini:", type="password")

# --- BARRA LATERAL SIMPLIFICADA ---
st.sidebar.markdown("---")
st.sidebar.header("📥 Tus Datos Mensuales")
ingresos_mensuales = st.sidebar.number_input("Tus ingresos mensuales netos (€)", value=2000, step=100)
ahorro_mensual_total = st.sidebar.number_input("Tu ahorro neto total al mes (€)", value=400, step=50)
capital_inicial = st.sidebar.number_input("Dinero total acumulado actualmente (€)", value=5000, step=500)

st.sidebar.markdown("---")
st.sidebar.header("🏠 Datos de tu Hipoteca/Préstamo")
capital_prestamo = st.sidebar.number_input("Total del préstamo/hipoteca (€)", value=150000, step=5000)
interes_prestamo = st.sidebar.number_input("Interés anual de la hipoteca (%)", value=3.5, step=0.1)
anos_prestamo = st.sidebar.number_input("Plazo restante (en años)", value=25, step=1)

# --- MOTOR DE CÁLCULO ---
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
    
    # 2. INTERÉS COMPUESTO (CON TRADUCCIÓN A EUROS EN TIEMPO REAL)
    st.subheader("📈 2. Proyección de Inversión (A 15 años)")
    pct_inversion = st.slider("¿Qué porcentaje de tu ahorro mensual quieres invertir?", 10, 100, 50, step=5)
    
    # Aquí hacemos la traducción matemática de porcentaje a Euros:
    aportacion_mensual_calculada = ahorro_mensual_total * (pct_inversion / 100)
    
    # Lo mostramos en bonito justo debajo de la barra:
    st.markdown(f"💵 Ese **{pct_inversion}%** equivale a: **{aportacion_mensual_calculada:,.2f} € al mes** para inversión.")
    
    tasa_inv = 0.07  # 7% medio mercado indexado
    total = capital_inicial
    for _ in range(15):
        total = (total + (aportacion_mensual_calculada * 12)) * (1 + tasa_inv)
        
    st.success(f"Invirtiendo esos **{aportacion_mensual_calculada:,.2f} €/mes** "
               f"empezando con tus {capital_inicial:,.2f} € actuales a un 7% anual, en 15 años tendrás:\n\n"
               f"**🚀 {total:,.2f} €**")

with col2:
    # 3. AMORTIZACIÓN HIPOTECA
    st.subheader("🏠 3. Tu Hipoteca al mes")
    tasa_m = (interes_prestamo / 100) / 12
    num_p = anos_prestamo * 12
    if tasa_m > 0:
        cuota = capital_prestamo * (tasa_m * (1 + tasa_m)**num_p) / ((1 + tasa_m)**num_p - 1)
    else:
        cuota = capital_prestamo / num_p
    total_intereses = (cuota * num_p) - capital_prestamo
    st.warning(f"**Cuota Mensual:** {cuota:,.2f} €\n\n"
               f"**Intereses pendientes por pagar al banco:** {total_intereses:,.2f} €")

    # 4. LIBERTAD FINANCIERA
    st.subheader("🕊️ 4. Tu Libertad Financiera (Regla del 4%)")
    num_libertad = gastos_anuales_estimados * 25
    st.error(f"Con un estilo de vida de {gastos_mensuales_calculados:,.2f} € al mes en gastos, "
             f"necesitas acumular un capital invertido de:\n\n"
             f"**🎯 {num_libertad:,.2f} €**\n\n"
             f"Al llegar a esta cifra, podrías vivir de rentas de forma indefinida sin agotar tu dinero.")

# --- BOTÓN DE IA ---
st.markdown("---")
st.subheader("🧠 🤖 CONSULTORÍA ESTRATÉGICA POR IA")

if st.button("🚀 Solicitar Informe al Mejor Asesor Financiero del Mundo"):
    if not api_key_input:
        st.error("Por favor, introduce tu API Key en la barra lateral izquierda para activar la IA.")
    else:
        try:
            genai.configure(api_key=api_key_input)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Actúa como el mejor asesor financiero senior del mundo, con mentalidad analítica y visión de futuro a corto, medio y largo plazo. 
            Analiza la situación de este usuario basándose en sus datos reales actuales:
            - Ingresos mensuales: {ingresos_mensuales} €
            - Ahorro mensual total: {ahorro_mensual_total} € (Gastos mensuales calculados de {gastos_mensuales_calculados} €)
            - Capital acumulado hoy: {capital_inicial} €
            - Cantidad decidida para mover a inversión mensualmente: {aportacion_mensual_calculada} € (Representa el {pct_inversion}% de su ahorro)
            - Hipoteca: {capital_prestamo} € al {interes_prestamo}% a {anos_prestamo} años (Cuota: {cuota:.2f} €).
            - Su meta de libertad financiera requiere: {num_libertad} €
            
            Redacta un informe estratégico impecable en español, con viñetas y un lenguaje claro e inteligente, estructurado en:
            1. **Diagnóstico de Salud Financiera:** Analiza si su nivel de ahorro e inversión actual con respecto a sus ingresos es óptimo o peligroso.
            2. **Plan Táctico a Corto Plazo (Próximos 12 meses):** Qué hacer exactamente mes a mes con el dinero que le sobra (¿amortizar hipoteca?, ¿guardar fondo de emergencia?, ¿invertir?). Diles cantidades reales basadas en sus números.
            3. **Estrategia de Crecimiento a Medio y Largo Plazo:** Dónde y cómo mover el dinero (fondos indexados, depósitos, etc.) según las posibilidades reales que tiene para llegar lo más rápido posible a su número de Libertad Financiera ({num_libertad} €).
            
            Sé muy específico, directo y dale consejos de valor real.
            """
            
            with st.spinner("Tu asesor financiero de IA está analizando los mercados y tus números..."):
                response = model.generate_content(prompt)
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Hubo un problema con la IA: {e}")

