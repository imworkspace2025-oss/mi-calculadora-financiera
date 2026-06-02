import streamlit as st
import google.generativeai as genai
import pandas as pd
import math

# Configuración de página limpia y ancha
st.set_page_config(page_title="Cuadro de Mandos Financiero Pro", layout="wide")

st.title("📊 TU DASHBOARD FINANCIERO INTEGRAL")
st.write("Gestiona tu patrimonio, optimiza tu hipoteca y proyecta tu libertad financiera con gráficos interactivos.")

# ==========================================
# 🛠️ BARRA LATERAL CON DESPLEGABLES (EXPANDERS)
# ==========================================
st.sidebar.title("⚙️ Panel de Control")

# Desplegable 1: Configuración de la IA
with st.sidebar.expander("🔑 Configuración de IA", expanded=True):
    api_key_input = st.text_input("Introduce tu Gemini API Key:", type="password", help="Necesaria solo para activar la pestaña del Consultor de IA.")
    if not api_key_input:
        st.caption("🔒 IA en espera. Las calculadoras y gráficas funcionan al 100% sin clave.")

# Desplegable 2: Datos del Usuario
with st.sidebar.expander("📥 Tus Datos Mensuales", expanded=False):
    ingresos_mensuales = st.number_input("Ingresos mensuales netos (€)", value=2000, step=100)
    ahorro_mensual_total = st.number_input("Ahorro neto total al mes (€)", value=500, step=50)
    capital_inicial = st.number_input("Dinero acumulado actual (€)", value=5000, step=500)

# Desplegable 3: Datos de la Hipoteca
with st.sidebar.expander("🏠 Tu Hipoteca Base", expanded=False):
    tipo_hipoteca = st.sidebar.selectbox("Tipo de Hipoteca", ["Fija", "Variable", "Mixta"])
    capital_original = st.number_input("Préstamo original (€)", value=150000, step=5000)
    capital_pendiente = st.number_input("Capital pendiente actual (€)", value=120000, step=5000)
    cuota_mensual_actual = st.number_input("Cuota mensual del recibo (€)", value=600, step=50)
    interes_anual_actual = st.number_input("Interés anual actual (%)", value=3.5, step=0.1)

# Desplegable 4: Costes Ocultos / Seguros
with st.sidebar.expander("🛡️ Seguros y Vinculaciones", expanded=False):
    seguros_anuales_banco = st.number_input("Coste TOTAL ANUAL de seguros bancarios (€)", value=400, step=50)

# Desplegable 5: Estrategias de Aceleración
with st.sidebar.expander("⚡ Aceleradores de Capital", expanded=False):
    amortizacion_extra = st.number_input("Aportación extra mensual (€/mes)", value=0, step=50)
    inyeccion_capital_unica = st.number_input("Inyección de capital única/puntual (€)", value=0, step=1000)


# ==========================================
# 🧮 MOTOR DE CÁLCULO INTERNO (MATEMÁTICAS)
# ==========================================
gastos_mensuales_calculados = ingresos_mensuales - ahorro_mensual_total
gastos_anuales_estimados = gastos_mensuales_calculados * 12

# Cálculos Hipoteca Base
tasa_m = (interes_anual_actual / 100) / 12
coste_mensual_seguros = seguros_anuales_banco / 12
cuota_real_total = cuota_mensual_actual + coste_mensual_seguros

if cuota_mensual_actual > (capital_pendiente * tasa_m):
    interes_este_mes = capital_pendiente * tasa_m
    capital_este_mes = cuota_mensual_actual - interes_este_mes
    
    meses_restantes_normal = -math.log(1 - (capital_pendiente * tasa_m) / cuota_mensual_actual) / math.log(1 + tasa_m)
    anos_normal = meses_restantes_normal / 12
    total_pagado_normal = cuota_mensual_actual * meses_restantes_normal
    intereses_totales_normal = total_pagado_normal - capital_pendiente
else:
    interes_este_mes = capital_pendiente * tasa_m
    capital_este_mes = 0
    anos_normal = 0
    intereses_totales_normal = 0

# ==========================================
# 🗂️ PESTAÑAS CENTRALES (TABS)
# ==========================================
tab_resumen, tab_presupuesto, tab_inversion, tab_hipoteca, tab_libertad, tab_ia = st.tabs([
    "📊 Vista General", 
    "🥗 Presupuesto 50/30/20", 
    "📈 Curva de Inversión", 
    "🏠 Escáner Hipoteca", 
    "🕊️ Libertad Financiera",
    "🤖 Consultor IA"
])

# ------------------------------------------
# PESTAÑA 1: VISTA GENERAL
# ------------------------------------------
with tab_resumen:
    st.subheader("🏁 Resumen Ejecutivo de tu Salud Financiera")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tasa de Ahorro Real", f"{((ahorro_mensual_total/ingresos_mensuales)*100):.1f}%", f"{ahorro_mensual_total} €/mes")
    col2.metric("Cuota Real Hipoteca", f"{cuota_real_total:,.2f} €", f"+{coste_mensual_seguros:.1f} €/mes en seguros", delta_color="inverse")
    col3.metric("Años de Hipoteca Libres", f"{anos_normal:.1f} años" if anos_normal > 0 else "Error datos")
    
    num_libertad = gastos_anuales_estimados * 25
    col4.metric("Meta Libertad Financiera", f"{num_libertad:,.0f} €")
    
    st.markdown("---")
    st.info("💡 **Navegación:** Explora las pestañas superiores para ver los análisis detallados y las gráficas individuales de cada bloque.")

# ------------------------------------------
# PESTAÑA 2: REGLA 50/30/20 + GRÁFICA
# ------------------------------------------
with tab_presupuesto:
    st.subheader("🥗 Distribución del Presupuesto Mensual")
    nec = ingresos_mensuales * 0.5
    cap = ingresos_mensuales * 0.3
    aho = ingresos_mensuales * 0.2
    
    col_p1, col_p2 = st.columns([1, 1])
    
    with col_p1:
        st.markdown(f"**Análisis de tus ingresos ({ingresos_mensuales:,.2f} €):**")
        st.info(f"• **🏠 Necesidades (50%):** Presupuesto de {nec:,.2f} €/mes\n\n"
                f"• **🎉 Caprichos (30%):** Presupuesto de {cap:,.2f} €/mes\n\n"
                f"• **🐷 Ahorro Óptimo (20%):** Deberías ahorrar {aho:,.2f} €/mes")
        st.success(f"👏 Tu ahorro real configurado es de **{ahorro_mensual_total:,.2f} €/mes**.")

    with col_p2:
        st.markdown("**📊 Comparativa de Presupuestos (€):**")
        df_presupuesto = pd.DataFrame({
            "Importe (€)": [nec, cap, aho, ahorro_mensual_total]
        }, index=["Necesidades (50%)", "Caprichos (30%)", "Ahorro Rec. (20%)", "Tu Ahorro Real"])
        st.bar_chart(df_presupuesto)

# ------------------------------------------
# PESTAÑA 3: INTERÉS COMPUESTO + GRÁFICA DE LÍNEA
# ------------------------------------------
with tab_inversion:
    st.subheader("📈 Proyección y Curva de Crecimiento del Capital")
    
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        pct_inversion = st.slider("¿Qué % de tu ahorro mensual vas a invertir?", 10, 100, 50, step=5)
    with c_s2:
        anos_inversion = st.slider("¿A cuántos años vista quieres proyectar?", 1, 40, 15, step=1)
        
    ahorro_disponible_para_invertir = ahorro_mensual_total - amortizacion_extra
    if ahorro_disponible_para_invertir < 0:
        st.error("⚠️ Alerta: Estás amortizando al mes más de lo que logras ahorrar.")
        ahorro_disponible_para_invertir = 0
        
    aportacion_mensual_calculada = ahorro_disponible_para_invertir * (pct_inversion / 100)
    tasa_inv = 0.07
    
    # Calcular histórico año a año para la gráfica
    lista_anos = []
    lista_capital = []
    total_acumulado = capital_inicial
    
    for ano in range(1, anos_inversion + 1):
        total_acumulado = (total_acumulado + (aportacion_mensual_calculada * 12)) * (1 + tasa_inv)
        lista_anos.append(f"Año {ano}")
        lista_capital.append(total_acumulado)
        
    col_inv1, col_inv2 = st.columns([1, 2])
    with col_inv1:
        st.metric("Tu aportación mensual", f"{aportacion_mensual_calculada:,.2f} €")
        st.metric(f"Capital Final (Año {anos_inversion})", f"{total_acumulado:,.2f} €")
        st.caption("Simulación calculada basándose en un 7% de interés medio anual (Fondos Indexados globales).")
        
    with col_inv2:
        st.markdown("**📈 Evolución temporal de tu patrimonio:**")
        df_crecimiento = pd.DataFrame({"Capital acumulado (€)": lista_capital}, index=lista_anos)
        st.line_chart(df_crecimiento)

# ------------------------------------------
# PESTAÑA 4: ESCÁNER DE HIPOTECA + GRÁFICAS COMPARATIVAS
# ------------------------------------------
with tab_hipoteca:
    st.subheader("🏠 Radiografía y Optimización de la Hipoteca")
    
    if anos_normal == 0:
        st.error("La cuota mensual del recibo debe ser superior a los intereses devengados este mes.")
    else:
        pagado_ya = capital_original - capital_pendiente
        porcentaje_pagado = (pagado_ya / capital_original) * 100 if capital_original > 0 else 0
        
        col_h1, col_h2 = st.columns(2)
        
        with col_h1:
            st.markdown("#### 🔍 Desglose de tu recibo mensual real:")
            df_cuota = pd.DataFrame({
                "Euros (€)": [capital_este_mes, interes_este_mes, coste_mensual_seguros]
            }, index=["Capital (Tu Casa)", "Intereses (Banco)", "Seguros (Coste Oculto)"])
            st.bar_chart(df_cuota)
            
        with col_h2:
            st.markdown("#### 📊 Estado Actual de la Deuda:")
            st.info(f"• **Porcentaje pagado de la vivienda:** {porcentaje_pagado:.1f}%\n\n"
                    f"• **Tiempo restante original:** {anos_normal:.1f} años\n\n"
                    f"• **Intereses pendientes base:** {intereses_totales_normal:,.2f} €")

        # Cálculo de estrategias extraordinarias si existen
        capital_pendiente_neto = capital_pendiente - inyeccion_capital_unica
        
        if inyeccion_capital_unica >= capital_pendiente:
            st.success("🎉 **¡HACHAZO INMEDIATO!** Liquidación total. Eres libre de deuda hoy.")
        elif amortizacion_extra > 0 or inyeccion_capital_unica > 0:
            cuota_con_extra = cuota_mensual_actual + amortizacion_extra
            
            if cuota_con_extra > (capital_pendiente_neto * tasa_m):
                meses_restantes_extra = -math.log(1 - (capital_pendiente_neto * tasa_m) / cuota_con_extra) / math.log(1 + tasa_m)
                anos_extra = meses_restantes_extra / 12
                
                total_pagado_extra = inyeccion_capital_unica + (cuota_con_extra * meses_restantes_extra)
                intereses_totales_extra = total_pagado_extra - capital_pendiente
                
                anos_ahorrados = anos_normal - anos_extra
                dinero_ahorrado_interes = intereses_totales_normal - intereses_totales_extra

                st.markdown("---")
                st.markdown("### 🔥 Impacto de tus Inyecciones y Extras de Capital")
                
                col_m1, col_m2 = st.columns([1, 1])
                with col_m1:
                    st.metric("Años ahorrados al banco", f"{anos_ahorrados:.1f} años antes", f"La hipoteca baja a {anos_extra:.1f} años")
                    st.metric("Dinero salvado en intereses puros", f"{dinero_ahorrado_interes:,.2f} €")
                with col_m2:
                    st.markdown("**📉 Comparativa de Intereses Totales a pagar (€):**")
                    df_intereses = pd.DataFrame({
                        "Intereses (€)": [intereses_totales_normal, intereses_totales_extra]
                    }, index=["Intereses Sin Extras", "Intereses Aplicando Extras"])
                    st.bar_chart(df_intereses)

# ------------------------------------------
# PESTAÑA 5: LIBERTAD FINANCIERA
# ------------------------------------------
with tab_libertad:
    st.subheader("🕊️ Estrategia de Libertad Financiera (Regla del 4%)")
    st.error(f"## 🎯 TU NÚMERO OBJETIVO: {num_libertad:,.2f} €")
    st.write(f"Para mantener tu ritmo de vida actual, tus gastos anuales ascienden a **{gastos_anuales_estimados:,.2f} €**. "
             f"Si logras acumular tu número objetivo invertido, podrías retirar un 4% cada año de por vida sin que el dinero se acabe jamás.")

# ------------------------------------------
# PESTAÑA 6: CONSULTORÍA DE IA
# ------------------------------------------
with tab_ia:
    st.subheader("🤖 Consultor Estratégico de IA")
    if not api_key_input:
        st.warning("🔒 Esta pestaña es exclusiva para los informes de la IA. Para activarla, introduce tu Gemini API Key en la barra lateral izquierda.")
    else:
        if st.button("🚀 Solicitar Dictamen Financiero Personalizado"):
            try:
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Actúa como el mejor asesor financiero. Analiza este mapa completo:
                - Ingresos netos: {ingresos_mensuales} € | Ahorro total: {ahorro_mensual_total} €
                - Capital acumulado hoy: {capital_inicial} € | Inversión mensual simulada: {aportacion_mensual_calculada} € a {anos_inversion} años
                - Aceleradores: Mensual extra de {amortizacion_extra} € e Inyección única de {inyeccion_capital_unica} €
                - Hipoteca: Préstamo original de {capital_original} €. Debe {capital_pendiente} € en {tipo_hipoteca} al {interes_anual_actual}%. Cuota de {cuota_mensual_actual} €/mes.
                - SEGUROS VINCULADOS: {seguros_anuales_banco} € al año (añade {coste_mensual_seguros:.2f} €/mes ocultos haciendo una cuota real de {cuota_real_total:.2f} €/mes).
                - Desglose de cuota base: {capital_este_mes:.2f} € van a casa y {interes_este_mes:.2f} € a intereses.
                - Tiempo restante contrato: {anos_normal:.1f} años.
                - Meta libertad financiera: {num_libertad} €
                
                Redacta tu dictamen estructurado en estos tres bloques directos y profesionales:
                1. **EL IMPACTO DE LAS VINCULACIONES (Alerta de sobrecoste):** Analiza el peso de los seguros. Explica si le conviene mantenerlos o si habitualmente compensa perder la bonificación bancaria a cambio de contratar seguros libres.
                2. **ESTRATEGIA OPTIMIZADA DE DESAPALANCAMIENTO VS INVERSIÓN:** Con los números en la mano, calcula si el capital de las inyecciones rinde más matando esta estructura de hipoteca o en fondos indexados globales al 7%.
                3. **HOJA DE RUTA DE VEHÍCULOS DE INVERSIÓN:** Nombra opciones reales (Cuentas remuneradas, Fondos Indexados de bajo coste de Vanguard/Amundi o Robo-advisors) ideales para este perfil.
                """
                
                with st.spinner("La IA está cruzando los datos..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"Hubo un problema con la IA: {e}")
