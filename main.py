import streamlit as st
import google.generativeai as genai
import pandas as pd
import math
import json
import plotly.express as px

# 1. Configuración de pantalla premium y limpia
st.set_page_config(page_title="Cuadro de Mandos Financiero Pro", layout="wide")

# CSS para centrar las pestañas en la pantalla de forma elegante
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 BIENVENIDO A TU TERMINAL PATRIMONIAL TOP", anchor=False)
st.write("Tu suite financiera avanzada y automatizada. Los cambios se guardan al instante en la memoria local de tu navegador.")

# ==========================================
# 💾 MOTOR DE MEMORIA AUTOMÁTICA COMPLETA
# ==========================================
VALORES_POR_DEFECTO = {
    "ingresos_mensuales": 2500,
    "dinero_extra_anual": 3000,
    "ahorro_mensual_total": 600,
    "capital_inicial": 8000,
    "inflacion_anual": 2.5,
    "activar_crisis": False,
    "anos_proyeccion": 15,
    "inversiones": [
        {
            "nombre": "Fondo Indexado Global",
            "tipo": "Interés Compuesto (ETFs / Fondos)",
            "valor_actual": 10000.0,
            "aportacion_mensual": 300.0,
            "interes_anual": 7.5,
            "precio_compra": 120000.0,
            "gastos_iniciales": 10000.0,
            "alquiler_mensual": 650.0,
            "gastos_anuales": 1200.0,
            "capital_invertido": 5000.0,
            "valor_final": 6500.0
        }
    ],
    "tipo_hipoteca": "Fija",
    "capital_original": 150000,
    "capital_pendiente": 115000,
    "interes_anual_actual": 3.2,
    "cuota_mensual_actual": 580,
    "seguros_anuales_banco": 360,
    "amortizacion_extra": 0,
    "inyeccion_capital_unica": 0
}

# Inicialización a prueba de bombas
if "datos_usuario" not in st.session_state:
    st.session_state.datos_usuario = VALORES_POR_DEFECTO.copy()

# Forzar que existan todas las llaves por si la caché del navegador es antigua
for clave, valor in VALORES_POR_DEFECTO.items():
    if clave not in st.session_state.datos_usuario:
        st.session_state.datos_usuario[clave] = valor

# Carga desde URL si existe
if "db" in st.query_params:
    try:
        datos_url = json.loads(st.query_params["db"])
        for clave, valor in datos_url.items():
            st.session_state.datos_usuario[clave] = valor
    except:
        pass

du = st.session_state.datos_usuario

# Migración automática si el usuario tenía el texto antiguo "ROI Simple" guardado
for item in du.get("inversiones", []):
    if item.get("tipo") == "ROI Simple":
        item["tipo"] = "Activos Estáticos / Otros"

def guardar_automatico():
    st.query_params["db"] = json.dumps(st.session_state.datos_usuario)

# ==========================================
# ⚙️ BARRA LATERAL AVANZADA (ENTRADA GLOBAL)
# ==========================================
st.sidebar.title("⚙️ Configuración Global")

with st.sidebar.expander("🔑 Inteligencia Artificial (Gemini)", expanded=False):
    api_key_input = st.text_input("Introduce tu API Key:", type="password")

with st.sidebar.expander("📥 Tus Flujos de Caja", expanded=True):
    du["ingresos_mensuales"] = st.number_input("Ingresos netos al mes (€)", value=int(du["ingresos_mensuales"]), step=100, on_change=guardar_automatico, help="Tus ingresos limpios mensuales recurrentes (nómina líquida, facturación neta, etc.).")
    du["dinero_extra_anual"] = st.number_input("Pagas/Bonus extras al año (€)", value=int(du["dinero_extra_anual"]), step=500, on_change=guardar_automatico, help="Suma de pagas extraordinarias, bonus anuales u otros ingresos variables anualizados.")
    du["ahorro_mensual_total"] = st.number_input("Tu ahorro real al mes (€)", value=int(du["ahorro_mensual_total"]), step=50, on_change=guardar_automatico, help="La cantidad de dinero neta que logras apartar y conservar en tu bolsillo cada mes.")
    du["capital_inicial"] = st.number_input("Efectivo / Fondo Emergencia (€)", value=int(du["capital_inicial"]), step=500, on_change=guardar_automatico, help="Dinero líquido inmediato disponible en cuenta corriente para imprevistos diarios.")

with st.sidebar.expander("🛡️ Simulador de Entorno Económico", expanded=True):
    du["inflacion_anual"] = st.number_input("Inflación anual estimada (%)", value=float(du["inflacion_anual"]), step=0.1, on_change=guardar_automatico, help="El ritmo estimado al que suben los precios de la vida. Reduce tu poder adquisitivo real en las gráficas a futuro.")
    du["anos_proyeccion"] = st.slider("Años a proyectar en el futuro", min_value=5, max_value=40, value=int(du["anos_proyeccion"]), step=1, on_change=guardar_automatico, help="Línea temporal en años para evaluar el impacto del interés compuesto en tu patrimonio.")
    
    du["activar_crisis"] = st.toggle(
        "💥 Activar 'Test de Estrés' (Crisis de mercado)", 
        value=bool(du["activar_crisis"]), 
        on_change=guardar_automatico,
        help="Simula un crack bursátil con una caída del 25% en tus fondos financieros durante el Año 2. Úsalo para medir la resiliencia psicológica de tu plan y ver cómo las inyecciones mensuales constantes aceleran tu recuperación económica posterior."
    )
    if du["activar_crisis"]:
        st.sidebar.caption("⚠️ Se simulará un desplome del 25% en tus activos financieros en el Año 2 de la proyección.")

# Cálculos transversales automáticos
ingreso_extra_prorrateado = du["dinero_extra_anual"] / 12
ingresos_totales = du["ingresos_mensuales"] + ingreso_extra_prorrateado
gastos_mensuales = ingresos_totales - du["ahorro_mensual_total"]
gastos_anuales_proyectados = gastos_mensuales * 12
num_libertad = gastos_anuales_proyectados * 25

# DECLARACIÓN DE PESTAÑAS PRINCIPALES
tab_resumen, tab_presupuesto, tab_inversion, tab_hipoteca, tab_libertad, tab_ia = st.tabs([
    "👑 Cuadro de Mandos", "🥗 Presupuesto Interactivo", "📈 Rentabilidad e Inflación", 
    "🏠 Consultor Hipotecario", "🕊️ Horizonte Independencia", "🤖 Dictamen IA"
])

# ==========================================
# 📥 MOTOR DINÁMICO DE ACTIVOS E INVERSIONES
# ==========================================
patrimonio_inversiones_total = 0.0
cronologia_anos = list(range(1, du["anos_proyeccion"] + 1))
datos_grafica_nominal = {"Año": cronologia_anos}
datos_grafica_real = {"Año": cronologia_anos}
dict_distribucion_activos = {"Efectivo": du["capital_inicial"]}

# Inicializamos estructuras por si no hay inversiones
for item in du.get("inversiones", []):
    dict_distribucion_activos[item["nombre"]] = item["valor_actual"]

with tab_inversion:
    st.subheader("💼 Matriz Patrimonial y Asignación de Activos", anchor=False)
    
    if st.button("➕ Vincular Nuevo Activo/Inversión"):
        du["inversiones"].append({
            "nombre": f"Nuevo Activo {len(du['inversiones']) + 1}",
            "tipo": "Interés Compuesto (ETFs / Fondos)",
            "valor_actual": 0.0, "aportacion_mensual": 0.0, "interes_anual": 7.0,
            "precio_compra": 100000.0, "gastos_iniciales": 10000.0, "alquiler_mensual": 500.0, "gastos_anuales": 1000.0,
            "capital_invertido": 5000.0, "valor_final": 5000.0
        })
        guardar_automatico()
        st.rerun()

    for idx, inv in enumerate(du.get("inversiones", [])):
        with st.container(border=True):
            col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
            with col_c1:
                inv["nombre"] = st.text_input("Identificador del Activo:", value=inv["nombre"], key=f"inv_name_{idx}", on_change=guardar_automatico)
            with col_c2:
                # CAMBIO SOLICITADO: REPLANTEADO "ROI SIMPLE" A "ACTIVOS ESTÁTICOS / OTROS" CON SU TOOLTIP
                inv["tipo"] = st.selectbox(
                    "Naturaleza del activo:", 
                    ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Otros"],
                    index=["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Otros"].index(inv["tipo"] if inv["tipo"] in ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Otros"] else "Activos Estáticos / Otros"),
                    key=f"inv_tipo_{idx}", on_change=guardar_automatico,
                    help="Elige el modelo matemático del activo. 'Activos Estáticos / Otros' sirve para bienes que no rinden intereses mensuales automáticos (oro, coleccionables, cripto estático o préstamos particulares) donde solo mides su valor actual frente a la inflación."
                )
            with col_c3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("❌ Eliminar Activo", key=f"inv_del_{idx}"):
                    du["inversiones"].pop(idx)
                    guardar_automatico()
                    st.rerun()

            proyeccion_nominal = []
            proyeccion_real = []
            
            if inv["tipo"] == "Interés Compuesto (ETFs / Fondos)":
                c1, c2, c3 = st.columns(3)
                with c1: inv["valor_actual"] = st.number_input("Capital actual (€)", value=float(inv["valor_actual"]), key=f"f1_{idx}", step=500.0, on_change=guardar_automatico, help="El saldo total invertido a día de hoy en esta estrategia.")
                with c2: inv["aportacion_mensual"] = st.number_input("Inyección mensual (€)", value=float(inv["aportacion_mensual"]), key=f"f2_{idx}", step=50.0, on_change=guardar_automatico, help="Dinero nuevo que aportas desde tu ahorro mes a mes (Estrategia DCA).")
                with c3: inv["interes_anual"] = st.number_input("Rendimiento anual Neto (%)", value=float(inv["interes_anual"]), key=f"f3_{idx}", step=0.5, on_change=guardar_automatico, help="Rentabilidad media anual esperada del fondo tras descontar comisiones del gestor.")
                
                patrimonio_inversiones_total += inv["valor_actual"]
                dict_distribucion_activos[inv["nombre"]] = inv["valor_actual"]
                
                acumulado_nom = inv["valor_actual"]
                acumulado_real = inv["valor_actual"]
                for i, ano in enumerate(cronologia_anos):
                    if du["activar_crisis"] and ano == 2:
                        acumulado_nom = acumulado_nom * 0.75
                        acumulado_real = acumulado_real * 0.75
                    
                    acumulado_nom = (acumulado_nom + (inv["aportacion_mensual"] * 12)) * (1 + (inv["interes_anual"] / 100))
                    proyeccion_nominal.append(acumulado_nom)
                    
                    rendimiento_real = (inv["interes_anual"] - du["inflacion_anual"]) / 100
                    acumulado_real = (acumulado_real + (inv["aportacion_mensual"] * 12)) * (1 + rendimiento_real)
                    proyeccion_real.append(acumulado_real)

            elif inv["tipo"] == "Rentabilidad Inmobiliaria (Ladrillo)":
                c1, c2, c3, c4 = st.columns(4)
                with c1: inv["precio_compra"] = st.number_input("Precio compra (€)", value=float(inv["precio_compra"]), key=f"l1_{idx}", step=5000.0, on_change=guardar_automatico, help="El precio de adquisición escriturado de la propiedad.")
                with c2: inv["gastos_iniciales"] = st.number_input("Reformas e Impuestos (€)", value=float(inv["gastos_iniciales"]), key=f"l2_{idx}", step=1000.0, on_change=guardar_automatico, help="Gastos de notaría, impuestos (ITP/IVA) y reformas de puesta a punto inicial.")
                with c3: inv["alquiler_mensual"] = st.number_input("Renta mensual líquida (€)", value=float(inv["alquiler_mensual"]), key=f"l3_{idx}", step=50.0, on_change=guardar_automatico, help="El alquiler mensual bruto cobrado al inquilino. Pon 0 si se trata de tu vivienda habitual.")
                with c4: inv["gastos_anuales"] = st.number_input(
                    "Gastos de explotación/año (€)", 
                    value=float(inv["gastos_anuales"]), 
                    key=f"l4_{idx}", 
                    step=100.0, 
                    on_change=guardar_automatico,
                    help="Gastos propios de la vivienda (IBI, comunidad, tasa de basuras, mantenimiento y seguros de hogar/impagos). ⚠️ ATENCIÓN: NO metas aquí la cuota de la hipoteca ni los seguros del banco, eso ya se calcula de forma aislada en la sección de hipotecas para evitar duplicar costes."
                )

                inv["valor_actual"] = inv["precio_compra"] + inv["gastos_iniciales"]
                patrimonio_inversiones_total += inv["valor_actual"]
                dict_distribucion_activos[inv["nombre"]] = inv["valor_actual"]
                
                flujo_neto = (inv["alquiler_mensual"] * 12) - inv["gastos_anuales"]
                acumulado_nom = inv["valor_actual"]
                acumulado_real = inv["valor_actual"]
                for ano in cronologia_anos:
                    acumulado_nom += flujo_neto
                    proyeccion_nominal.append(acumulado_nom)
                    
                    acumulado_real += (flujo_neto / ((1 + (du["inflacion_anual"]/100)) ** ano))
                    proyeccion_real.append(acumulado_real)

            elif inv["tipo"] == "Activos Estáticos / Otros":
                c1, c2 = st.columns(2)
                with c1: inv["capital_invertido"] = st.number_input("Dinero invertido original (€)", value=float(inv["capital_invertido"]), key=f"r1_{idx}", step=500.0, on_change=guardar_automatico, help="El dinero total desembolsado el día que compraste o adquiriste este bien.")
                with c2: inv["valor_final"] = st.number_input("Valor actual (€)", value=float(inv["valor_final"]), key=f"r2_{idx}", step=500.0, on_change=guardar_automatico, help="Lo que vale este bien en el mercado hoy en día (Ej: Tasación del oro, saldo actual de criptomonedas, valor de un reloj, etc.).")
                
                inv["valor_actual"] = inv["valor_final"]
                patrimonio_inversiones_total += inv["valor_actual"]
                dict_distribucion_activos[inv["nombre"]] = inv["valor_actual"]
                
                for ano in cronologia_anos:
                    proyeccion_nominal.append(inv["valor_actual"])
                    proyeccion_real.append(inv["valor_actual"] / ((1 + (du["inflacion_anual"]/100)) ** ano))

            datos_grafica_nominal[inv["nombre"]] = proyeccion_nominal
            datos_grafica_real[inv["nombre"]] = proyeccion_real

    patrimonio_neto_global = du["capital_inicial"] + patrimonio_inversiones_total

# ==========================================
# 🏠 MOTOR DE LA HIPOTECA
# ==========================================
with tab_hipoteca:
    st.subheader("🏠 Análisis Técnico y Estratégico de Deuda Bancaria", anchor=False)
    col1, col2, col3, col4 = st.columns(4)
    with col1: du["tipo_hipoteca"] = st.selectbox("Tipo de interés:", ["Fija", "Variable", "Mixta"], index=["Fija", "Variable", "Mixta"].index(du["tipo_hipoteca"]), on_change=guardar_automatico)
    with col2: du["capital_original"] = st.number_input("Capital prestado original (€)", value=int(du["capital_original"]), step=5000, on_change=guardar_automatico, help="La cantidad de dinero total que te prestó inicialmente el banco.")
    with col3: du["capital_pendiente"] = st.number_input("Capital vivo actual (€)", value=int(du["capital_pendiente"]), step=5000, on_change=guardar_automatico, help="Lo que te queda por pagar hoy al banco para cancelar la deuda por completo.")
    with col4: du["interes_anual_actual"] = st.number_input("Tipo de interés anual (%)", value=float(du["interes_anual_actual"]), step=0.1, on_change=guardar_automatico, help="El tipo de interés (TIN) que te está aplicando el banco actualmente.")
    
    col5, col6, col7, col8 = st.columns(4)
    with col5: du["cuota_mensual_actual"] = st.number_input("Cuota del recibo mensual (€)", value=int(du["cuota_mensual_actual"]), step=50, on_change=guardar_automatico, help="El coste exacto del recibo de la hipoteca que te pasan cada mes por el banco.")
    with col6: du["seguros_anuales_banco"] = st.number_input("Seguros obligatorios / año (€)", value=int(du["seguros_anuales_banco"]), step=50, on_change=guardar_automatico, help="La suma anual de seguros vinculados obligatorios (vida, hogar vinculante) impuestos por el banco.")
    with col7: du["amortizacion_extra"] = st.number_input("Plan amortización extra mensual (€)", value=int(du["amortizacion_extra"]), step=50, on_change=guardar_automatico, help="Dinero adicional recurrente que decides inyectar cada mes para quitarte deuda anticipadamente.")
    with col8: du["inyeccion_capital_unica"] = st.number_input("Inyección amortización única ya (€)", value=int(du["inyeccion_capital_unica"]), step=1000, on_change=guardar_automatico, help="Un pago extraordinario único e inmediato que haces hoy mismo para rebajar el capital pendiente.")

    tasa_mensual = (du["interes_anual_actual"] / 100) / 12
    coste_mensual_seguros = du["seguros_anuales_banco"] / 12
    cuota_financiera_verdadera = du["cuota_mensual_actual"] + coste_mensual_seguros

    if du["cuota_mensual_actual"] > (du["capital_pendiente"] * tasa_mensual):
        interes_mes_actual = du["capital_pendiente"] * tasa_mensual
        # CORRECCIÓN DE KEYERROR LOCK: Usamos la variable local calculada correctamente
        amortizacion_capital_mes = cuota_financiera_verdadera - interes_mes_actual
        meses_contrato = -math.log(1 - (du["capital_pendiente"] * tasa_mensual) / du["cuota_mensual_actual"]) / math.log(1 + tasa_mensual)
        anos_contrato_restantes = meses_contrato / 12
        intereses_totales_banco = (du["cuota_mensual_actual"] * meses_contrato) - du["capital_pendiente"]
    else:
        interes_mes_actual, amortizacion_capital_mes, anos_contrato_restantes, intereses_totales_banco = 0, 0, 0, 0

# ==========================================
# 📊 VISUALIZACIÓN DE MÉTRICAS PREMIUM (PESTAÑA 1)
# ==========================================
with tab_resumen:
    st.subheader("👑 Cuadro de Mandos Patrimonial", anchor=False)
    
    c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
    with c_kpi1:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>PATRIMONIO NETO ACTUAL</p>", unsafe_allow_html=True)
            st.markdown(f"## {patrimonio_neto_global:,.2f} €")
            st.caption(f"Líquido: {du['capital_inicial']:,} € | En Activos: {patrimonio_inversiones_total:,.2f} €")
    with c_kpi2:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>TASA DE AHORRO MENSUAL</p>", unsafe_allow_html=True)
            tasa_ahorro = (du["ahorro_mensual_total"] / ingresos_totales) * 100
            color_tasa = "green" if tasa_ahorro >= 20 else "orange" if tasa_ahorro >= 10 else "red"
            st.markdown(f"<h2 style='color:{color_tasa}; margin:0;'>{tasa_ahorro:.1f}%</h2>", unsafe_allow_html=True)
            st.caption(f"Guardas {du['ahorro_mensual_total']} € de {ingresos_totales:,.0f} € netos.")
    with c_kpi3:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>SALUD DE LA HIPOTECA</p>", unsafe_allow_html=True)
            st.markdown(f"## {anos_contrato_restantes:.1f} años")
            st.caption(f"Deuda pendiente: {du['capital_pendiente']:,} € | Seguros: {coste_mensual_seguros:,.1f} €/mes")

    st.markdown("<br>", unsafe_allow_html=True)
    col_dash1, col_dash2 = st.columns([2, 3])
    with col_dash1:
        with st.container(border=True):
            st.markdown("#### 🍩 Distribución de Activos Reales (Asset Allocation)")
            df_pie = pd.DataFrame({
                "Activo": list(dict_distribucion_activos.keys()),
                "Valor (€)": list(dict_distribucion_activos.values())
            })
            fig_pie = px.pie(df_pie, values="Valor (€)", names="Activo", hole=0.4, color_discrete_sequence=px.colors.qualitative.Safe)
            fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
    with col_dash2:
        with st.container(border=True):
            st.markdown("#### 🎯 Ruta Hacia la Libertad Financiera")
            porcentaje_meta = (patrimonio_neto_global / num_libertad) * 100 if num_libertad > 0 else 0
            st.markdown(f"Has consolidado el **{porcentaje_meta:.1f}%** de tu meta de independencia financiera.")
            st.progress(min(porcentaje_meta / 100, 1.0))
            st.info(f"💡 **Objetivo:** Necesitas acumular **{num_libertad:,.0f} €** (Regla del 4% sobre tus gastos actuales) para vivir de rendimientos.")

# ==========================================
# 🥗 PESTAÑA 2: PRESUPUESTO INTERACTIVO (PLOTLY)
# ==========================================
with tab_presupuesto:
    st.subheader("🥗 Optimización del Presupuesto Estratégico (Regla 50/30/20)", anchor=False)
    nec, cap, aho_rec = ingresos_totales * 0.5, ingresos_totales * 0.3, ingresos_totales * 0.2
    
    col_p1, col_p2 = st.columns([2, 3])
    with col_p1:
        st.markdown(f"""
        - **🏠 Costes Fijos / Necesidades (50%):** Máximo **{nec:,.2f} €/mes**. *(Vivienda, facturas, comida)*
        - **🎉 Estilo de vida / Caprichos (30%):** Máximo **{cap:,.2f} €/mes**. *(Ocio, viajes, restaurantes)*
        - **🐷 Inversión / Ahorro Mínimo (20%):** Deberías guardar **{aho_rec:,.2f} €/mes**.
        ---
        Tu tasa de ahorro autodeclarada actual es de **{du['ahorro_mensual_total']:,.2f} €/mes**.
        """)
        if du['ahorro_mensual_total'] >= aho_rec:
            st.success("🎉 ¡Excelente! Estás ahorrando por encima de los estándares recomendados.")
        else:
            st.warning("⚠️ Tu ahorro actual está por debajo de la regla del 20%. Revisa gastos.")
            
    with col_p2:
        df_p = pd.DataFrame({
            "Categoría": ["Necesidades (50%)", "Caprichos (30%)", "Ahorro Rec. (20%)", "Tu Ahorro Real"],
            "Importe Mensual (€)": [nec, cap, aho_rec, du["ahorro_mensual_total"]]
        })
        fig_bar_p = px.bar(df_p, x="Categoría", y="Importe Mensual (€)", color="Categoría", color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_bar_p.update_layout(height=300, showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_bar_p, use_container_width=True)

# ==========================================
# 📈 PESTAÑA 3: RENDIMIENTO CON AJUSTE DE INFLACIÓN Y CRISIS
# ==========================================
with tab_inversion:
    st.markdown("---")
    st.subheader("📊 Modelado de Escenarios de Riqueza Futura", anchor=False)
    
    if len(du.get("inversiones", [])) > 0:
        df_prep_nom = pd.DataFrame(datos_grafica_nominal).set_index("Año")
        df_total_nom = pd.DataFrame({"Valor Nominal (Dinero Futuro)": df_prep_nom.sum(axis=1)})
        
        df_prep_real = pd.DataFrame(datos_grafica_real).set_index("Año")
        df_total_real = pd.DataFrame({"Valor Real (Poder Adquisitivo Corregido)": df_prep_real.sum(axis=1)})
        
        df_proyeccion_final = df_total_nom.join(df_total_real).reset_index()
        df_melted = df_proyeccion_final.melt(id_vars=["Año"], var_name="Métrica", value_name="Capital Acumulado (€)")
        
        fig_lineas = px.line(df_melted, x="Año", y="Capital Acumulado (€)", color="Métrica", 
                             title=f"Evolución Patrimonial Proyectada a {du['anos_proyeccion']} años",
                             color_discrete_sequence=["#1f77b4", "#ff7f0e"])
        fig_lineas.update_layout(height=400, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
        st.plotly_chart(fig_lineas, use_container_width=True)
        
        st.caption(f"ℹ️ La línea azul es el dinero nominal. La línea naranja descuenta un {du['inflacion_anual']}% anual de inflación.")
    else:
        st.warning("Añade activos para ver el gráfico de proyecciones.")

# ==========================================
# 🏠 PESTAÑA 4: CONSULTORÍA ESTRATÉGICA AVANZADA HIPOTECA VS INVERSIÓN
# ==========================================
with tab_hipoteca:
    st.markdown("---")
    if anos_contrato_restantes > 0:
        st.subheader("🧠 Motor Analítico: ¿Priorizar Deuda o Invertir?", anchor=False)
        
        rentabilidad_media_activos = 0.0
        if len(du.get("inversiones", [])) > 0:
            tasas = [i["interes_anual"] for i in du["inversiones"] if "interes_anual" in i]
            rentabilidad_media_activos = sum(tasas) / len(tasas) if tasas else 6.0
        else:
            rentabilidad_media_activos = 6.0

        diferencial_arbitraje = rentabilidad_media_activos - du["interes_anual_actual"]

        col_st1, col_st2 = st.columns([3, 2])
        with col_st1:
            st.markdown(f"#### ⚖️ Veredicto del Consultor Financiero Automatizado")
            st.write(f"• Coste hipoteca: **{du['interes_anual_actual']}%**. Rendimiento medio inversiones: **{rentabilidad_media_activos:.1f}%**.")
            
            if diferencial_arbitraje > 1.0:
                st.success(f"📈 **VEREDICTO: PRIORIZAR INVERSIÓN**. Ganas más dinero invirtiendo que cancelando esta hipoteca.")
            elif diferencial_arbitraje < -0.5:
                st.error(f"🏠 **VEREDICTO: PRIORIZAR AMORTIZACIÓN**. Tu hipoteca te cuesta más de lo que rinde tu dinero. Cancela deuda.")
            else:
                st.warning(f"⚖️ **VEREDICTO: ESCENARIO MIXTO**. Coste y rendimiento parejos. Decide según tu perfil de riesgo.")
        with col_st2:
            df_arbitraje = pd.DataFrame({
                "Concepto": ["Coste Hipoteca", "Rendimiento Inversión"],
                "Porcentaje (%)": [du["interes_anual_actual"], rentabilidad_media_activos]
            })
            fig_arb = px.bar(df_arbitraje, x="Concepto", y="Porcentaje (%)", color="Concepto", color_discrete_sequence=["#d62728", "#2ca02c"])
            fig_arb.update_layout(height=220, showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_arb, use_container_width=True)

        capital_pendiente_neto = du["capital_pendiente"] - du["inyeccion_capital_unica"]
        if du["amortizacion_extra"] > 0 or du["inyeccion_capital_unica"] > 0:
            cuota_con_extra = du["cuota_mensual_actual"] + du["amortizacion_extra"]
            if cuota_con_extra > (capital_pendiente_neto * tasa_mensual):
                meses_extra = -math.log(1 - (capital_pendiente_neto * tasa_mensual) / cuota_con_extra) / math.log(1 + tasa_mensual)
                anos_extra = meses_extra / 12
                intereses_totales_extra = (du["inyeccion_capital_unica"] + (cuota_con_extra * meses_extra)) - du["capital_pendiente"]
                
                st.markdown("#### 🔥 Resultados de tu Plan de Aceleración Activo")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric("Años ahorrados al banco", f"{(anos_contrato_restantes - anos_extra):.1f} años menos")
                with col_m2:
                    st.metric("Intereses salvados", f"{(intereses_totales_banco - intereses_totales_extra):,.2f} €")

# ==========================================
# 🕊️ PESTAÑA 5: LIBERTAD FINANCIERA DETALLADA
# ==========================================
with tab_libertad:
    st.subheader("🕊️ Tu Meta de Libertad Financiera (Regla del 4%)", anchor=False)
    st.error(f"## 🎯 TU NÚMERO OBJETIVO: {num_libertad:,.2f} €")
    st.write(f"Gastos anuales proyectados: **{gastos_anuales_proyectados:,.2f} €**. Con ese objetivo invertido cubres tu nivel de vida.")

# ==========================================
# 🤖 PESTAÑA 6: CONSULTORÍA DE IA AVANZADA CRUZADA
# ==========================================
with tab_ia:
    st.subheader("🤖 Dictamen e Informe Estratégico de IA", anchor=False)
    if not api_key_input:
        st.warning("🔒 Introduce tu Gemini API Key en la barra lateral para desbloquear la IA.")
    else:
        if st.button("🚀 Generar Auditoría Patrimonial Completa"):
            try:
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                resumen_activos = ""
                for i in du.get("inversiones", []):
                    resumen_activos += f"- {i['nombre']} ({i['tipo']}): Valor: {i['valor_actual']} €. Rentabilidad: {i.get('interes_anual', 0)}%\n"

                prompt = f"""
                Eres un analista financiero élite. Analiza este informe patrimonial brevemente:
                - Ingresos: {ingresos_totales:.2f} €/mes
                - Ahorro: {du['ahorro_mensual_total']} €/mes ({tasa_ahorro:.1f}%)
                - Efectivo: {du['capital_inicial']} €
                - Inversiones:\n{resumen_activos}
                - Patrimonio Total: {patrimonio_neto_global:.2f} €
                - Hipoteca: Debe {du['capital_pendiente']} € al {du['interes_anual_actual']}%.
                - Inflación simulada: {du['inflacion_anual']}%. Crisis activada: {du['activar_crisis']}.
                
                Redacta un dictamen conciso de 3 secciones en Markdown elegante:
                1. Evaluación del Asset Allocation frente a la inflación.
                2. Crítica del coste de hipoteca vs inversión.
                3. Una recomendación táctica audaz para llegar a la meta de ({num_libertad:.0f} €).
                """
                with st.spinner("La IA está calculando los escenarios económicos..."):
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"Error en el motor analítico de IA: {e}")

# Indicador visual de estado de la persistencia automática
st.sidebar.markdown("---")
st.sidebar.caption("✅ Autofijado activo. Tus datos se salvan solos con cada click.")
