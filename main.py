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
st.write("Gestiona tu patrimonio de forma centralizada. Datos globales a la izquierda; herramientas y gráficos dinámicos en cada pestaña.")

# ==========================================
# ⚙️ 1. INICIALIZACIÓN DE ESTADOS (SESSION STATE)
# ==========================================
# Creamos una inversión por defecto si la lista está vacía para que la app no empiece en blanco
if "inversiones" not in st.session_state:
    st.session_state.inversiones = [
        {
            "nombre": "Mi Primer Fondo Indexado",
            "tipo": "Interés Compuesto (ETFs / Fondos)",
            "valor_actual": 5000.0,
            "aportacion_mensual": 200.0,
            "interes_anual": 7.0,
            "precio_compra": 100000.0,
            "gastos_iniciales": 12000.0,
            "alquiler_mensual": 600.0,
            "gastos_anuales": 1000.0,
            "capital_invertido": 10000.0,
            "valor_final": 13500.0
        }
    ]

# ==========================================
# ⚙️ 2. BARRA LATERAL (SOLO PARA LO GLOBAL E IA)
# ==========================================
st.sidebar.title("⚙️ Datos Globales")

# Configuración de la IA
with st.sidebar.expander("🔑 Configuración de IA", expanded=False):
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
# 🗂️ 3. DECLARACIÓN DE PESTAÑAS (CENTRADAS)
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
# 📥 4. MOTOR DE CONFIGURACIÓN DINÁMICA DE INVERSIONES
# ==========================================
with tab_inversion:
    st.subheader("💼 Tus Activos Actuales e Inversiones")
    st.write("Añade, elimina y personaliza cada una de tus inversiones. Los filtros cambiarán según el tipo seleccionado.")

    # Botón dinámico para añadir una nueva inversión a la lista
    if st.button("➕ Añadir Nueva Inversión"):
        st.session_state.inversiones.append({
            "nombre": f"Inversión Nueva {len(st.session_state.inversiones) + 1}",
            "tipo": "Interés Compuesto (ETFs / Fondos)",
            "valor_actual": 0.0,
            "aportacion_mensual": 0.0,
            "interes_anual": 7.0,
            "precio_compra": 100000.0,
            "gastos_iniciales": 12000.0,
            "alquiler_mensual": 600.0,
            "gastos_anuales": 1000.0,
            "capital_invertido": 10000.0,
            "valor_final": 13500.0
        })

    # Inicializamos variables para consolidar datos globales
    patrimonio_inversiones_total = 0.0
    anos_proyeccion_horizonte = 15
    
    # Preparamos un diccionario para construir la gran gráfica global unificada
    cronologia_anos = list(range(1, anos_proyeccion_horizonte + 1))
    datos_grafica_global = {"Año": cronologia_anos}
    dict_graficas_individuales = {}

    # Iteramos sobre cada inversión guardada en el estado de la sesión
    for idx, inv in enumerate(st.session_state.inversiones):
        with st.container(border=True):
            # Fila de cabecera: Nombre, Tipo y Botón de borrar
            col_cab1, col_cab2, col_cab3 = st.columns([2, 2, 1])
            with col_cab1:
                inv["nombre"] = st.text_input("Nombre identificativo:", value=inv["nombre"], key=f"inv_name_{idx}")
            with col_cab2:
                inv["tipo"] = st.selectbox(
                    "Tipo de activo / Filtro:", 
                    ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "ROI Simple"],
                    index=["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "ROI Simple"].index(inv["tipo"]),
                    key=f"inv_tipo_{idx}"
                )
            with col_cab3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("❌ Eliminar", key=f"inv_del_{idx}"):
                    st.session_state.inversiones.pop(idx)
                    st.invalidate_pages() # Limpieza interna de Streamlit
                    st.rerun()

            # Inputs y proyecciones específicas según el tipo de inversión seleccionado
            proyeccion_activo_lista = []
            
            if inv["tipo"] == "Interés Compuesto (ETFs / Fondos)":
                c_f1, c_f2, c_f3 = st.columns(3)
                with c_f1: inv["valor_actual"] = st.number_input("Capital inicial invertido (€)", value=float(inv["valor_actual"]), key=f"f1_{idx}", step=500.0)
                with c_f2: inv["aportacion_mensual"] = st.number_input("Aportación mensual (€/mes)", value=float(inv["aportacion_mensual"]), key=f"f2_{idx}", step=50.0)
                with c_f3: inv["interes_anual"] = st.number_input("Rentabilidad anual esperada (%)", value=float(inv["interes_anual"]), key=f"f3_{idx}", step=0.5)
                
                patrimonio_inversiones_total += inv["valor_actual"]
                
                # Proyección a 15 años (Solución al error del orden alfabético de los índices de la gráfica)
                acumulado = inv["valor_actual"]
                for ano in cronologia_anos:
                    acumulado = (acumulado + (inv["aportacion_mensual"] * 12)) * (1 + (inv["interes_anual"] / 100))
                    proyeccion_activo_lista.append(acumulado)

            elif inv["tipo"] == "Rentabilidad Inmobiliaria (Ladrillo)":
                c_l1, c_l2, c_l3, c_l4 = st.columns(4)
                with c_l1: inv["precio_compra"] = st.number_input("Precio de compra inmueble (€)", value=float(inv["precio_compra"]), key=f"l1_{idx}", step=5000.0)
                with c_l2: inv["gastos_iniciales"] = st.number_input("Impuestos, gastos y reformas (€)", value=float(inv["gastos_iniciales"]), key=f"l2_{idx}", step=1000.0)
                with c_l3: inv["alquiler_mensual"] = st.number_input("Alquiler mensual percibido (€)", value=float(inv["alquiler_mensual"]), key=f"l3_{idx}", step=50.0)
                with c_l4: inv["gastos_anuales"] = st.number_input("Gastos anuales totales (IBI, Seguro...) (€)", value=float(inv["gastos_anuales"]), key=f"l4_{idx}", step=100.0)
                
                # El patrimonio actual en ladrillo es el coste total del activo comprado
                inv["valor_actual"] = inv["precio_compra"] + inv["gastos_iniciales"]
                patrimonio_inversiones_total += inv["valor_actual"]
                
                # Proyección: Valor del inmueble + acumulación de flujos de caja netos por alquiler
                flujo_anual_neto = (inv["alquiler_mensual"] * 12) - inv["gastos_anuales"]
                acumulado = inv["valor_actual"]
                for ano in cronologia_anos:
                    acumulado += flujo_anual_neto
                    proyeccion_activo_lista.append(acumulado)

            elif inv["tipo"] == "ROI Simple":
                c_r1, c_r2 = st.columns(2)
                with c_r1: inv["capital_invertido"] = st.number_input("Dinero invertido original (€)", value=float(inv["capital_invertido"]), key=f"r1_{idx}", step=500.0)
                with c_r2: inv["valor_final"] = st.number_input("Valor de mercado actual (€)", value=float(inv["valor_final"]), key=f"r2_{idx}", step=500.0)
                
                inv["valor_actual"] = inv["valor_final"]
                patrimonio_inversiones_total += inv["valor_actual"]
                
                # Al ser ROI estático, asumimos que mantiene su valor si no hay interés compuesto asignado
                for ano in cronologia_anos:
                    proyeccion_activo_lista.append(inv["valor_actual"])

            # Guardamos los vectores de datos para construir las gráficas posteriormente
            datos_grafica_global[inv["nombre"]] = proyeccion_activo_lista
            dict_graficas_individuales[inv["nombre"]] = proyeccion_activo_lista

    # El patrimonio neto total será el dinero líquido de la cuenta más la suma de todas las inversiones añadidas
    patrimonio_neto_total = capital_inicial + patrimonio_inversiones_total


# ==========================================
# 🏠 5. CONTROLES ESPECÍFICOS DE LA HIPOTECA
# ==========================================
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

    # Cálculos matemáticos de la hipoteca
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
# 📊 6. RENDERIZADO FINAL DE RESULTADOS Y GRÁFICAS
# ==========================================

# --- PESTAÑA 1: VISTA GENERAL (Resúmenes automáticos y dinámicos) ---
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
            st.markdown("#### 2. Tu Patrimonio e Inversión Colectiva")
            st.metric("Patrimonio Neto Calculado", f"{patrimonio_neto_total:,.2f} €", f"Total invertido dinámico: {patrimonio_inversiones_total:,.2f} €")
            st.caption(f"Tienes actualmente un total de **{len(st.session_state.inversiones)}** inversiones configuradas.")

    with c_v2:
        with st.container(border=True):
            st.markdown("#### 3. Estado de tu Hipoteca")
            st.metric("Cuota Real Mensual", f"{cuota_real_total:,.2f} €", f"Recibo + {coste_mensual_seguros:.1f} €/mes en seguros", delta_color="inverse")
            st.metric("Tiempo pendiente de contrato", f"{anos_normal:.1f} años", f"{intereses_totales_normal:,.2f} € pendientes de pago", delta_color="inverse")

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


# --- PESTAÑA 3: RENDIMIENTO DE INVERSIONES (Tus Nuevas Gráficas Cruzadas) ---
with tab_inversion:
    st.markdown("---")
    st.markdown("### 📊 Gráficas de Rendimiento y Proyecciones")
    
    if len(st.session_state.inversiones) > 0:
        col_g_ind, col_g_glob = st.columns(2)
        
        with col_g_ind:
            st.markdown("#### 📈 Evolución Individual de cada Inversión")
            # Convertimos el diccionario individual en Dataframe numérico indexado por Año
            df_ind = pd.DataFrame(dict_graficas_individuales, index=cronologia_anos)
            st.line_chart(df_ind)
            st.caption("Visualiza de forma independiente el crecimiento y la tendencia de cada uno de tus activos.")
            
        with col_g_glob:
            st.markdown("#### 🌍 Tu Cartera de Inversión Global (Acumulado)")
            # Sumamos fila por fila todas las columnas de inversión para obtener la masa patrimonial unificada
            df_glob_prep = pd.DataFrame(datos_grafica_global).set_index("Año")
            df_total_acumulado = pd.DataFrame({"Patrimonio Invertido Total (€)": df_glob_prep.sum(axis=1)}, index=cronologia_anos)
            st.area_chart(df_total_acumulado)
            st.caption("Gráfica acumulada de toda tu riqueza invertida a lo largo de los próximos 15 años.")
    else:
        st.warning("No tienes ninguna inversión configurada. Pulsa el botón '➕ Añadir Nueva Inversión' en la parte superior.")


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
                
                # Construimos un resumen en texto de las inversiones dinámicas para alimentar el prompt de la IA
                resumen_inv_ia = ""
                for item in st.session_state.inversiones:
                    resumen_inv_ia += f"- {item['nombre']} ({item['tipo']}): Valor actual de {item['valor_actual']} €.\n"

                prompt = f"""
                Actúa como un asesor financiero de élite. Analiza este mapa patrimonial completo:
                - Ingresos totales (con extras prorrateados): {ingresos_totales_calculados:.2f} €/mes
                - Ahorro mensual: {ahorro_mensual_total} €/mes
                - Desglose de Inversiones Actuales:\n{resumen_inv_ia}
                - Patrimonio Neto Total: {patrimonio_neto_total:.2f} € (incluyendo {capital_inicial} € de dinero líquido)
                - Hipoteca bancaria: Debe {capital_pendiente} € al {interes_anual_actual}%. Cuota recibo: {cuota_mensual_actual} €/mes. Seguros vinculados: {seguros_anuales_banco} €/año.
                - Meta libertad financiera calculada: {num_libertad} €
                
                Genera un análisis profesional rápido de 3 bloques sobre la diversificación de su cartera dinámica, el impacto de los seguros vinculados y un veredicto estratégico sobre si priorizar la amortización de deuda o la aportación a estas inversiones.
                """
                with st.spinner("La IA está cruzando los datos dinámicos de tu cartera..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"Error con el motor de IA: {e}")
