import streamlit as st
import google.generativeai as genai
import pandas as pd
import math

# Configuración de página limpia y ancha
st.set_page_config(page_title="Cuadro de Mandos Financiero Pro", layout="wide")

# CSS para centrar las pestañas en la pantalla (Marca roja)
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 TU DASHBOARD FINANCIERO INTEGRAL")
st.write("Modifica tus datos en la barra lateral izquierda y observa los resúmenes y gráficas centralizados al instante.")

# ==========================================
# ⚙️ BARRA LATERAL IZQUIERDA (TODO LO EDITABLE AQUÍ)
# ==========================================
st.sidebar.title("⚙️ Panel de Control")

# 1. Configuración de la IA
with st.sidebar.expander("🔑 Configuración de IA", expanded=True):
    api_key_input = st.text_input("Introduce tu Gemini API Key:", type="password")
    if not api_key_input:
        st.caption("🔒 IA en espera. El dashboard funciona al 100% sin clave.")

# 2. Tus Datos Económicos (Marca rosa con dinero extra)
with st.sidebar.expander("📥 Tus datos económicos", expanded=False):
    ingresos_mensuales = st.number_input("Ingresos mensuales netos (€)", value=2000, step=100)
    dinero_extra_anual = st.number_input("Ingresos extras anuales (Pagas, bonus...) (€)", value=0, step=500)
    ahorro_mensual_total = st.number_input("Ahorro neto total al mes (€)", value=500, step=50)
    capital_inicial = st.number_input("Dinero en cuenta/efectivo (€)", value=5000, step=500)

# 3. Tus Inversiones Actuales y Calculadora (Inputs de inversión en el lateral)
with st.sidebar.expander("💼 Tus Inversiones y Calculadora", expanded=False):
    st.markdown("**Patrimonio Actual:**")
    valor_inmuebles = st.number_input("Valor de propiedades/viviendas (€)", value=0, step=5000)
    valor_etfs = st.number_input("Valor en ETFs / Acciones (€)", value=0, step=1000)
    valor_otros = st.number_input("Otros activos (Fondos, Cripto...) (€)", value=0, step=500)
    
    st.markdown("---")
    st.markdown("**🧮 Configurar Calculadora Financiera:**")
    tipo_inversion = st.selectbox("Tipo de inversión a simular:", 
                                  ["Interés Compuesto (ETFs)", "Rentabilidad Inmobiliaria", "ROI Simple"])
    
    # Inputs condicionales de las calculadoras dentro del lateral
    if tipo_inversion == "Interés Compuesto (ETFs)":
        cap_sim_inicial = st.number_input("Capital inicial simulación (€)", value=float(capital_inicial), step=1000.0)
        aport_sim_mensual = st.number_input("Aportación mensual (€/mes)", value=float(ahorro_mensual_total), step=50.0)
        anos_simulacion = st.slider("Años a proyectar", 1, 40, 15)
    elif tipo_inversion == "Rentabilidad Inmobiliaria":
        precio_compra = st.number_input("Precio compra vivienda (€)", value=100000, step=5000)
        gastos_iniciales = st.number_input("Impuestos y reformas (€)", value=12000, step=1000)
        alquiler_mensual = st.number_input("Alquiler mensual esperado (€)", value=600, step=50)
        gastos_anuales_vivienda = st.number_input("Gastos anuales (IBI, comunidad...) (€)", value=1000, step=100)
    elif tipo_inversion == "ROI Simple":
        capital_invertido_roi = st.number_input("Dinero invertido (€)", value=10000, step=500)
        valor_final_roi = st.number_input("Valor final obtenido (€)", value=13500, step=500)

# 4. Tu Hipoteca (Marca azul - Todo unificado y editable)
with st.sidebar.expander("🏠 Tu Hipoteca", expanded=False):
    tipo_hipoteca = st.selectbox("Tipo de Hipoteca", ["Fija", "Variable", "Mixta"])
    capital_original = st.number_input("Préstamo original (€)", value=150000, step=5000)
    capital_pendiente = st.number_input("Capital pendiente actual (€)", value=120000, step=5000)
    cuota_mensual_actual = st.number_input("Cuota mensual del recibo (€)", value=600, step=50)
    interes_anual_actual = st.number_input("Interés anual actual (%)", value=3.5, step=0.1)
    seguros_anuales_banco = st.number_input("Coste ANUAL de seguros bancarios (€)", value=400, step=50)
    amortizacion_extra = st.number_input("Aportación extra mensual (€/mes)", value=0, step=50)
    inyeccion_capital_unica = st.number_input("Inyección única / Puntual (€)", value=0, step=1000)


# ==========================================
# 🧮 MOTOR INTERNO DE CÁLCULO
# ==========================================
# Prorrateo de ingresos extras
ingreso_mensual_extra_prorrateado = dinero_extra_anual / 12
ingresos_totales_calculados = ingresos_mensuales + ingreso_mensual_extra_prorrateado
gastos_mensuales_calculados = ingresos_totales_calculados - ahorro_mensual_total
gastos_anuales_estimados = gastos_mensuales_calculados * 12

# Patrimonio Neto
patrimonio_neto_total = capital_inicial + valor_inmuebles + valor_etfs + valor_otros

# Matemáticas Hipoteca
tasa_m = (interes_anual_actual / 100) / 12
coste_mensual_seguros = seguros_anuales_banco / 12
cuota_real_total = cuota_mensual_actual + coste_mensual_seguros

if cuota_mensual_actual > (capital_pendiente * tasa_m):
    interes_este_mes = capital_pendiente * tasa_m
    capital_este_mes = cuota_mensual_actual - interes_este_mes
    meses_restantes_normal = -math.log(1 - (capital_pendiente * tasa_m) / cuota_mensual_actual) / math.log(1 + tasa_m)
    anos_normal = meses_restantes_normal / 12
    intereses_totales_normal = (cuota_mensual_actual * meses_restantes_normal) - capital_pendiente
else:
    interes_este_mes = capital_pendiente * tasa_m
    capital_este_mes = 0
    anos_normal = 0
    intereses_totales_normal = 0

# Meta de libertad financiera (Regla del 4%)
num_libertad = gastos_anuales_estimados * 25


# ==========================================
# 🗂️ PESTAÑAS CENTRALES (100% VISTAS Y RESÚMENES)
# ==========================================
tab_resumen, tab_presupuesto, tab_inversion, tab_hipoteca, tab_libertad, tab_ia = st.tabs([
    "📊 Vista General", 
    "🥗 Presupuesto 50/30/20", 
    "📈 Rendimiento de Inversiones", 
    "🏠 Escáner Hipoteca", 
    "🕊️ Libertad Financiera",
    "🤖 Consultor IA"
])

# ------------------------------------------
# PESTAÑA 1: VISTA GENERAL (RESUMEN INTEGRAL DE LAS 4 OPCIONES)
# ------------------------------------------
with tab_resumen:
    st.subheader("🏁 Resumen Ejecutivo de tu Salud Financiera")
    st.write("Una instantánea de tus 4 pilares financieros calculados de forma cruzada:")
    
    c_v1, c_v2 = st.columns(2)
    
    with c_v1:
        # Pilar 1: Presupuesto
        with st.container(border=True):
            st.markdown("#### 1. Presupuesto Inteligente (50/30/20)")
            tasa_ahorro = (ahorro_mensual_total / ingresos_totales_calculados) * 100
            st.metric("Tu Tasa de Ahorro Real", f"{tasa_ahorro:.1f}%", f"{ahorro_mensual_total} €/mes guardados")
            st.caption(f"Ingresos totales prorrateados: {ingresos_totales_calculados:,.2f} €/mes (incluye pagas extras).")
            
        # Pilar 2: Inversión y Patrimonio
        with st.container(border=True):
            st.markdown("#### 2. Proyección y Patrimonio Activo")
            st.metric("Patrimonio Neto Total", f"{patrimonio_neto_total:,.2f} €", f"Líquido en cuenta: {capital_inicial} €")
            st.caption(f"Simulador configurado actualmente en modo: **{tipo_inversion}** (Ver desglose en su pestaña).")

    with c_v2:
        # Pilar 3: Hipoteca
        with st.container(border=True):
            st.markdown("#### 3. Tu Hipoteca al mes")
            st.metric("Cuota Real Mensual", f"{cuota_real_total:,.2f} €", f"Incluye {coste_mensual_seguros:.1f} € de seguros ocultos", delta_color="inverse")
            st.metric("Tiempo restante por contrato", f"{anos_normal:.1f} años", f"{intereses_totales_normal:,.2f} € pendientes al banco", delta_color="inverse")

        # Pilar 4: Libertad Financiera
        with st.container(border=True):
            st.markdown("#### 4. Tu Libertad Financiera")
            st.metric("Meta Objetivo (Regla del 4%)", f"{num_libertad:,.0f} €")
            porcentaje_meta = (patrimonio_neto_total / num_libertad) * 100 if num_libertad > 0 else 0
            st.progress(min(porcentaje_meta / 100, 1.0))
            st.caption(f"Has completado el **{porcentaje_meta:.1f}%** de tu número de la libertad financiera.")

# ------------------------------------------
# PESTAÑA 2: BLOQUE PRESUPUESTO
# ------------------------------------------
with tab_presupuesto:
    st.subheader("🥗 Resumen del Presupuesto Mensual")
    nec = ingresos_totales_calculados * 0.5
    cap = ingresos_totales_calculados * 0.3
    aho = ingresos_totales_calculados * 0.2
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f"**Límites ideales recomendados para {ingresos_totales_calculados:,.2f} €/mes:**")
        st.info(f"• **🏠 Necesidades básicas (50%):** Máximo {nec:,.2f} €/mes\n\n"
                f"• **🎉 Caprichos y Ocio (30%):** Máximo {cap:,.2f} €/mes\n\n"
                f"• **🐷 Ahorro recomendado (20%):** Deberías guardar {aho:,.2f} €/mes")
        st.success(f"👏 Tu configuración real guarda **{ahorro_mensual_total:,.2f} €/mes**.")
    with col_p2:
        df_presupuesto = pd.DataFrame({
            "Importe (€)": [nec, cap, aho, ahorro_mensual_total]
        }, index=["Necesidades (50%)", "Caprichos (30%)", "Ahorro Rec. (20%)", "Tu Ahorro Real"])
        st.bar_chart(df_presupuesto)

# ------------------------------------------
# PESTAÑA 3: BLOQUE RENDIMIENTO DE INVERSIONES (RESUMEN INDIVIDUAL DE CALCULADORA)
# ------------------------------------------
with tab_inversion:
    st.subheader(f"🧮 Resumen de Simulación: {tipo_inversion}")
    
    if tipo_inversion == "Interés Compuesto (ETFs)":
        interes_estimado = 0.07
        lista_anos, lista_capital = [], []
        tot = cap_sim_inicial
        for ano in range(1, anos_simulacion + 1):
            tot = (tot + (aport_sim_mensual * 12)) * (1 + interes_estimado)
            lista_anos.append(f"Año {ano}")
            lista_capital.append(tot)
            
        col_res1, col_res2 = st.columns([1, 2])
        with col_res1:
            st.metric("Capital Final Estimado", f"{tot:,.2f} €")
            st.metric("Intereses Generados", f"{tot - (cap_sim_inicial + (aport_sim_mensual*12*anos_simulacion)):,.2f} €")
        with col_res2:
            df_compuesto = pd.DataFrame({"Evolución Patrimonio (€)": lista_capital}, index=lista_anos)
            st.line_chart(df_compuesto)
            
    elif tipo_inversion == "Rentabilidad Inmobiliaria":
        inversion_total_real = precio_compra + gastos_iniciales
        ingresos_anuales_brutos = alquiler_mensual * 12
        ingresos_anuales_netos = ingresos_anuales_brutos - gastos_anuales_vivienda
        rent_bruta = (ingresos_anuales_brutos / inversion_total_real) * 100
        rent_neta = (ingresos_anuales_netos / inversion_total_real) * 100
        
        col_in1, col_in2, col_in3 = st.columns(3)
        col_in1.metric("Inversión Total Real", f"{inversion_total_real:,.2f} €")
        col_in2.metric("Rentabilidad Bruta", f"{rent_bruta:.2f}%")
        col_in3.metric("Rentabilidad Neta Anual", f"{rent_neta:.2f}%")
        
        df_inmo = pd.DataFrame({
            "Importe Anual (€)": [ingresos_anuales_brutos, gastos_anuales_vivienda, ingresos_anuales_netos]
        }, index=["Ingresos Brutos", "Gastos de Operación", "Beneficio Neto"])
        st.bar_chart(df_inmo)
        
    elif tipo_inversion == "ROI Simple":
        beneficio_neto_roi = valor_final_roi - capital_invertido_roi
        roi_porcentaje = (beneficio_neto_roi / capital_invertido_roi) * 100 if capital_invertido_roi > 0 else 0
        col_r1, col_r2 = st.columns(2)
        col_r1.metric("Beneficio Neto Limpio", f"{beneficio_neto_roi:,.2f} €")
        col_r2.metric("Retorno Inversión (ROI)", f"{roi_porcentaje:.2f}%")

# ------------------------------------------
# PESTAÑA 4: BLOQUE ESCÁNER HIPOTECA
# ------------------------------------------
with tab_hipoteca:
    st.subheader("🏠 Análisis del Bloque de Hipoteca")
    
    if anos_normal == 0:
        st.error("Revisa los datos de la hipoteca en la barra lateral.")
    else:
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            st.markdown("#### Desglose del recibo mensual actual:")
            df_cuota = pd.DataFrame({
                "Euros (€)": [capital_este_mes, interes_este_mes, coste_mensual_seguros]
            }, index=["Capital (Tu Casa)", "Intereses (Banco)", "Seguros (Coste Oculto)"])
            st.bar_chart(df_cuota)
        with col_h2:
            st.markdown("#### Datos de Deuda:")
            st.info(f"• **Años por contrato:** {anos_normal:.1f} años\n\n"
                    f"• **Intereses totales pendientes:** {intereses_totales_normal:,.2f} €")

        # Aceleradores
        capital_pendiente_neto = capital_pendiente - inyeccion_capital_unica
        if amortizacion_extra > 0 or inyeccion_capital_unica > 0:
            cuota_con_extra = cuota_mensual_actual + amortizacion_extra
            if cuota_con_extra > (capital_pendiente_neto * tasa_m):
                meses_restantes_extra = -math.log(1 - (capital_pendiente_neto * tasa_m) / cuota_con_extra) / math.log(1 + tasa_m)
                anos_extra = meses_restantes_extra / 12
                total_pagado_extra = inyeccion_capital_unica + (cuota_con_extra * meses_restantes_extra)
                intereses_totales_extra = total_pagado_extra - capital_pendiente
                
                anos_ahorrados = anos_normal - anos_extra
                dinero_ahorrado_interes = intereses_totales_normal - intereses_totales_extra

                st.markdown("---")
                st.markdown("### 🔥 Impacto de la Amortización Extraordinaria")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric("Años ahorrados al banco", f"{anos_ahorrados:.1f} años antes")
                    st.metric("Dinero salvado en intereses", f"{dinero_ahorrado_interes:,.2f} €")
                with col_m2:
                    df_intereses = pd.DataFrame({
                        "Intereses (€)": [intereses_totales_normal, intereses_totales_extra]
                    }, index=["Sin Estrategia", "Con Estrategia"])
                    st.bar_chart(df_intereses)

# ------------------------------------------
# PESTAÑA 5: BLOQUE LIBERTAD FINANCIERA
# ------------------------------------------
with tab_libertad:
    st.subheader("🕊️ Tu Meta de Libertad Financiera (Regla del 4%)")
    st.error(f"## 🎯 TU NÚMERO OBJETIVO: {num_libertad:,.2f} €")
    st.write(f"Tus gastos anuales proyectados son de **{gastos_anuales_estimados:,.2f} €**. "
             f"Si logras acumular tu número objetivo invertido, la rentabilidad media cubrirá tus gastos de por vida sin agotar el capital.")

# ------------------------------------------
# PESTAÑA 6: CONSULTORÍA DE IA
# ------------------------------------------
with tab_ia:
    st.subheader("🤖 Informe Estratégico por Inteligencia Artificial")
    if not api_key_input:
        st.warning("🔒 Introduce tu Gemini API Key en la barra lateral para activar los informes de la IA.")
    else:
        if st.button("🚀 Solicitar Dictamen Financiero"):
            try:
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Actúa como un asesor financiero de élite. Analiza este mapa patrimonial:
                - Ingresos totales (con extras prorrateados): {ingresos_totales_calculados:.2f} €/mes
                - Ahorro mensual: {ahorro_mensual_total} €/mes
                - Patrimonio Neto: {patrimonio_neto_total} € (Efectivo: {capital_inicial} €, Inmuebles: {valor_inmuebles} €, ETFs: {valor_etfs} €, Otros: {valor_otros} €)
                - Hipoteca: Debe {capital_pendiente} € al {interes_anual_actual}%. Cuota recibo: {cuota_mensual_actual} €/mes. Seguros vinculados: {seguros_anuales_banco} €/año.
                - Meta libertad financiera: {num_libertad} €
                
                Genera un análisis profesional rápido de 3 bloques sobre su diversificación, los seguros del banco y si conviene usar el dinero extra en inversión o en liquidar hipoteca.
                """
                with st.spinner("La IA está cruzando los datos..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"Error con el motor de IA: {e}")
