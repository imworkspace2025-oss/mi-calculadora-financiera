import streamlit as st
import pandas as pd
import math
import json
import plotly.express as px

# Configuración inicial
st.set_page_config(page_title="Terminal Patrimonial", layout="wide")

# Inicialización de estado si está vacío
if "datos_usuario" not in st.session_state:
    st.session_state.datos_usuario = {
        "ingresos_mensuales": 1500,
        "dinero_extra_anual": 2500,
        "ahorro_mensual_total": 300,
        "capital_inicial": 1000,
        "inversiones": [{"nombre": "Vivienda Manises", "tipo": "Rentabilidad Inmobiliaria (Ladrillo)", "valor_actual": 40000, "precio_compra": 30000, "gastos_iniciales": 10000, "alquiler_mensual": 660, "gastos_mensuales_inv": 300, "gastos_anuales": 500}],
        "deudas": []
    }

du = st.session_state.datos_usuario

# --- LÓGICA GLOBAL ---
ingresos_totales = du["ingresos_mensuales"] + (du["dinero_extra_anual"] / 12)
gastos_vivos = ingresos_totales - du["ahorro_mensual_total"]

# --- BARRA LATERAL ---
st.sidebar.title("⚙️ Configuración Global")
du["ingresos_mensuales"] = st.sidebar.number_input("Ingresos netos al mes (€)", value=du["ingresos_mensuales"])
du["dinero_extra_anual"] = st.sidebar.number_input("Pagas/Bonus extras al año (€)", value=du["dinero_extra_anual"])
du["ahorro_mensual_total"] = st.sidebar.number_input("Tu ahorro real al mes (€)", value=du["ahorro_mensual_total"])
du["capital_inicial"] = st.sidebar.number_input("Efectivo / Liquidez Total (€)", value=du["capital_inicial"])

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(["👑 Cuadro de Mandos", "🥗 Presupuesto", "📈 Inversión"])

with tab1:
    st.subheader("Cuadro de Mandos Patrimonial")
    c1, c2 = st.columns(2)
    c1.metric("Ingresos Totales Mensuales", f"{ingresos_totales:,.2f} €")
    c2.metric("Capacidad de Ahorro", f"{du['ahorro_mensual_total']} €")
    
    # Gráfica básica de ejemplo
    df_activos = pd.DataFrame(du["inversiones"])
    if not df_activos.empty:
        fig = px.pie(df_activos, values='valor_actual', names='nombre', title="Distribución de Activos")
        st.plotly_chart(fig)

with tab2:
    st.subheader("Presupuesto y Deudas")
    st.write(f"Tus gastos de vida actuales son: **{gastos_vivos:,.2f} €/mes**.")
    st.write("Gestiona tus deudas en el panel lateral si es necesario.")

with tab3:
    st.subheader("Inversión")
    st.write("Lista de activos actuales:")
    st.json(du["inversiones"])
    if st.button("Añadir inversión"):
        du["inversiones"].append({"nombre": "Nuevo Activo", "tipo": "Otro", "valor_actual": 0})
        st.rerun()

st.sidebar.success("✅ Dashboard sincronizado.")
