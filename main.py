import streamlit as st
import google.generativeai as genai
import pandas as pd
import math

# Configuración de página limpia y ancha
st.set_page_config(page_title="Cuadro de Mandos Financiero Pro", layout="wide")

# CSS para centrar las pestañas en la pantalla (Tu marca roja)
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 TU DASHBOARD FINANCIERO INTEGRAL")
st.write("Gestiona tu patrimonio de forma centralizada. Datos globales a la izquierda; herramientas y gráficos en cada pestaña.")

# ==========================================
# ⚙️ 1. BARRA LATERAL (SOLO PARA LO GLOBAL E IA)
# ==========================================
st.sidebar.title("⚙️ Datos Globales")

# Configuración de la IA
with st.sidebar.expander("🔑 Configuración de IA", expanded=True):
    api_key_input = st.text_input("Introduce tu Gemini API Key:", type="password")
    if not api_key_input:
        st.caption("🔒 IA en espera. El dashboard funciona al 100% sin clave.")

# Tus Datos Económicos Básicos (Tu marca rosa)
with st.sidebar.expander("📥 Tus datos económicos", expanded=True):
    ingresos_mensuales = st.number_input("Ingresos mensuales netos (€)", value=2000, step=100)
    dinero_extra_anual = st.number_input("Ingresos extras anuales (Pagas, bonus...) (€)", value=0, step=500)
    ahorro_mensual_total = st.number_input("Ahorro neto total al mes (€)", value=500, step=50)
    capital_inicial = st.number_input("Dinero líquido en cuenta (€)", value=5000, step=500)


# Prorrateo global de ingresos extras para los cálculos
ingreso_mensual_extra_prorrateado = dinero_extra_anual / 12
ingresos_totales_calculados = ingresos_mensuales + ingreso_mensual_extra_prorrateado
gastos_mensuales_calculados = ingresos_totales_calculados - ahorro_mensual_total
gastos_anuales_estimados = gastos_mensuales_calculados * 12
num_libertad = gastos_anuales_estimados * 25


# ==========================================
# 🗂️ 2. DECLARACIÓN DE PESTAÑAS (CENTRADAS)
# ==========================================
tab_resumen, tab_presupuesto, tab_inversion, tab_hipoteca, tab_libertad, tab_ia = st.tabs([
    "📊 Vista General", 
    "🥗 Presupuesto 50/30/20", 
    "📈 Rendimiento de Inversiones", 
    "🏠 Escáner Hipoteca", 
    "🕊️ Libertad Financiera",
    "🤖 Consultor IA"
])


# ==========================================
# 📥 3. RECOGIDA DE INPUTS ESPECÍFICOS EN SUS PESTAÑAS
# (Colocamos los inputs arriba para calcular antes de mostrar la Vista General)
# ==========================================

# --- CONTROLES DE LA PESTAÑA INVERSIÓN ---
with tab_inversion:
    st.subheader("💼 Tus Activos Actuales e Inversiones")
    st.write("Introduce tu patrimonio actual y configura la calculadora financiera en la parte superior:")
    
    col_act1, col_act2, col_act3 = st.columns(3)
    with col_act1:
        valor_inmuebles = st.number_input("Valor total de tus propiedades/viviendas (€)", value=0, step=5000)
    with col_act2:
        valor_etfs = st.number_input("Valor actual de tus ETFs / Acciones (€)", value=0, step=1000)
    with col_act3:
        valor_otros = st.number_input("Otros activos (Planes, Cripto...) (€)", value=0, step=500)
        
    patrimonio_neto_total = capital_inicial + valor_inmuebles + valor_etfs + valor_otros
    
    st.markdown("#### 🧮 Calculadora Financiera Multiopción")
    tipo_inversion = st.selectbox("¿Qué modalidad de inversión quieres simular?", 
                                  ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "ROI Simple"])
    
    # Inputs específicos según calculadora
    if tipo_inversion == "Interés Compuesto (ETFs / Fondos)":
        c1, c2, c3 = st.columns(3)
        with c1: cap_sim_inicial = st.number_input("Capital inicial simulación (€)", value=float(capital_inicial), step=1000.0)
        with c2: aport_sim_mensual = st.number_input("Aportación mensual (€/mes)", value=float(ahorro_mensual_total), step=50.0)
        with c3: anos_simulacion = st.slider("Años a proyectar en el gráfico", 1, 40, 15)
    elif tipo_inversion == "Rentabilidad Inmobiliaria (Ladrillo)":
        cc1, cc2, cc3, cc4 = st.columns(4)
        with cc1: precio_compra = st.number_input("Precio compra vivienda (€)", value=100000, step=5000)
        with cc2: gastos_iniciales = st.number_input("Impuestos y reformas (€)", value=12000, step=1000)
        with cc3: alquiler_mensual = st.number_input("Alquiler mensual bruto (€)", value=600, step=50)
        with cc4: gastos_anuales_vivienda = st.number_input("Gastos anuales (IBI, Comunidad...) (€)", value=1000, step=100)
    elif tipo_inversion == "ROI Simple":
        cx1, cx2 = st.columns(2)
        with cx1: capital_invertido_roi = st.number_input("Dinero total invertido (€)", value=10000, step=500)
        with cx2: valor_final_roi = st.number_input("Valor actual / final alcanzado (€)", value=13500, step=500)


# --- CONTROLES DE LA PESTAÑA HIPOTECA ---
with tab_hipoteca:
    st.subheader("🏠 Configuración y Escáner de tu Hipoteca")
    st.write("Introduce las condiciones de tu préstamo bancario para analizar los costes reales:")
    
    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1: tipo_hipoteca = st.selectbox("Tipo de Hipoteca", ["Fija", "Variable", "Mixta"])
    with col_h2: capital_original = st.number_input("Préstamo original (€)", value=150000, step=5000)
    with col_h3: capital_pendiente = st.number_input("Capital pendiente actual (€)", value=120000, step=5000)
    with col_h4: interes_anual_actual = st.number_input("Interés anual (%)", value=3.5, step=0.1)
    
    col_h5, col_h6, col_h7, col_h8 = st.columns(4)
    with col_h5: cuota_mensual_actual = st.number_input("Cuota mensual del recibo (€)", value=600, step=50)
    with col_h6: seguros_anuales_banco = st.number_input("Seguros anuales vinculados (€)", value=400, step=50)
    with col_h7: amortizacion_extra = st.number_input("Amortización mensual extra (€/mes)", value=0, step=50)
    with col_h8: inyeccion_capital_unica = st.number_input("Inyección de capital puntual (€)", value=0, step=1000)

    # Cálculos matemáticos internos de la hipoteca
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


# ==========================================
# 📊 4. RENDERIZADO DE RESULTADOS (DE ABAJO HACIA ARRIBA)
# ==========================================

# --- PESTAÑA 1: VISTA GENERAL (Tus 4 bloques clave restaurados) ---
with tab_resumen:
    st.subheader("🏁 Resumen Ejecutivo de tu Salud Financiera")
    st.write("Una instantánea global cruzando la información de todas tus pestañas:")
    
    c_v1, c_v2 = st.columns(2)
    with c_v1:
        with st.container(border=True):
            st.markdown("#### 1. Presupuesto Inteligente (50/30/20)")
            tasa_ahorro = (ahorro_mensual_total / ingresos_totales_calculados) * 100
            st.metric("Tu Tasa de Ahorro Real", f"{tasa_ahorro:.1f}%", f"{ahorro_mensual_total} €/mes guardados")
            st.caption(f"Tus ingresos mensuales ponderados son de {ingresos_totales_calculados:,.2f} €.")
            
        with st.container(border=True):
            st.markdown("#### 2. Tu Patrimonio e Inversión")
            st.metric("Patrimonio Neto Calculado", f"{patrimonio_neto_total:,.2f} €", f"Líquido: {capital_inicial} €")
            st.caption(f"Calculadora activa en modo: **{tipo_inversion}**.")

    with c_v2:
        with st.container(border=True):
            st.markdown("#### 3. Estado de tu Hipoteca")
            st.metric("Cuota Real Mensual", f"{cuota_real_total:,.2f} €", f"Recibo + {coste_mensual_seguros:.1f} €/mes en seguros", delta_color="inverse")
            st.metric("Tiempo pendiente de contrato", f"{anos_normal:.1f} años", f"{intereses_totales_normal:,.2f} € pendientes por regalar al banco", delta_color="inverse")

        with st.container(border=True):
            st.markdown("#### 4. Tu Libertad Financiera")
            st.metric("Meta de Capital (Regla del 4%)", f"{num_libertad:,.0f} €")
            porcentaje_meta = (patrimonio_neto_total / num_libertad) * 100 if num_libertad > 0 else 0
            st.progress(min(porcentaje_meta / 100, 1.0))
            st.caption(f"Llevas completado el **{porcentaje_meta:.1f}%** de tu libertad financiera.")


# --- PESTAÑA 2: PRESUPUESTO ---
with tab_presupuesto:
    st.markdown("---")
    st.markdown("### 📊 Gráficas y Distribución del Presupuesto")
    nec = ingresos_totales_calculados * 0.5
    cap = ingresos_totales_calculados * 0.3
    aho = ingresos_totales_calculados * 0.2
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.info(f"• **🏠 Necesidades básicas (50%):** Máximo {nec:,.2f} €/mes\n\n"
                f"• **🎉 Caprichos y Ocio (30%):** Máximo {cap:,.2f} €/mes\n\n"
                f"• **🐷 Ahorro recomendado (20%):** Deberías guardar {aho:,.2f} €/mes")
        st.success(f"👏 Tu configuración actual guarda **{ahorro_mensual_total:,.2f} €/mes**.")
    with col_p2:
        df_presupuesto = pd.DataFrame({
            "Importe (€)": [nec, cap, aho, ahorro_mensual_total]
        }, index=["Necesidades (50%)", "Caprichos (30%)", "Ahorro Rec. (20%)", "Tu Ahorro Real"])
        st.bar_chart(df_presupuesto)


# --- PESTAÑA 3: RENDIMIENTO DE INVERSIONES (RESULTADOS GRÁFICOS ABAJO) ---
with tab_inversion:
    st.markdown("---")
    st.markdown("### 📊 Gráficas de Rendimiento y Análisis Financiero")
    
    if tipo_inversion == "Interés Compuesto (ETFs / Fondos)":
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
            
    elif tipo_inversion == "Rentabilidad Inmobiliaria (Ladrillo)":
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
        }, index=["Ingresos Brutos", "Gastos Operativos", "Beneficio Neto"])
        st.bar_chart(df_inmo)
        
    elif tipo_inversion == "ROI Simple":
        beneficio_neto_roi = valor_final_roi - capital_invertido_roi
        roi_porcentaje = (beneficio_neto_roi / capital_invertido_roi) * 100 if capital_invertido_roi > 0 else 0
        col_r1, col_r2 = st.columns(2)
        col_r1.metric("Beneficio Neto Limpio", f"{beneficio_neto_roi:,.2f} €")
        col_r2.metric("Retorno Inversión (ROI)", f"{roi_porcentaje:.2f}%")


# --- PESTAÑA 4: RESULTADOS HIPOTECA ---
with tab_hipoteca:
    st.markdown("---")
    st.markdown("### 📊 Resultados del Análisis Hipotecario")
    
    if anos_normal == 0:
        st.error("Revisa los datos de la hipoteca en la parte superior.")
    else:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("#### Desglose de tu recibo mensual:")
            df_cuota = pd.DataFrame({
                "Euros (€)": [capital_este_mes, interes_este_mes, coste_mensual_seguros]
            }, index=["Capital (Tu Bolsillo)", "Intereses (Banco)", "Seguros (Coste Oculto)"])
            st.bar_chart(df_cuota)
        with col_g2:
            st.markdown("#### Diagnóstico de Deuda:")
            st.info(f"• **Años restantes por contrato:** {anos_normal:.1f} años\n\n"
                    f"• **Intereses totales pendientes:** {intereses_totales_normal:,.2f} €")

        # Impacto amortización extra
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
                st.markdown("### 🔥 Resultados de la Estrategia de Aceleración")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric("Años ahorrados al banco", f"{anos_ahorrados:.1f} años antes")
                    st.metric("Dinero salvado en intereses", f"{dinero_ahorrado_interes:,.2f} €")
                with col_m2:
                    df_intereses = pd.DataFrame({
                        "Intereses (€)": [intereses_totales_normal, intereses_totales_extra]
                    }, index=["Sin Acelerador", "Con Acelerador"])
                    st.bar_chart(df_intereses)


# --- PESTAÑA 5: LIBERTAD FINANCIERA ---
with tab_libertad:
    st.subheader("🕊️ Tu Meta de Libertad Financiera (Regla del 4%)")
    st.error(f"## 🎯 TU NÚMERO OBJETIVO: {num_libertad:,.2f} €")
    st.write(f"Tus gastos anuales proyectados son de **{gastos_anuales_estimados:,.2f} €**. "
             f"Alcanzando esta meta invertida, el rendimiento anual medio cubrirá tu vida de por vida.")


# --- PESTAÑA 6: CONSULTORÍA DE IA ---
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
