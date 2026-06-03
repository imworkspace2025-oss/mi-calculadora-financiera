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

st.title("📊 BIENVENIDO A TU TERMINAL PATRIMONIAL TOP")
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

# Carga inicial o lectura desde la URL
if "db" not in st.query_params:
    if "datos_usuario" not in st.session_state:
        st.session_state.datos_usuario = VALORES_POR_DEFECTO.copy()
else:
    try:
        st.session_state.datos_usuario = json.loads(st.query_params["db"])
    except:
        if "datos_usuario" not in st.session_state:
            st.session_state.datos_usuario = VALORES_POR_DEFECTO.copy()

du = st.session_state.datos_usuario

def guardar_automatico():
    st.query_params["db"] = json.dumps(st.session_state.datos_usuario)

# ==========================================
# ⚙️ BARRA LATERAL AVANZADA (ENTRADA GLOBAL)
# ==========================================
st.sidebar.title("⚙️ Configuración Global")

with st.sidebar.expander("🔑 Inteligencia Artificial (Gemini)", expanded=False):
    api_key_input = st.text_input("Introduce tu API Key:", type="password")

with st.sidebar.expander("📥 Tus Flujos de Caja", expanded=True):
    du["ingresos_mensuales"] = st.number_input("Ingresos netos al mes (€)", value=du["ingresos_mensuales"], step=100, on_change=guardar_automatico)
    du["dinero_extra_anual"] = st.number_input("Pagas/Bonus extras al año (€)", value=du["dinero_extra_anual"], step=500, on_change=guardar_automatico)
    du["ahorro_mensual_total"] = st.number_input("Tu ahorro real al mes (€)", value=du["ahorro_mensual_total"], step=50, on_change=guardar_automatico)
    du["capital_inicial"] = st.number_input("Efectivo / Fondo Emergencia (€)", value=du["capital_inicial"], step=500, on_change=guardar_automatico)

with st.sidebar.expander("🛡️ Simulador de Entorno Económico", expanded=True):
    du["inflacion_anual"] = st.number_input("Inflación anual estimada (%)", value=float(du["inflacion_anual"]), step=0.1, on_change=guardar_automatico)
    du["anos_proyeccion"] = st.slider("Años a proyectar en el futuro", min_value=5, max_value=40, value=int(du["anos_proyeccion"]), step=1, on_change=guardar_automatico)
    du["activar_crisis"] = st.toggle("💥 Activar 'Test de Estrés' (Crisis de mercado)", value=bool(du["activar_crisis"]), on_change=guardar_automatico)
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
for item in du["inversiones"]:
    dict_distribucion_activos[item["nombre"]] = item["valor_actual"]

with tab_inversion:
    st.subheader("💼 Matriz Patrimonial y Asignación de Activos")
    
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

    for idx, inv in enumerate(du["inversiones"]):
        with st.container(border=True):
            col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
            with col_c1:
                inv["nombre"] = st.text_input("Identificador del Activo:", value=inv["nombre"], key=f"inv_name_{idx}", on_change=guardar_automatico)
            with col_c2:
                inv["tipo"] = st.selectbox(
                    "Naturaleza del activo:", 
                    ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "ROI Simple"],
                    index=["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "ROI Simple"].index(inv["tipo"]),
                    key=f"inv_tipo_{idx}", on_change=guardar_automatico
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
                with c1: inv["valor_actual"] = st.number_input("Capital actual (€)", value=float(inv["valor_actual"]), key=f"f1_{idx}", step=500.0, on_change=guardar_automatico)
                with c2: inv["aportacion_mensual"] = st.number_input("Inyección mensual (€)", value=float(inv["aportacion_mensual"]), key=f"f2_{idx}", step=50.0, on_change=guardar_automatico)
                with c3: inv["interes_anual"] = st.number_input("Rendimiento anual Neto (%)", value=float(inv["interes_anual"]), key=f"f3_{idx}", step=0.5, on_change=guardar_automatico)
                
                patrimonio_inversiones_total += inv["valor_actual"]
                dict_distribucion_activos[inv["nombre"]] = inv["valor_actual"]
                
                acumulado_nom = inv["valor_actual"]
                acumulado_real = inv["valor_actual"]
                for i, ano in enumerate(cronologia_anos):
                    # Simulación de crisis en el año 2 si está activada
                    if du["activar_crisis"] and ano == 2:
                        acumulado_nom = acumulado_nom * 0.75
                        acumulado_real = acumulado_real * 0.75
                    
                    acumulado_nom = (acumulado_nom + (inv["aportacion_mensual"] * 12)) * (1 + (inv["interes_anual"] / 100))
                    proyeccion_nominal.append(acumulado_nom)
                    
                    # Descontamos el efecto inflación de manera compuesta
                    rendimiento_real = (inv["interes_anual"] - du["inflacion_anual"]) / 100
                    acumulado_real = (acumulado_real + (inv["aportacion_mensual"] * 12)) * (1 + rendimiento_real)
                    proyeccion_real.append(acumulado_real)

            elif inv["tipo"] == "Rentabilidad Inmobiliaria (Ladrillo)":
                c1, c2, c3, c4 = st.columns(4)
                with c1: inv["precio_compra"] = st.number_input("Precio compra (€)", value=float(inv["precio_compra"]), key=f"l1_{idx}", step=5000.0, on_change=guardar_automatico)
                with c2: inv["gastos_iniciales"] = st.number_input("Reformas e Impuestos (€)", value=float(inv["gastos_iniciales"]), key=f"l2_{idx}", step=1000.0, on_change=guardar_automatico)
                with c3: inv["alquiler_mensual"] = st.number_input("Renta mensual líquida (€)", value=float(inv["alquiler_mensual"]), key=f"l3_{idx}", step=50.0, on_change=guardar_automatico)
                with c4: inv["gastos_anuales"] = st.number_input("Gastos de explotación/año (€)", value=float(inv["gastos_anuales"]), key=f"l4_{idx}", step=100.0, on_change=guardar_automatico)
                
                inv["valor_actual"] = inv["precio_compra"] + inv["gastos_iniciales"]
                patrimonio_inversiones_total += inv["valor_actual"]
                dict_distribucion_activos[inv["nombre"]] = inv["valor_actual"]
                
                flujo_neto = (inv["alquiler_mensual"] * 12) - inv["gastos_anuales"]
                acumulado_nom = inv["valor_actual"]
                acumulado_real = inv["valor_actual"]
                for ano in cronologia_anos:
                    acumulado_nom += flujo_neto
                    proyeccion_nominal.append(acumulado_nom)
                    
                    # El ladrillo suele indexarse a la inflación, simulamos estabilidad de poder adquisitivo
                    acumulado_real += (flujo_neto / ((1 + (du["inflacion_anual"]/100)) ** ano))
                    proyeccion_real.append(acumulado_real)

            elif inv["tipo"] == "ROI Simple":
                c1, c2 = st.columns(2)
                with c1: inv["capital_invertido"] = st.number_input("Dinero aportado original (€)", value=float(inv["capital_invertido"]), key=f"r1_{idx}", step=500.0, on_change=guardar_automatico)
                with c2: inv["valor_final"] = st.number_input("Valor de valoración actual (€)", value=float(inv["valor_final"]), key=f"r2_{idx}", step=500.0, on_change=guardar_automatico)
                
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
    st.subheader("🏠 Análisis Técnico y Estratégico de Deuda Bancaria")
    col1, col2, col3, col4 = st.columns(4)
    with col1: du["tipo_hipoteca"] = st.selectbox("Tipo de interés:", ["Fija", "Variable", "Mixta"], index=["Fija", "Variable", "Mixta"].index(du["tipo_hipoteca"]), on_change=guardar_automatico)
    with col2: du["capital_original"] = st.number_input("Capital prestado original (€)", value=int(du["capital_original"]), step=5000, on_change=guardar_automatico)
    with col3: du["capital_pendiente"] = st.number_input("Capital vivo actual (€)", value=int(du["capital_pendiente"]), step=5000, on_change=guardar_automatico)
    with col4: du["interes_anual_actual"] = st.number_input("Tipo de interés anual (%)", value=float(du["interes_anual_actual"]), step=0.1, on_change=guardar_automatico)
    
    col5, col6, col7, col8 = st.columns(4)
    with col5: du["cuota_mensual_actual"] = st.number_input("Cuota del recibo mensual (€)", value=int(du["cuota_mensual_actual"]), step=50, on_change=guardar_automatico)
    with col6: du["seguros_anuales_banco"] = st.number_input("Seguros obligatorios / año (€)", value=int(du["seguros_anuales_banco"]), step=50, on_change=guardar_automatico)
    with col7: du["amortizacion_extra"] = st.number_input("Plan amortización extra mensual (€)", value=int(du["amortizacion_extra"]), step=50, on_change=guardar_automatico)
    with col8: du["inyeccion_capital_unica"] = st.number_input("Inyección amortización única ya (€)", value=int(du["inyeccion_capital_unica"]), step=1000, on_change=guardar_automatico)

    tasa_mensual = (du["interes_anual_actual"] / 100) / 12
    coste_mensual_seguros = du["seguros_anuales_banco"] / 12
    cuota_financiera_verdadera = du["cuota_mensual_actual"] + coste_mensual_seguros

    if du["cuota_mensual_actual"] > (du["capital_pendiente"] * tasa_mensual):
        interes_mes_actual = du["capital_pendiente"] * tasa_mensual
        amortizacion_capital_mes = du["cuota_mensual_actual"] - interes_mes_actual
        meses_contrato = -math.log(1 - (du["capital_pendiente"] * tasa_mensual) / du["cuota_mensual_actual"]) / math.log(1 + tasa_mensual)
        anos_contrato_restantes = meses_contrato / 12
        intereses_totales_banco = (du["cuota_mensual_actual"] * meses_contrato) - du["capital_pendiente"]
    else:
        interes_mes_actual, amortizacion_capital_mes, anos_contrato_restantes, intereses_totales_banco = 0, 0, 0, 0

# ==========================================
# 📊 VISUALIZACIÓN DE MÉTRICAS PREMIUM (PESTAÑA 1)
# ==========================================
with tab_resumen:
    st.subheader("🏁 Cuadro de Mandos Patrim
