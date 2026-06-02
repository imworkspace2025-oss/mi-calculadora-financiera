import streamlit as st

st.set_page_config(page_title="Super-App Financiera", layout="wide")

st.title("🧮 TU ASESOR FINANCIERO INTEGRAL")
st.write("Introduce tus datos una vez para activar los 4 motores de análisis en paralelo.")

# --- BARRA LATERAL: DATOS ÚNICOS DEL USUARIO ---
st.sidebar.header("📥 Tus Datos Financieros")
ingresos_mensuales = st.sidebar.number_input("Ingresos mensuales netos (€)", value=2000, step=100)
gastos_anuales_estimados = st.sidebar.number_input("Gastos anuales totales (€)", value=18000, step=500)
capital_inicial = st.sidebar.number_input("Dinero ahorrado/invertido actual (€)", value=5000, step=500)
aportacion_mensual = st.sidebar.number_input("¿Cuánto puedes invertir al mes? (€)", value=200, step=50)

st.sidebar.markdown("---")
st.sidebar.header("🏠 Datos de tu Hipoteca/Préstamo")
capital_prestamo = st.sidebar.number_input("Total del préstamo (€)", value=150000, step=5000)
interes_prestamo = st.sidebar.number_input("Interés anual hipoteca (%)", value=3.5, step=0.1)
anos_prestamo = st.sidebar.number_input("Plazo hipoteca (años)", value=25, step=1)

# --- PANEL PRINCIPAL: LAS 4 OPCIONES A LA VEZ ---
col1, col2 = st.columns(2)

with col1:
    # --- BLOQUE 1: REGLA 50/30/20 ---
    st.subheader("📊 1. Presupuesto Inteligente (50/30/20)")
    nec = ingresos_mensuales * 0.5
    cap = ingresos_mensuales * 0.3
    aho = ingresos_mensuales * 0.2
    st.info(f"**Necesidades (50%):** {nec:,.2f} €\n\n**Caprichos (30%):** {cap:,.2f} €\n\n**Tu objetivo de Ahorro (20%):** {aho:,.2f} €")
    
    # --- BLOQUE 2: INTERÉS COMPUESTO ---
    st.subheader("📈 2. Proyección de Inversión (A 15 años)")
    tasa_inv = 0.07 # 7% medio del mercado indexado
    total = capital_inicial
    for _ in range(15):
        total = (total + (aportacion_mensual * 12)) * (1 + tasa_inv)
    st.success(f"Si inviertes tus {aportacion_mensual} €/mes a una media del 7% anual, en 15 años tus {capital_inicial:,.2f} € se convertirán en:\n\n**{total:,.2f} €**")

with col2:
    # --- BLOQUE 3: AMORTIZACIÓN HIPOTECA ---
    st.subheader("🏠 3. Tu Hipoteca al mes")
    tasa_m = (interes_prestamo / 100) / 12
    num_p = anos_prestamo * 12
    if tasa_m > 0:
        cuota = capital_prestamo * (tasa_m * (1 + tasa_m)**num_p) / ((1 + tasa_m)**num_p - 1)
    else:
        cuota = capital_prestamo / num_p
    total_intereses = (cuota * num_p) - capital_prestamo
    st.warning(f"**Cuota Mensual:** {cuota:,.2f} €\n\n**Intereses totales al banco:** {total_intereses:,.2f} €")

    # --- BLOQUE 4: LIBERTAD FINANCIERA ---
    st.subheader("🕊️ 4. Tu Libertad Financiera")
    num_libertad = gastos_anuales_estimados * 25
    st.error(f"Para poder dejar de trabajar y vivir de tus inversiones (Regla del 4%), necesitas acumular un capital de:\n\n**{num_libertad:,.2f} €**")
