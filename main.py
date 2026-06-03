import streamlit as st
import google.generativeai as genai
import pandas as pd
import math
import json
import plotly.express as px

# 1. Configuración de pantalla
st.set_page_config(page_title="Cuadro de Mandos Financiero Pro", layout="wide")

# ==========================================
# 💾 MOTOR DE MEMORIA Y ESTADOS
# ==========================================
VALORES_POR_DEFECTO = {
    "ingresos_mensuales": 2500,
    "dinero_extra_anual": 3000,
    "ahorro_mensual_total": 600,
    "capital_inicial": 8000,
    "inflacion_anual": 2.5,
    "activar_crisis": False,
    "anos_proyeccion": 15,
    "inversiones": [],
    "tipo_hipoteca": "Fija",
    "capital_original": 150000,
    "capital_pendiente": 115000,
    "interes_anual_actual": 3.2,
    "cuota_mensual_actual": 580,
    "seguros_anuales_banco": 360,
    "deudas": []
}

if "datos_usuario" not in st.session_state:
    st.session_state.datos_usuario = VALORES_POR_DEFECTO.copy()

du = st.session_state.datos_usuario

def guardar_automatico():
    st.query_params["db"] = json.dumps(st.session_state.datos_usuario)

# ==========================================
# ⚙️ BARRA LATERAL (CORREGIDA)
# ==========================================
st.sidebar.title("⚙️ Configuración Global")

with st.sidebar.expander("📥 Tus Flujos de Caja", expanded=True):
    du["ingresos_mensuales"] = st.number_input("Ingresos netos al mes (€)", value=int(du["ingresos_mensuales"]), step=100, on_change=guardar_automatico)
    du["dinero_extra_anual"] = st.number_input("Pagas/Bonus extras al año (€)", value=int(du["dinero_extra_anual"]), step=500, on_change=guardar_automatico)
    du["ahorro_mensual_total"] = st.number_input("Tu ahorro real al mes (€)", value=int(du["ahorro_mensual_total"]), step=50, on_change=guardar_automatico)
    du["capital_inicial"] = st.number_input("Efectivo / Liquidez Total (€)", value=int(du["capital_inicial"]), step=500, on_change=guardar_automatico)

# ==========================================
# 🧮 LÓGICA (Simplificada para evitar errores de sintaxis)
# ==========================================
ingresos_totales = du["ingresos_mensuales"] + (du["dinero_extra_anual"] / 12)
gastos_vivos = ingresos_totales - du["ahorro_mensual_total"]

# ==========================================
# 📊 PESTAÑAS
# ==========================================
tab1, tab2, tab3 = st.tabs(["👑 Cuadro de Mandos", "🥗 Presupuesto", "📈 Inversión"])

with tab1:
    st.subheader("Cuadro de Mandos")
    st.metric("Ingresos Totales", f"{ingresos_totales:,.2f} €")
    
with tab2:
    st.subheader("Presupuesto")
    st.write(f"Gastos de vida estimados: {gastos_vivos:,.2f} €")

with tab3:
    st.subheader("Inversión")
    if st.button("➕ Añadir inversión"):
        du["inversiones"].append({"nombre": "Nuevo Activo", "valor": 0})
        guardar_automatico()
        st.rerun()
    st.write("Lista de activos:", du["inversiones"])

st.sidebar.markdown("---")
st.sidebar.caption("✅ Sistema listo y funcional.")
