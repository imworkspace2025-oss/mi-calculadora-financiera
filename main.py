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

# Cálculos transversales básicos
ingreso_extra_prorrateado = du["dinero_extra_anual"] / 12
ingresos_totales = du["ingresos_mensuales"] + ingreso_extra_prorrateado
gastos_mensuales_vivos = ingresos_totales - du["ahorro_mensual_total"]
num_libertad = (gastos_mensuales_vivos * 12) * 25

# Sumas dinámicas de deudas extras introducidas por el usuario
total_cuotas_deudas_extra = sum(float(d["cuota_mensual"]) for d in du["deudas"] if d["tipo"] == "Actual")
total_pendiente_deudas_extra = sum(float(d["pendiente"]) for d in du["deudas"] if d["tipo"] == "Actual")

# Pestañas principales
tab_resumen, tab_presupuesto, tab_inversion, tab_hipoteca, tab_libertad, tab_ia = st.tabs([
    "👑 Cuadro de Mandos", "🥗 Presupuesto y Deudas", "📈 Rentabilidad e Inversión", 
    "🏠 Consultor Hipotecario", "🕊️ Horizonte Independencia", "🤖 Dictamen e IA Chat"
])

# ==========================================
# 📥 MOTOR DINÁMICO DE ACTIVOS E INVERSIONES
# ==========================================
patrimonio_inversiones_total = 0.0
cronologia_anos = list(range(1, du["anos_proyeccion"] + 1))
datos_grafica_nominal = {"Año": cronologia_anos}
datos_grafica_real = {"Año": cronologia_anos}
dict_distribucion_activos = {"Efectivo": du["capital_inicial"]}

for item in du.get("inversiones", []):
    dict_distribucion_activos[item["nombre"]] = item["valor_actual"]

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

            proyeccion_nominal, proyeccion_real = [], []
            if inv["tipo"] == "Interés Compuesto (ETFs / Fondos)":
                c1, c2, c3 = st.columns(3)
                with c1: inv["valor_actual"] = st.number_input("Capital actual (€)", value=float(inv["valor_actual"]), key=f"f1_{idx}", on_change=guardar_automatico)
                with c2: inv["aportacion_mensual"] = st.number_input("Inyección al mes (€)", value=float(inv["aportacion_mensual"]), key=f"f2_{idx}", on_change=guardar_automatico)
                with c3: inv["interes_anual"] = st.number_input("Rendimiento anual Neto (%)", value=float(inv["interes_anual"]), key=f"f3_{idx}", on_change=guardar_automatico)
                
                patrimonio_inversiones_total += inv["valor_actual"]
                acumulado_nom, acumulado_real = inv["valor_actual"], inv["valor_actual"]
                for i, ano in enumerate(cronologia_anos):
                    if du["activar_crisis"] and ano == 2:
                        acumulado_nom *= 0.75; acumulado_real *= 0.75
                    acumulado_nom = (acumulado_nom + (inv["aportacion_mensual"] * 12)) * (1 + (inv["interes_anual"] / 100))
                    proyeccion_nominal.append(acumulado_nom)
                    rendimiento_real = (inv["interes_anual"] - du["inflacion_anual"]) / 100
                    acumulado_real = (acumulado_real + (inv["aportacion_mensual"] * 12)) * (1 + rendimiento_real)
                    proyeccion_real.append(acumulado_real)

            elif inv["tipo"] == "Rentabilidad Inmobiliaria (Ladrillo)":
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1: inv["precio_compra"] = st.number_input("Precio compra (€)", value=float(inv["precio_compra"]), key=f"l1_{idx}", on_change=guardar_automatico)
                with c2: inv["gastos_iniciales"] = st.number_input("Gastos/Impuestos iniciales (€)", value=float(inv["gastos_iniciales"]), key=f"l2_{idx}", on_change=guardar_automatico)
                with c3: inv["alquiler_mensual"] = st.number_input("Renta mensual (€)", value=float(inv["alquiler_mensual"]), key=f"l3_{idx}", on_change=guardar_automatico)
                with c4: inv["gastos_mensuales_inv"] = st.number_input("Gastos fijos al MES (€)", value=float(inv["gastos_mensuales_inv"]), key=f"l5_{idx}", on_change=guardar_automatico)
                with c5: inv["gastos_anuales"] = st.number_input("Gastos fijos al AÑO (€)", value=float(inv["gastos_anuales"]), key=f"l4_{idx}", on_change=guardar_automatico)

                inv["valor_actual"] = inv["precio_compra"] + inv["gastos_iniciales"]
                patrimonio_inversiones_total += inv["valor_actual"]
                flujo_neto = (inv["alquiler_mensual"] * 12) - (inv["gastos_mensuales_inv"] * 12) - inv["gastos_anuales"]
                acumulado_nom, acumulado_real = inv["valor_actual"], inv["valor_actual"]
                for ano in cronologia_anos:
                    acumulado_nom += flujo_neto
                    proyeccion_nominal.append(acumulado_nom)
                    acumulado_real += (flujo_neto / ((1 + (du["inflacion_anual"]/100)) ** ano))
                    proyeccion_real.append(acumulado_real)

            elif inv["tipo"] == "Activos Estáticos / Otros":
                c1, c2 = st.columns(2)
                with c1: inv["capital_invertido"] = st.number_input("Original invertido (€)", value=float(inv["capital_invertido"]), key=f"r1_{idx}", on_change=guardar_automatico)
                with c2: inv["valor_final"] = st.number_input("Valor de mercado (€)", value=float(inv["valor_final"]), key=f"r2_{idx}", on_change=guardar_automatico)
                inv["valor_actual"] = inv["valor_final"]
                patrimonio_inversiones_total += inv["valor_actual"]
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
