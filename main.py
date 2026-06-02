import streamlit as st
import google.generativeai as genai
import pandas as pd
import math

# Configuración de página limpia y ancha
st.set_page_config(page_title="Cuadro de Mandos Financiero Pro", layout="wide")

# Inyección de CSS para centrar las pestañas (Tu marca roja)
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 TU DASHBOARD FINANCIERO INTEGRAL")
st.write("Gestiona tu patrimonio, optimiza tu hipoteca y proyecta tus inversiones en un entorno limpio y centralizado.")

# ==========================================
# 🛠️ BARRA LATERAL CON DESPLEGABLES REESTRUCTURADOS
# ==========================================
st.sidebar.title("⚙️ Panel de Control")

# Desplegable 1: Configuración de la IA
with st.sidebar.expander("🔑 Configuración de IA", expanded=True):
    api_key_input = st.text_input("Introduce tu Gemini API Key:", type="password")
    if not api_key_input:
        st.caption("🔒 IA en espera. Las calculadoras y gráficas funcionan al 100% sin clave.")

# Desplegable 2: Tus Datos Económicos (Tu marca rosa)
with st.sidebar.expander("📥 Tus datos económicos", expanded=False):
    ingresos_mensuales = st.number_input("Ingresos mensuales netos (€)", value=2000, step=100)
    dinero_extra_anual = st.number_input("Ingresos extras anuales (Pagas extra, bonus...) (€)", value=0, step=500)
    ahorro_mensual_total = st.number_input("Ahorro neto total al mes (€)", value=500, step=50)
    capital_inicial = st.number_input("Dinero en cuenta/efectivo (€)", value=5000, step=500)

# Desplegable 3: Tus Inversiones Actuales (NUEVA PETICIÓN)
with st.sidebar.expander("📈 Tus Inversiones Actuales", expanded=False):
    st.caption("Añade tus activos para calcular tu patrimonio neto total.")
    valor_inmuebles = st.number_input("Valor de propiedades/viviendas (€)", value=0, step=5000)
    valor_etfs = st.number_input("Valor en ETFs / Acciones (€)", value=0, step=1000)
    valor_otros = st.number_input("Otros activos (Fondos, Cripto...) (€)", value=0, step=500)

# Desplegable 4: Tu Hipoteca (Tu marca azul - Todo unificado)
with st.sidebar.expander("🏠 Tu Hipoteca", expanded=False):
    tipo_hipoteca = st.selectbox("Tipo de Hipoteca", ["Fija", "Variable", "Mixta"])
    capital_original = st.number_input("Préstamo original (€)", value=150000, step=5000)
    capital_pendiente = st.number_input("Capital pendiente actual (€)", value=120000, step=5000)
    cuota_mensual_actual = st.number_input("Cuota mensual del recibo (€)", value=600, step=50)
    interes_anual_actual = st.number_input("Interés anual actual (%)", value=3.5, step=0.1)
    
    st.markdown("---")
    st.markdown("**🛡️ Gastos Vinculados:**")
    seguros_anuales_banco = st.number_input("Coste ANUAL de seguros del banco (€)", value=400, step=50)
    
    st.markdown("---")
    st.markdown("**⚡ Aceleradores de Capital:**")
    amortizacion_extra = st.number_input("Aportación extra mensual (€/mes)", value=0, step=50)
    inyeccion_capital_unica = st.number_input("Inyección única / Puntual (€)", value=0, step=1000)


# ==========================================
# 🧮 MOTOR DE CÁLCULO INTERNO
# ==========================================
# Prorrateo de ingresos extras
ingreso_mensual_extra_prorrateado = dinero_extra_anual / 12
ingresos_totales_calculados = ingresos_mensuales + ingreso_mensual_extra_prorrateado

gastos_mensuales_calculados = ingresos_totales_calculados - ahorro_mensual_total
gastos_anuales_estimados = gastos_mensuales_calculados * 12

# Patrimonio Neto Total
patrimonio_neto_total = capital_inicial + valor_inmuebles + valor_etfs + valor_otros

# Matemáticas de la hipoteca
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
# 🗂️ PESTAÑAS CENTRALES (CENTRADAS POR CSS)
# ==========================================
tab_resumen, tab_presupuesto, tab_calculadora, tab_hipoteca, tab_libertad, tab_ia = st.tabs([
    "📊 Vista General", 
    "🥗 Presupuesto 50/30/20", 
    "🧮 Calculadora de Inversión", 
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
    col1.metric("Patrimonio Neto Total", f"{patrimonio_neto_total:,.2f} €", f"Efectivo: {capital_inicial} €")
    col2.metric("Tasa de Ahorro Real", f"{((ahorro_mensual_total/ingresos_totales_calculados)*100):.1f}%", f"{ahorro_mensual_total} €/mes")
    col3.metric("Cuota Real Hipoteca", f"{cuota_real_total:,.2f} €", f"+{coste_mensual_seguros:.1f} €/mes seguros", delta_color="inverse")
    
    num_libertad = gastos_anuales_estimados * 25
    col4.metric("Meta Libertad Financiera", f"{num_libertad:,.0f} €")
    
    if dinero_extra_anual > 0:
        st.caption(f"ℹ️ Tus ingresos mensuales se han incrementado en +{ingreso_mensual_extra_prorrateado:,.2f} €/mes debido a tus pagas/ingresos extras anuales.")

# ------------------------------------------
# PESTAÑA 2: REGLA 50/30/20
# ------------------------------------------
with tab_presupuesto:
    st.subheader("🥗 Distribución del Presupuesto Mensual")
    nec = ingresos_totales_calculados * 0.5
    cap = ingresos_totales_calculados * 0.3
    aho = ingresos_totales_calculados * 0.2
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown(f"**Distribución para tus ingresos totales ({ingresos_totales_calculados:,.2f} €/mes):**")
        st.info(f"• **🏠 Necesidades (50%):** Máximo {nec:,.2f} €/mes\n\n"
                f"• **🎉 Caprichos (30%):** Máximo {cap:,.2f} €/mes\n\n"
                f"• **🐷 Ahorro Sugerido (20%):** Deberías guardar {aho:,.2f} €/mes")
        st.success(f"👏 Tu ahorro real actual es de **{ahorro_mensual_total:,.2f} €/mes**.")

    with col_p2:
        df_presupuesto = pd.DataFrame({
            "Importe (€)": [nec, cap, aho, ahorro_mensual_total]
        }, index=["Necesidades (50%)", "Caprichos (30%)", "Ahorro Rec. (20%)", "Tu Ahorro Real"])
        st.bar_chart(df_presupuesto)

# ------------------------------------------
# PESTAÑA 3: CALCULADORA FINANCIERA MULTIÓPCIÓN (NUEVA PETICIÓN)
# ------------------------------------------
with tab_calculadora:
    st.subheader("🧮 Calculadora Financiera de Opciones de Inversión")
    
    tipo_inversion = st.selectbox("¿Qué tipo de inversión quieres calcular?", 
                                  ["Interés Compuesto (ETFs / Acciones)", "Rentabilidad Inmobiliaria (Viviendas)", "ROI de Inversión Simple"])
    
    st.markdown("---")
    
    if tipo_inversion == "Interés Compuesto (ETFs / Acciones)":
        st.markdown("#### 📈 Proyección de Interés Compuesto")
        c1, c2, c3 = st.columns(3)
        with c1:
            capital_inv_inicial = st.number_input("Capital inicial para esta simulación (€)", value=float(capital_inicial))
        with c2:
            aportacion_mensual = st.number_input("Aportación mensual (€/mes)", value=float(ahorro_mensual_total - amortizacion_extra))
        with c3:
            anos_simulacion = st.slider("Años de simulación", 1, 40, 15)
            
        interes_estimado = 0.07 # 7% promedio de mercado indexado
        lista_anos = []
        lista_capital = []
        tot = capital_inv_inicial
        
        for ano in range(1, anos_simulacion + 1):
            tot = (tot + (aportacion_mensual * 12)) * (1 + interes_estimado)
            lista_anos.append(f"Año {ano}")
            lista_capital.append(tot)
            
        col_res1, col_res2 = st.columns([1, 2])
        with col_res1:
            st.metric("Capital Final Estimado", f"{tot:,.2f} €")
            st.metric("Intereses Puros Generados", f"{tot - (capital_inv_inicial + (aportacion_mensual*12*anos_simulacion)):,.2f} €")
        with col_res2:
            df_compuesto = pd.DataFrame({"Evolución del Capital (€)": lista_capital}, index=lista_anos)
            st.line_chart(df_compuesto)
            
    elif tipo_inversion == "Rentabilidad Inmobiliaria (Viviendas)":
        st.markdown("#### 🏠 Simulador de Inversión en Ladrillo")
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            precio_compra = st.number_input("Precio de compra de la vivienda (€)", value=100000, step=5000)
            gastos_reforma_impuestos = st.number_input("Gastos iniciales (Notaría, reformas, ITP...) (€)", value=12000, step=1000)
        with cc2:
            alquiler_mensual = st.number_input("Alquiler mensual que vas a cobrar (€)", value=600, step=50)
        with cc3:
            gastos_anuales_vivienda = st.number_input("Gastos anuales (IBI, seguro, comunidad...) (€)", value=1000, step=100)
            
        inversion_total_real = precio_compra + gastos_reforma_impuestos
        ingresos_anuales_brutos = alquiler_mensual * 12
        ingresos_anuales_netos = ingresos_anuales_brutos - gastos_anuales_vivienda
        
        rentabilidad_bruta = (ingresos_anuales_brutos / inversion_total_real) * 100
        rentabilidad_neta = (ingresos_anuales_netos / inversion_total_real) * 100
        
        st.markdown("##### 🏁 Resultados del Análisis Inmobiliario:")
        col_in1, col_in2, col_in3 = st.columns(3)
        col_in1.metric("Inversión Total Real realizada", f"{inversion_total_real:,.2f} €")
        col_in2.metric("Rentabilidad BRUTA Anual", f"{rentabilidad_bruta:.2f}%")
        col_in3.metric("Rentabilidad NETA Anual", f"{rentabilidad_neta:.2f}%")
        
        df_inmo = pd.DataFrame({
            "Importe Anual (€)": [ingresos_anuales_brutos, gastos_anuales_vivienda, ingresos_anuales_netos]
        }, index=["Ingresos Brutos", "Gastos de Operación", "Beneficio Limpio (Neto)"])
        st.bar_chart(df_inmo)
        
    elif tipo_inversion == "ROI de Inversión Simple":
        st.markdown("#### 🧮 Cálculo de Retorno de Inversión (ROI) Genérico")
        cx1, cx2 = st.columns(2)
        with cx1:
            capital_invertido_roi = st.number_input("Cantidad de dinero invertida (€)", value=10000, step=500)
        with cx2:
            valor_final_roi = st.number_input("Valor final obtenido / actual (€)", value=13500, step=500)
            
        beneficio_neto_roi = valor_final_roi - capital_invertido_roi
        roi_porcentaje = (beneficio_neto_roi / capital_invertido_roi) * 100 if capital_invertido_roi > 0 else 0
        
        col_r1, col_r2 = st.columns(2)
        col_r1.metric("Beneficio Neto Limpio", f"{beneficio_neto_roi:,.2f} €")
        col_r2.metric("Retorno de la Inversión (ROI)", f"{roi_porcentaje:.2f}%")

# ------------------------------------------
# PESTAÑA 4: ESCÁNER DE HIPOTECA
# ------------------------------------------
with tab_hipoteca:
    st.subheader("🏠 Radiografía y Optimización de la Hipoteca")
    
    if anos_normal == 0:
        st.error("La cuota mensual debe ser superior a los intereses devengados.")
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
            st.info(f"• **Porcentaje pagado de la propiedad:** {porcentaje_pagado:.1f}%\n\n"
                    f"• **Años restantes por contrato:** {anos_normal:.1f} años\n\n"
                    f"• **Intereses pendientes de pago:** {intereses_totales_normal:,.2f} €")

        # Efecto de aceleradores
        capital_pendiente_neto = capital_pendiente - inyeccion_capital_unica
        if inyeccion_capital_unica >= capital_pendiente:
            st.success("🎉 ¡HACHAZO INMEDIATO! Deuda liquidada por completo.")
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
                st.markdown("### 🔥 Impacto de tus Aceleradores")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric("Años que le quitas al banco", f"{anos_ahorrados:.1f} años antes", f"Baja a {anos_extra:.1f} años")
                    st.metric("Dinero salvado en intereses", f"{dinero_ahorrado_interes:,.2f} €")
                with col_m2:
                    df_intereses = pd.DataFrame({
                        "Intereses (€)": [intereses_totales_normal, intereses_totales_extra]
                    }, index=["Intereses Sin Extras", "Intereses Con Extras"])
                    st.bar_chart(df_intereses)

# ------------------------------------------
# PESTAÑA 5: LIBERTAD FINANCIERA
# ------------------------------------------
with tab_libertad:
    st.subheader("🕊 extinction Opciones de Libertad Financiera (Regla del 4%)")
    st.error(f"## 🎯 TU NÚMERO OBJETIVO: {num_libertad:,.2f} €")
    st.write(f"Tus gastos anuales proyectados son de **{gastos_anuales_estimados:,.2f} €**. "
             f"Alcanzando esta meta invertida, la rentabilidad anual cubrirá tu ritmo de vida de por vida.")

# ------------------------------------------
# PESTAÑA 6: CONSULTORÍA DE IA
# ------------------------------------------
with tab_ia:
    st.subheader("🤖 Consultor Estratégico de IA")
    if not api_key_input:
        st.warning("🔒 Introduce tu Gemini API Key en la barra lateral para que la IA estudie tu nuevo patrimonio neto total.")
    else:
        if st.button("🚀 Generar Dictamen Financiero Avanzado"):
            try:
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Actúa como un asesor financiero de élite. Analiza este mapa patrimonial completo:
                - Ingresos base: {ingresos_mensuales} € | Ingresos extras anuales: {dinero_extra_anual} € (Prorrateo mensual total: {ingresos_totales_calculados:.2f} €)
                - Ahorro mensual: {ahorro_mensual_total} €
                
                PATRIMONIO NETO ACTUAL: {patrimonio_neto_total} € 
                (Desglose: Efectivo {capital_inicial} €, Inmuebles {valor_inmuebles} €, ETFs/Acciones {valor_etfs} €, Otros {valor_otros} €)
                
                HIPOTECA Y DEUDA:
                - Debe {capital_pendiente} € de un préstamo original de {capital_original} € ({tipo_hipoteca} al {interes_anual_actual}%).
                - Cuota del recibo: {cuota_mensual_actual} €/mes.
                - SEGUROS VINCULADOS AL BANCO: {seguros_anuales_banco} € al año (coste oculto prorrateado de {coste_mensual_seguros:.2f} €/mes, cuota real: {cuota_real_total:.2f} €/mes).
                - Aceleradores configurados: Extra mensual de {amortizacion_extra} €/mes e Inyección puntual de {inyeccion_capital_unica} €.
                - Meta de Libertad Financiera: {num_libertad} €
                
                Redacta un informe estratégico estructurado en:
                1. **EVALUACIÓN DEL PATRIMONIO NETO Y PERFIL DE RIESGO:** Analiza su nivel de diversificación actual en base a sus activos.
                2. **EL DILEMA DE LOS SEGUROS VINCULADOS:** Determina si el coste de {seguros_anuales_banco} €/año justifica la bonificación del interés o si debe buscar un seguro libre.
                3. **DÓNDE COLOCAR EL DINERO EXTRA:** Analiza si es mejor usar el capital de aceleración en amortizar hipoteca o en alimentar su cartera de inversión para acelerar el interés compuesto.
                """
                
                with st.spinner("La IA está analizando tu ecosistema financiero integral..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"Error con el motor de IA: {e}")
