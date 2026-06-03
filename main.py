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
    du["ingresos_mensuales"] = st.number_input("Ingresos
