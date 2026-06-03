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
            "gastos_mensuales_inv": 50.0,
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
    "inyeccion_capital_unica": 0,
    "antiguedad_trabajo": 3,
    "nombre_empresa": "Inditex S.A.",
    "es_autonomo_empresa": False,
    "facturacion_anual": 45000,
    "deudas": [
        {"nombre": "Financiación Coche", "tipo": "Actual", "cuota_mensual": 210.0, "pendiente": 6400.0, "horizonte": "Inmediato"},
        {"nombre": "Reforma Cocina", "tipo": "Próxima", "cuota_mensual": 150.0, "pendiente": 4500.0, "horizonte": "En 6 meses"}
    ]
}

# Crear estados iniciales si no existen
if "datos_usuario" not in st.session_state:
    st.session_state.datos_usuario = VALORES_POR_DEFECTO.copy()

if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = []

if "auditoria_estatica" not in st.session_state:
    st.session_state.auditoria_estatica = ""

# Carga desde URL si se comparte un enlace externo
if "db" in st.query_params:
    try:
        datos_url = json.loads(st.query_params["db"])
        for clave, valor in datos_url.items():
            st.session_state.datos_usuario[clave] = valor
    except:
        pass

# Blindaje anti-keyerror y actualización de estructuras viejas
for clave, valor in VALORES_POR_DEFECTO.items():
    if clave not in st.session_state.datos_usuario:
        st.session_state.datos_usuario[clave] = valor

du = st.session_state.datos_usuario

# Asegurar que los activos inmobiliarios tengan la nueva variable de gastos mensuales
for item in du.get("inversiones", []):
    if "gastos_mensuales_inv" not in item:
        item["gastos_mensuales_inv"] = 0.0

def guardar_automatico():
    st.query_params["db"] = json.dumps(st.session_state.datos_usuario)

# ==========================================
# ⚙️ BARRA LATERAL AVANZADA (ENTRADA GLOBAL)
# ==========================================
st.sidebar.title("⚙️ Configuración Global")

if "api_key_guardada" not in st.session_state:
    st.session_state.api_key_guardada = ""

with st.sidebar.expander("🔑 Inteligencia Artificial (Gemini)", expanded=not bool(st.session_state.api_key_guardada)):
    if not st.session_state.api_key_guardada:
        clave_introducida = st.text_input("Introduce tu API Key y pulsa Intro:", type="password")
        if clave_introducida:
            st.session_state.api_key_guardada = clave_introducida
            st.rerun()
    else:
        st.success("✅ API Key vinculada y activa")
        if st.button("🔄 Cambiar / Borrar clave"):
            st.session_state.api_key_guardada = ""
            st.session_state.historial_chat = []
            st.session_state.auditoria_estatica = ""
            st.rerun()

with st.sidebar.expander("📥 Tus Flujos de Caja", expanded=True):
    du["ingresos_mensuales"] = st.number_input("Ingresos netos al mes (€)", value=int(du["ingresos_mensuales"]), step=100, on_change=guardar_automatico)
    du["dinero_extra_anual"] = st.number_input("Pagas/Bonus extras al año (€)", value=int(du["dinero_extra_anual"]), step=500, on_change=guardar_automatico)
    du["ahorro_mensual_total"] = st.number_input("Tu ahorro real al mes (€)", value=int(du["ahorro_mensual_total"]), step=50, on_change=guardar_automatico)
    du["capital_inicial"] = st.number_input("Efectivo / Liquidez Total (€)", value=int(du["capital_inicial"]), step=500, on_change=guardar_automatico)

with st.sidebar.expander("💳 Perfil Crediticio y Laboral", expanded=True):
    du["nombre_empresa"] = st.text_input("Nombre de la empresa / pagador:", value=str(du["nombre_empresa"]), on_change=guardar_automatico)
    du["antiguedad_trabajo"] = st.number_input("Tu antigüedad en este empleo (Años)", min_value=0, max_value=50, value=int(du["antiguedad_trabajo"]), on_change=guardar_automatico)
    
    du["es_autonomo_empresa"] = st.toggle("💼 ¿Eres Autónomo o Empresa?", value=bool(du["es_autonomo_empresa"]), on_change=guardar_automatico)
    if du["es_autonomo_empresa"]:
        du["facturacion_anual"] = st.number_input("Facturación bruta anual (€)", value=int(du["facturacion_anual"]), step=5000, on_change=guardar_automatico)

with st.sidebar.expander("🛡️ Simulador de Entorno Económico", expanded=False):
    du["inflacion_anual"] = st.number_input("Inflación anual estimada (%)", value=float(du["inflacion_anual"]), step=0.1, on_change=guardar_automatico)
    du["anos_proyeccion"] = st.slider("Años a proyectar en el futuro", min_value=5, max_value=40, value=int(du["anos_proyeccion"]), step=1, on_change=guardar_automatico)
    du["activar_crisis"] = st.toggle("💥 Activar 'Test de Estrés'", value=bool(du["activar_crisis"]), on_change=guardar_automatico)


# ==========================================
# 🧮 MOTOR MATEMÁTICO GLOBAL (FUERA DE LAS PESTAÑAS)
# ==========================================
ingreso_extra_prorrateado = du["dinero_extra_anual"] / 12
ingresos_totales = du["ingresos_mensuales"] + ingreso_extra_prorrateado
gastos_mensuales_vivos = ingresos_totales - du["ahorro_mensual_total"]
num_libertad = (gastos_mensuales_vivos * 12) * 25

total_cuotas_deudas_extra = sum(float(d["cuota_mensual"]) for d in du["deudas"] if d["tipo"] == "Actual")
total_pendiente_deudas_extra = sum(float(d["pendiente"]) for d in du["deudas"] if d["tipo"] == "Actual")

patrimonio_inversiones_total = 0.0
cronologia_anos = list(range(1, du["anos_proyeccion"] + 1))
datos_grafica_nominal = {"Año": cronologia_anos}
datos_grafica_real = {"Año": cronologia_anos}
dict_distribucion_activos = {"Efectivo": du["capital_inicial"]}

# Bucle global para calcular proyecciones financieras complejas sin importar la pestaña
for idx, inv in enumerate(du.get("inversiones", [])):
    proyeccion_nominal, proyeccion_real = [], []
    
    if inv["tipo"] == "Interés Compuesto (ETFs / Fondos)":
        patrimonio_inversiones_total += inv["valor_actual"]
        acumulado_nom, acumulado_real = inv["valor_actual"], inv["valor_actual"]
        for ano in cronologia_anos:
            if du["activar_crisis"] and ano == 2:
                acumulado_nom *= 0.75; acumulado_real *= 0.75
            acumulado_nom = (acumulado_nom + (inv["aportacion_mensual"] * 12)) * (1 + (inv["interes_anual"] / 100))
            proyeccion_nominal.append(acumulado_nom)
            rendimiento_real = (inv["interes_anual"] - du["inflacion_anual"]) / 100
            acumulado_real = (acumulado_real + (inv["aportacion_mensual"] * 12)) * (1 + rendimiento_real)
            proyeccion_real.append(acumulado_real)

    elif inv["tipo"] == "Rentabilidad Inmobiliaria (Ladrillo)":
        inv["valor_actual"] = inv["precio_compra"] + inv["gastos_iniciales"]
        patrimonio_inversiones_total += inv["valor_actual"]
        flujo_neto = (inv["alquiler_mensual"] * 12) - (inv["gastos_mensuales_inv"] * 12) - inv["gastos_anuales"]
        acumulado_nom, acumulado_real = inv["valor_actual"], inv["valor_actual"]
        for ano in cronologia_anos:
            acumulado_nom += flujo_neto
            proyeccion_nominal.append(acumulado_nom)
            acumulado_real += (flujo_neto / ((1 + (du["inflacion_anual"]/100)) ** ano))
            proyeccion_real.append(acumulado_real)

    elif inv["tipo"] in ["Activos Estáticos / Otros", "Activos Estáticos / Others"]:
        inv["valor_actual"] = inv["valor_final"]
        patrimonio_inversiones_total += inv["valor_actual"]
        for ano in cronologia_anos:
            proyeccion_nominal.append(inv["valor_actual"])
            proyeccion_real.append(inv["valor_actual"] / ((1 + (du["inflacion_anual"]/100)) ** ano))

    datos_grafica_nominal[inv["nombre"]] = proyeccion_nominal
    datos_grafica_real[inv["nombre"]] = proyeccion_real

# Inicializar distribución de activos con los valores calculados/actualizados
for item in du.get("inversiones", []):
    dict_distribucion_activos[item["nombre"]] = item["valor_actual"]

patrimonio_neto_global = du["capital_inicial"] + patrimonio_inversiones_total

# Cálculos de la hipoteca globales
tasa_mensual = (du["interes_anual_actual"] / 100) / 12
coste_mensual_seguros = du["seguros_anuales_banco"] / 12
cuota_financiera_verdadera = du["cuota_mensual_actual"] + coste_mensual_seguros

if du["cuota_mensual_actual"] > (du["capital_pendiente"] * tasa_mensual):
    meses_contrato = -math.log(1 - (du["capital_pendiente"] * tasa_mensual) / du["cuota_mensual_actual"]) / math.log(1 + tasa_mensual)
    anos_contrato_restantes = meses_contrato / 12
    intereses_totales_banco = (du["cuota_mensual_actual"] * meses_contrato) - du["capital_pendiente"]
else:
    anos_contrato_restantes, intereses_totales_banco = 0, 0

# Configuración del Fondo de Emergencia Global
gastos_mensuales_totales = du["cuota_mensual_actual"] + total_cuotas_deudas_extra + gastos_mensuales_vivos
meses_cobertura = du["capital_inicial"] / gastos_mensuales_totales if gastos_mensuales_totales > 0 else 0

if meses_cobertura < 3:
    estado_seguridad = "Bajo Mínimos"
else:
    estado_seguridad = "Saludable / Estándar" if meses_cobertura <= 6 else "Excelente"


# ==========================================
# 📊 CREACIÓN Y DEFINICIÓN DE PESTAÑAS
# ==========================================
tab_resumen, tab_presupuesto, tab_inversion, tab_hipoteca, tab_libertad, tab_ia = st.tabs([
    "👑 Cuadro de Mandos", "🥗 Presupuesto y Deudas", "📈 Rentabilidad e Inversión", 
    "🏠 Consultor Hipotecario", "🕊️ Horizonte Independencia", "🤖 Dictamen e IA Chat"
])

# ----- PESTAÑA 1: CUADRO DE MANDOS -----
with tab_resumen:
    st.subheader("👑 Cuadro de Mandos Patrimonial", anchor=False)
    c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
    with c_kpi1:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>PATRIMONIO NETO ACTUAL</p>", unsafe_allow_html=True)
            st.markdown(f"## {patrimonio_neto_global - du['capital_pendiente'] - total_pendiente_deudas_extra:,.2f} €")
            st.caption(f"Líquido: {du['capital_inicial']:,} € | Activos Vinculados: {patrimonio_inversiones_total:,.2f} €")
    with c_kpi2:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>TASA DE AHORRO MENSUAL</p>", unsafe_allow_html=True)
            tasa_ahorro = (du["ahorro_mensual_total"] / ingresos_totales) * 100
            st.markdown(f"## {tasa_ahorro:.1f}%")
            st.caption(f"Ahorras {du['ahorro_mensual_total']} € de {ingresos_totales:,.0f} € netos.")
    with c_kpi3:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>PASIVOS RECONOCIDOS</p>", unsafe_allow_html=True)
            deuda_consolidada = du["capital_pendiente"] + total_pendiente_deudas_extra
            st.markdown(f"## {deuda_consolidada:,.0f} €")
            st.caption(f"Hipotecaria: {du['capital_pendiente']:,} € | Consumo/Otras: {total_pendiente_deudas_extra:,.0f} €")

    st.markdown("<br>", unsafe_allow_html=True)
    col_dash1, col_dash2 = st.columns([2, 3])
    with col_dash1:
        with st.container(border=True):
            df_pie = pd.DataFrame({"Activo": list(dict_distribucion_activos.keys()), "Valor (€)": list(dict_distribucion_activos.values())})
            fig_pie = px.pie(df_pie, values="Valor (€)", names="Activo", hole=0.4, title="Asset Allocation Actual")
            fig_pie.update_layout(height=250, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)
    with col_dash2:
        with st.container(border=True):
            st.markdown("#### 🎯 Meta Independencia Financiera")
            porcentaje_meta = (patrimonio_neto_global / num_libertad) * 100 if num_libertad > 0 else 0
            st.progress(min(porcentaje_meta / 100, 1.0))
            st.info(f"Objetivo: **{num_libertad:,.0f} €** (Regla del 4%). Llevas completado el **{porcentaje_meta:.1f}%**.")

# ----- PESTAÑA 2: PRESUPUESTO Y DEUDAS -----
with tab_presupuesto:
    st.subheader("🥗 Optimización y Control de Riesgos Patrimoniales", anchor=False)
    
    st.markdown("### 🛡️ Escudo de Contingencias (Fondo de Emergencia)")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.metric("Tus Gastos Mensuales Reales", f"{gastos_mensuales_totales:,.2f} €", help="Incluye costes de vida, hipoteca y cuotas de tus deudas activas.")
    with col_f2:
        st.metric("Meses de Cobertura de tu Liquidez", f"{meses_cobertura:.1f} meses")
    with col_f3:
        if meses_cobertura < 3:
            st.error("🚨 Alerta: Fondo Insuficiente. Estás expuesto ante imprevistos graves.")
        elif 3 <= meses_cobertura <= 6:
            st.warning("⚠️ Rango Estándar: Tienes colchón, pero ajustado para crisis medianas.")
        else:
            st.success("✅ Rango Óptimo: Nivel máximo de seguridad patrimonial.")

    st.markdown("---")
    st.markdown("### 💳 Matriz de Pasivos (Deudas Actuales y Próximas)")
    
    if st.button("➕ Añadir Nueva Deuda / Próximo Gasto"):
        du["deudas"].append({"nombre": "Nueva Deuda", "tipo": "Actual", "cuota_mensual": 100.0, "pendiente": 2000.0, "horizonte": "Inmediato"})
        guardar_automatico()
        st.rerun()
        
    for d_idx, deuda in enumerate(du.get("deudas", [])):
        with st.container(border=True):
            col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns([2, 2, 2, 2, 1])
            with col_d1:
                deuda["nombre"] = st.text_input("Concepto / Deuda:", value=deuda["nombre"], key=f"d_name_{d_idx}", on_change=guardar_automatico)
            with col_d2:
                deuda["tipo"] = st.selectbox("Estado temporal:", ["Actual", "Próxima"], index=["Actual", "Próxima"].index(deuda["tipo"]), key=f"d_tipo_{d_idx}", on_change=guardar_automatico)
            with col_d3:
                deuda["cuota_mensual"] = st.number_input("Cuota estimada al mes (€):", value=float(deuda["cuota_mensual"]), key=f"d_cuota_{d_idx}", on_change=guardar_automatico)
            with col_d4:
                if deuda["tipo"] == "Actual":
                    deuda["pendiente"] = st.number_input("Capital Pendiente (€):", value=float(deuda["pendiente"]), key=f"d_pend_{d_idx}", on_change=guardar_automatico)
                    deuda["horizonte"] = "Inmediato"
                else:
                    deuda["horizonte"] = st.selectbox("Llegada estimada:", ["En 3 meses", "En 6 meses", "En 12 meses", "Más de 1 año"], index=["En 3 meses", "En 6 meses", "En 12 meses", "Más de 1 año"].index(deuda["horizonte"] if deuda["horizonte"] in ["En 3 meses", "En 6 meses", "En 12 meses", "Más de 1 año"] else "En 3 meses"), key=f"d_horiz_{d_idx}", on_change=guardar_automatico)
                    deuda["pendiente"] = st.number_input("Gasto total estimado (€):", value=float(deuda["pendiente"]), key=f"d_pend_{d_idx}", on_change=guardar_automatico)
            with col_d5:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("❌", key=f"d_del_{d_idx}"):
                    du["deudas"].pop(d_idx)
                    guardar_automatico()
                    st.rerun()

# ----- PESTAÑA 3: RENTABILIDAD E INVERSIÓN -----
with tab_inversion:
    st.subheader("💼 Matriz Patrimonial y Asignación de Activos", anchor=False)
    if st.button("➕ Vincular Nuevo Activo/Inversión"):
        du["inversiones"].append({
            "nombre": f"Nuevo Activo {len(du['inversiones']) + 1}",
            "tipo": "Interés Compuesto (ETFs / Fondos)",
            "valor_actual": 0.0, "aportacion_mensual": 0.0, "interes_anual": 7.0,
            "precio_compra": 100000.0, "gastos_iniciales": 10000.0, "alquiler_mensual": 500.0, 
            "gastos_mensuales_inv": 40.0, "gastos_anuales": 600.0, "capital_invertido": 5000.0, "valor_final": 5000.0
        })
        guardar_automatico()
        st.rerun()

    for idx, inv in enumerate(du.get("inversiones", [])):
        with st.container(border=True):
            col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
            with col_c1: inv["nombre"] = st.text_input("Identificador:", value=inv["nombre"], key=f"inv_name_{idx}", on_change=guardar_automatico)
            with col_c2: inv["tipo"] = st.selectbox("Naturaleza:", ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Otros"], index=["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Otros"].index(inv["tipo"] if inv["tipo"] in ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Otros"] else "Activos Estáticos / Otros"), key=f"inv_tipo_{idx}", on_change=guardar_automatico)
            with col_c3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("❌ Eliminar", key=f"inv_del_{idx}"):
                    du["inversiones"].pop(idx)
                    guardar_automatico()
                    st.rerun()

            if inv["tipo"] == "Interés Compuesto (ETFs / Fondos)":
                c1, c2, c3 = st.columns(3)
                with c1: inv["valor_actual"] = st.number_input("Capital actual (€)", value=float(inv["valor_actual"]), key=f"f1_{idx}", on_change=guardar_automatico)
                with c2: inv["aportacion_mensual"] = st.number_input("Inyección al mes (€)", value=float(inv["aportacion_mensual"]), key=f"f2_{idx}", on_change=guardar_automatico)
                with c3: inv["interes_anual"] = st.number_input("Rendimiento anual Neto (%)", value=float(inv["interes_anual"]), key=f"f3_{idx}", on_change=guardar_automatico)

            elif inv["tipo"] == "Rentabilidad Inmobiliaria (Ladrillo)":
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1: inv["precio_compra"] = st.number_input("Precio compra (€)", value=float(inv["precio_compra"]), key=f"l1_{idx}", on_change=guardar_automatico)
                with c2: inv["gastos_iniciales"] = st.number_input("Gastos/Impuestos iniciales (€)", value=float(inv["gastos_iniciales"]), key=f"l2_{idx}", on_change=guardar_automatico)
                with c3: inv["alquiler_mensual"] = st.number_input("Renta mensual (€)", value=float(inv["alquiler_mensual"]), key=f"l3_{idx}", on_change=guardar_automatico)
                with c4: inv["gastos_mensuales_inv"] = st.number_input("Gastos fijos al MES (€)", value=float(inv["gastos_mensuales_inv"]), key=f"l5_{idx}", on_change=guardar_automatico)
                with c5: inv["gastos_anuales"] = st.number_input("Gastos fijos al AÑO (€)", value=float(inv["gastos_anuales"]), key=f"l4_{idx}", on_change=guardar_automatico)

            elif inv["tipo"] in ["Activos Estáticos / Otros", "Activos Estáticos / Others"]:
                c1, c2 = st.columns(2)
                with c1: inv["capital_invertido"] = st.number_input("Original invertido (€)", value=float(inv["capital_invertido"]), key=f"r1_{idx}", on_change=guardar_automatico)
                with c2: inv["valor_final"] = st.number_input("Valor de mercado (€)", value=float(inv["valor_final"]), key=f"r2_{idx}", on_change=guardar_automatico)

    st.markdown("---")
    if len(du.get("inversiones", [])) > 0:
        df_prep_nom = pd.DataFrame(datos_grafica_nominal).set_index("Año")
        df_total_nom = pd.DataFrame({"Valor Nominal": df_prep_nom.sum(axis=1)})
        df_prep_real = pd.DataFrame(datos_grafica_real).set_index("Año")
        df_total_real = pd.DataFrame({"Valor Real Corregido": df_prep_real.sum(axis=1)})
        df_melted = df_total_nom.join(df_total_real).reset_index().melt(id_vars=["Año"], var_name="Métrica", value_name="Capital (€)")
        fig_lineas = px.line(df_melted, x="Año", y="Capital (€)", color="Métrica", title="Evolución del Patrimonio Bajo Inflación")
        st.plotly_chart(fig_lineas, use_container_width=True)

# ----- PESTAÑA 4: CONSULTOR HIPOTECARIO -----
with tab_hipoteca:
    st.subheader("🏠 Análisis Técnico de Deuda Hipotecaria", anchor=False)
    col1, col2, col3, col4 = st.columns(4)
    with col1: du["tipo_hipoteca"] = st.selectbox("Tipo de interés:", ["Fija", "Variable", "Mixta"], index=["Fija", "Variable", "Mixta"].index(du["tipo_hipoteca"]), on_change=guardar_automatico)
    with col2: du["capital_original"] = st.number_input("Capital original (€)", value=int(du["capital_original"]), on_change=guardar_automatico)
    with col3: du["capital_pendiente"] = st.number_input("Capital pendiente actual (€)", value=int(du["capital_pendiente"]), on_change=guardar_automatico)
    with col4: du["interes_anual_actual"] = st.number_input("Interés anual (%)", value=float(du["interes_anual_actual"]), on_change=guardar_automatico)
    
    col5, col6, col7, col8 = st.columns(4)
    with col5: du["cuota_mensual_actual"] = st.number_input("Recibo mensual (€)", value=int(du["cuota_mensual_actual"]), on_change=guardar_automatico)
    with col6: du["seguros_anuales_banco"] = st.number_input("Seguros banco / año (€)", value=int(du["seguros_anuales_banco"]), on_change=guardar_automatico)
    with col7: du["amortizacion_extra"] = st.number_input("Amortización extra mes (€)", value=int(du["amortizacion_extra"]), on_change=guardar_automatico)
    with col8: du["inyeccion_capital_unica"] = st.number_input("Inyección puntual inmediata (€)", value=int(du["inyeccion_capital_unica"]), on_change=guardar_automatico)

    if anos_contrato_restantes > 0:
        st.info(f"📆 Tiempo restante estimado: **{anos_contrato_restantes:.1f} años** | Intereses pendientes al banco: **{intereses_totales_banco:,.2f} €**")

# ----- PESTAÑA 5: HORIZONTE INDEPENDENCIA -----
with tab_libertad:
    st.subheader("🕊️ Tu Meta de Libertad Financiera (Regla del 4%)", anchor=False)
    st.error(f"## 🎯 TU NÚMERO OBJETIVO: {num_libertad:,.2f} €")
    st.write("Este número representa el capital total necesario invertido para poder retirar un 4% anual perpetuo que cubra por completo tu nivel de vida actual sin trabajar.")

# ==========================================
# 📥 EXTRACCIÓN DE DOSSIER FIJO EN SIDEBAR
# ==========================================
txt_activos = ""
for i in du.get("inversiones", []):
    txt_activos += f"- {i['nombre']} ({i['tipo']}): {i['valor_actual']} EUR\n"

txt_deudas = ""
for d in du.get("deudas", []):
    txt_deudas += f"- {d['nombre']} ({d['tipo']}): Total: {d['pendiente']} EUR | Cuota: {d['cuota_mensual']} EUR/mes (Horizonte: {d['horizonte']})\n"

tasa_ahorro_val = (du["ahorro_mensual_total"] / ingresos_totales) * 100 if ingresos_totales > 0 else 0

dossier_bancario_md = f"""# REPORTING ESTRATÉGICO PATRIMONIAL
Generado para Entidades de Crédito y Gestión de Activos

## 1. RESUMEN EJECUTIVO DEL PERFIL
- Entidad Laboral Activa: {du['nombre_empresa']} (Antigüedad individual: {du['antiguedad_trabajo']} años)
- Ingresos Líquidos Mensuales: {du['ingresos_mensuales']} EUR
- Capacidad de Ahorro Demostrada: {du['ahorro_mensual_total']} EUR/mes (Tasa de ahorro: {tasa_ahorro_val:.1f}%)
- Colchón de Contingencia: {du['capital_inicial']} EUR ({meses_cobertura:.1f} meses de cobertura total. Estatus: {estado_seguridad})

## 2. DESGLOSE DE ACTIVOS CONSOLIDADOS
{txt_activos if txt_activos else "- Sin activos adicionales declarados."}

## 3. PASIVOS Y CALIFICACIÓN DE DEUDA
- Hipoteca Pendiente: {du['capital_pendiente']} EUR (Cuota: {du['cuota_mensual_actual']} EUR/mes al {du['interes_anual_actual']}%)
- Deudas Consolidadas Adicionales y Compromisos Próximos:
{txt_deudas if txt_deudas else "- Sin otras deudas vigentes."}

## 4. ANÁLISIS DE PROS Y CONTRAS DEL PERFIL
### PROS:
- Tasa de ahorro recurrente alta ({tasa_ahorro_val:.1f}%), garantizando liquidez para amortizaciones o nuevos proyectos.
- Colchón de emergencia robusto que mitiga riesgos de impago a corto plazo.
- Perfil profesional asentado en {du['nombre_empresa']}.

### CONTRAS / PUNTOS DE VIGILANCIA:
- Impacto de la inflación simulada al {du['inflacion_anual']}% sobre el capital no invertido.
- Compromisos futuros indexados que podrían alterar los ratios de endeudamiento mensuales.

## 5. ESTRATEGIA DE CRECIMIENTO RECOMENDADA
Optimizar el arbitraje de deuda maximizando las aportaciones recurrentes a activos indexados que superen con holgura el coste financiero de los pasivos vigentes.
"""

with st.sidebar.expander("📥 Extraer Dossier Financiero Pro", expanded=True):
    st.write("Descarga un completo informe corporativo ideal para presentar en bancos o analizar tu salud financiera fuera de la app.")
    formato = st.selectbox("Elige el formato de salida:", ["Dossier Técnico (.md / .txt)", "Proyecto Ejecutivo (.pdf / Imprimible)"])
    
    if formato == "Dossier Técnico (.md / .txt)":
        st.download_button(
            label="💾 Descargar Dossier Ejecutivo",
            data=dossier_bancario_md,
            file_name="Dossier_Patrimonial_Bancario.md",
            mime="text/markdown",
            use_container_width=True
        )
    else:
        st.info("💡 Para exportarlo en PDF limpio, pulsa el botón de abajo para visualizar el dossier adaptado y utiliza la opción 'Imprimir -> Guardar como PDF' de tu navegador.")
        if st.button("👁️ Previsualizar para Imprimir PDF", use_container_width=True):
            st.toast("Dossier listo al final de la barra lateral")
            st.sidebar.text_area("Copia o Imprime este texto:", value=dossier_bancario_md, height=300)


# ----- PESTAÑA 6: IA CHAT Y DICTAMEN -----
with tab_ia:
    st.subheader("🤖 Dictamen e Informe Estratégico de IA", anchor=False)
    
    if not st.session_state.get("api_key_guardada"):
        st.warning("🔒 Introduce tu Gemini API Key en la barra lateral para desbloquear la IA.")
    else:
        contexto_sistema = f"""
        Eres el mejor agente del mundo en asesoria financiera y gestion de patrimonio. Tu mision es orientar al usuario de forma analitica basandote en su perfil:
        - Flujos: Ingresos {du['ingresos_mensuales']} EUR/mes, Ahorro {du['ahorro_mensual_total']} EUR/mes, Pagas Extras: {du['dinero_extra_anual']} EUR/año.
        - Liquidez y Emergencias: Colchon de {du['capital_inicial']} EUR que cubre {meses_cobertura:.1f} meses de vida (Calificacion: {estado_seguridad}).
        - Activos actuales:\n{txt_activos}
        - Deudas y Pasivos:\n- Hipoteca: Debe {du['capital_pendiente']} EUR al {du['interes_anual_actual']}%.\n{txt_deudas}
        - Perfil Laboral: Empleado en {du['nombre_empresa']} con {du['antiguedad_trabajo']} años de antiguedad.
        - Objetivo Financiero: {num_libertad:.0f} EUR.
        
        REGLAS DE CONVERSACIÓN:
        1. Propon distribuciones en ETFs globales (MSCI World, S&P 500) o cuentas de alta remuneracion.
        2. Analiza especificamente el impacto de sus deudas actuales y proximas sobre su capacidad de inversion.
        3. Evalua su nivel de seguridad basandote en sus meses reales del Fondo de Emergencia.
        4. Escribe en Markdown profesional sin usar emojis ni simbolos de euro (usa la palabra 'EUR') para evitar roturas de codificacion.
        """

        col_btn, col_reset = st.columns([3, 1])
        with col_btn:
            if st.button("🚀 Generar Auditoría Patrimonial Completa", use_container_width=True):
                prompt_auditoria = f"""
                {contexto_sistema}
                Redacta un dictamen financiero macroeconomico inicial estructurado en 4 secciones claras:
                1. Analisis del Fondo de Emergencia actual frente a su matriz de deudas (actuales y proximas).
                2. Evaluacion del Asset Allocation frente a la inflacion de {du['inflacion_anual']}%.
                3. Critica de la salud financiera global ante el sector bancario (Score de credito segun su empresa y antiguedad).
                4. Recomendacion tactica personalizada para acelerar la meta de {num_libertad:.0f} EUR.
                """
                prompt_seguro = prompt_auditoria.replace("€", "EUR")
                prompt_seguro = "".join([c for c in prompt_seguro if ord(c) < 256])

                try:
                    genai.configure(api_key=st.session_state.api_key_guardada, transport='rest')
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    with st.spinner("La IA está auditando todo tu patrimonio consolidado..."):
                        response = model.generate_content(prompt_seguro)
                        st.session_state.auditoria_estatica = response.text
                        st.rerun()
                except Exception as e:
                    st.error(f"Error al generar auditoría: {e}")
        
        with col_reset:
            if st.button("🗑️ Limpiar Conversación", use_container_width=True):
                st.session_state.historial_chat = []
                st.session_state.auditoria_estatica = ""
                st.rerun()

        if st.session_state.auditoria_estatica:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("### 📋 Dictamen Financiero Estratégico Inicial")
                st.markdown(st.session_state.auditoria_estatica)

        st.markdown("---")
        st.markdown("#### 💬 Copiloto de Consultas Tácticas en Tiempo Real")

        for msg in st.session_state.historial_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if usuario_input := st.chat_input("Pregúntale a tu Asesor Patrimonial..."):
            with st.chat_message("user"):
                st.markdown(usuario_input)
            st.session_state.historial_chat.append({"role": "user", "content": usuario_input})

            historial_formateado = f"Auditoria Patrimonial Base:\n{st.session_state.auditoria_estatica}\n\n"
            for m in st.session_state.historial_chat:
                role_label = "Usuario" if m["role"] == "user" else "Asesor"
                historial_formateado += f"\n{role_label}: {m['content']}\n"

            prompt_completo = f"{contexto_sistema}\n\nHistorial:\n{historial_formateado}\nAsesor:"
            prompt_seguro = prompt_completo.replace("€", "EUR").encode("latin-1", "ignore").decode("latin-1")

            try:
                genai.configure(api_key=st.session_state.api_key_guardada, transport='rest')
                model = genai.GenerativeModel('gemini-2.5-flash')
                with st.spinner("Analizando impactos..."):
                    response = model.generate_content(prompt_seguro)
                    respuesta_ia = response.text
                    st.session_state.historial_chat.append({"role": "assistant", "content": respuesta_ia})
                    st.rerun()
            except Exception as e:
                st.error(f"Error al conectar con el asesor de IA: {e}")
