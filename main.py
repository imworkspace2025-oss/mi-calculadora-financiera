import streamlit as st
import google.generativeai as genai
import pandas as pd
import math
import json
import plotly.express as px
from fpdf import FPDF
import io

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

from supabase import create_client

# ----------------------------------------------------------------------
# 🔐 MOTOR DE USUARIOS Y LOGIN (SUPABASE)
# ----------------------------------------------------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    st.session_state["usuario_actual"] = ""

if not st.session_state["autenticado"]:
    st.title("🔐 Acceso a Movana Pro")
    
    pestana_login, pestana_registro = st.tabs(["Iniciar Sesión", "Crear Cuenta Nueva"])
    
    with pestana_login:
        usuario = st.text_input("Usuario / Email", key="login_user")
        contrasena = st.text_input("Contraseña", type="password", key="login_pass")
        
        if st.button("Entrar al Terminal Patrimonial", type="primary"):
            resultado = supabase.table("perfiles_usuarios").select("*").eq("usuario", usuario).execute()
            
            if resultado.data and resultado.data[0]["contrasena"] == contrasena:
                st.session_state["autenticado"] = True
                st.session_state["usuario_actual"] = usuario
                st.success("¡Acceso concedido!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
                
    with pestana_registro:
        nuevo_usuario = st.text_input("Elige un nombre de usuario", key="reg_user")
        nueva_contrasena = st.text_input("Elige una contraseña", type="password", key="reg_pass")
        confirmar_pass = st.text_input("Repite la contraseña", type="password", key="reg_confirm")
        
        if st.button("Registrar Cuenta Nueva"):
            if nuevo_usuario == "" or nueva_contrasena == "":
                st.warning("Por favor, rellena todos los campos.")
            elif nueva_contrasena != confirmar_pass:
                st.error("Las contraseñas no coinciden.")
            else:
                comprobacion = supabase.table("perfiles_usuarios").select("*").eq("usuario", nuevo_usuario).execute()
                if comprobacion.data:
                    st.error("Este nombre de usuario ya está registrado.")
                else:
                    supabase.table("perfiles_usuarios").insert({
                        "usuario": nuevo_usuario,
                        "contrasena": nueva_contrasena,
                        "datos_financieros": {}
                    }).execute()
                    st.success("¡Cuenta creada con éxito! Ya puedes iniciar sesión en la pestaña de al lado.")

    st.stop()

# ----------------------------------------------------------------------
# A PARTIR DE AQUÍ SE CORRERÁ TU CÓDIGO CUANDO TE LOGUEES:
# ----------------------------------------------------------------------
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
            "valor_final": 6500.0,
            "financiacion_inmueble": 80000.0  
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
    ],
    "impuesto_renta_variable": 19.0,
    "impuesto_inmobiliario": 20.0,
    "estres_euribor": 0.0,
    "estres_vacancia": 0,
    "estres_caida_bolsa": 0.0
}

if "datos_usuario" not in st.session_state:
    st.session_state.datos_usuario = VALORES_POR_DEFECTO.copy()

if "mensajes_chat" not in st.session_state:
    st.session_state.mensajes_chat = []

if "auditoria_estatica" not in st.session_state:
    st.session_state.auditoria_estatica = ""

# Blindaje anti-keyerror dinámico
for clave, valor in VALORES_POR_DEFECTO.items():
    if clave not in st.session_state.datos_usuario:
        st.session_state.datos_usuario[clave] = valor

du = st.session_state.datos_usuario

# Asegurar sub-estructuras de activos inmobiliarios
for item in du.get("inversiones", []):
    if "gastos_mensuales_inv" not in item: item["gastos_mensuales_inv"] = 0.0
    if "financiacion_inmueble" not in item: item["financiacion_inmueble"] = 0.0

def guardar_automatico():
    st.query_params["db"] = json.dumps(st.session_state.datos_usuario)

# ==========================================
# ⚙️ BARRA LATERAL AVANZADA (ENTRADA GLOBAL)
# ==========================================
st.sidebar.title("⚙️ Configuración Global")

st.session_state.api_key_guardada = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar.expander("📥 Tus Flujos de Caja", expanded=True):
    du["ingresos_mensuales"] = st.number_input("Ingresos netos al mes (€)", value=int(du["ingresos_mensuales"]), step=100, on_change=guardar_automatico)
    du["dinero_extra_anual"] = st.number_input("Pagas/Bonus extras al año (€)", value=int(du["dinero_extra_anual"]), step=500, on_change=guardar_automatico)
    du["ahorro_mensual_total"] = st.number_input("Tu ahorro real al mes (€)", value=int(du["ahorro_mensual_total"]), step=50, on_change=guardar_automatico)
    du["capital_inicial"] = st.number_input("Efectivo / Liquidez Total (€)", value=int(du["capital_inicial"]), step=500, on_change=guardar_automatico)

with st.sidebar.expander("⚖️ Módulo Fiscal (Impuestos)", expanded=False):
    du["impuesto_renta_variable"] = st.slider("Retención s/ Plusvalías Bolsa (%)", 19.0, 28.0, float(du["impuesto_renta_variable"]), step=0.5, on_change=guardar_automatico)
    du["impuesto_inmobiliario"] = st.slider("Tramo impositivo neto Alquiler (%)", 0.0, 47.0, float(du["impuesto_inmobiliario"]), step=1.0, on_change=guardar_automatico)

with st.sidebar.expander("🛡️ Test de Estrés Macroeconómico", expanded=False):
    du["inflacion_anual"] = st.number_input("Inflación anual estimada (%)", value=float(du["inflacion_anual"]), step=0.1, on_change=guardar_automatico)
    du["anos_proyeccion"] = st.slider("Años a proyectar en el futuro", min_value=5, max_value=40, value=int(du["anos_proyeccion"]), step=1, on_change=guardar_automatico)
    st.markdown("**Simular Escenarios de Riesgo:**")
    du["estres_euribor"] = st.slider("Simular Subida del Euríbor (+%)", 0.0, 5.0, float(du["estres_euribor"]), step=0.25, on_change=guardar_automatico)
    du["estres_caida_bolsa"] = st.slider("Simular Crack Bursátil Año 2 (-%)", 0.0, 50.0, float(du["estres_caida_bolsa"]), step=5.0, on_change=guardar_automatico)
    du["estres_vacancia"] = st.slider("Meses inmueble vacío (Sin Rentas/Año)", 0, 6, int(du["estres_vacancia"]), step=1, on_change=guardar_automatico)

with st.sidebar.expander("💳 Perfil Crediticio y Laboral", expanded=False):
    du["nombre_empresa"] = st.text_input("Nombre de la empresa / pagador:", value=str(du["nombre_empresa"]), on_change=guardar_automatico)
    du["antiguedad_trabajo"] = st.number_input("Tu antigüedad en este empleo (Años)", min_value=0, max_value=50, value=int(du["antiguedad_trabajo"]), on_change=guardar_automatico)
    du["es_autonomo_empresa"] = st.toggle("💼 ¿Eres Autónomo o Empresa?", value=bool(du["es_autonomo_empresa"]), on_change=guardar_automatico)
    if du["es_autonomo_empresa"]:
        du["facturacion_anual"] = st.number_input("Facturación bruta anual (€)", value=int(du["facturacion_anual"]), step=5000, on_change=guardar_automatico)


# ==========================================
# 🧮 MOTOR MATEMÁTICO INTEGRADO
# ==========================================
ingreso_extra_prorrateado = du["dinero_extra_anual"] / 12
ingresos_totales = du["ingresos_mensuales"] + ingreso_extra_prorrateado
gastos_mensuales_vivos = ingresos_totales - du["ahorro_mensual_total"]
num_libertad = (gastos_mensuales_vivos * 12) * 25

total_cuotas_deudas_extra = sum(float(d["cuota_mensual"]) for d in du["deudas"] if d["tipo"] == "Actual")
total_pendiente_deudas_extra = sum(float(d["pendiente"]) for d in du["deudas"] if d["tipo"] == "Actual")

# ✅ SOLUCIÓN AL NAMEERROR: Definimos correctamente la deuda consolidada global aquí
deuda_consolidada = du["capital_pendiente"] + total_pendiente_deudas_extra

# Impacto del Estrés del Euríbor en la hipoteca si no es fija
interes_hipoteca_estresado = du["interes_anual_actual"]
if du["tipo_hipoteca"] != "Fija":
    interes_hipoteca_estresado += du["estres_euribor"]

tasa_mensual = (interes_hipoteca_estresado / 100) / 12
coste_mensual_seguros = du["seguros_anuales_banco"] / 12

# Recalcular cuota hipotecaria si sube el Euríbor
cuota_hipotecaria_final = du["cuota_mensual_actual"]
if du["estres_euribor"] > 0 and du["tipo_hipoteca"] != "Fija" and du["capital_pendiente"] > 0:
    cuota_hipotecaria_final = (du["capital_pendiente"] * tasa_mensual) / (1 - (1 + tasa_mensual)**(-180)) 

patrimonio_inversiones_total = 0.0
cronologia_anos = list(range(1, du["anos_proyeccion"] + 1))
datos_grafica_nominal = {"Año": cronologia_anos}
datos_grafica_real = {"Año": cronologia_anos}
dict_distribucion_activos = {"Efectivo": du["capital_inicial"]}

# Almacén de métricas inmobiliarias avanzadas calculadas en tiempo de ejecución
metricas_ladrillo = {}

for idx, inv in enumerate(du.get("inversiones", [])):
    proyeccion_nominal, proyeccion_real = [], []
    
    if inv["tipo"] == "Interés Compuesto (ETFs / Fondos)":
        patrimonio_inversiones_total += inv["valor_actual"]
        acumulado_nom, acumulado_real = inv["valor_actual"], inv["valor_actual"]
        
        for ano in cronologia_anos:
            if du["estres_caida_bolsa"] > 0 and ano == 2:
                acumulado_nom *= (1 - (du["estres_caida_bolsa"] / 100))
                acumulado_real *= (1 - (du["estres_caida_bolsa"] / 100))
            
            rendimiento_bruto = inv["interes_anual"] / 100
            rendimiento_neto_fiscal = rendimiento_bruto * (1 - (du["impuesto_renta_variable"] / 100))
            
            acumulado_nom = (acumulado_nom + (inv["aportacion_mensual"] * 12)) * (1 + rendimiento_neto_fiscal)
            proyeccion_nominal.append(acumulado_nom)
            
            rendimiento_real = rendimiento_neto_fiscal - (du["inflacion_anual"] / 100)
            acumulado_real = (acumulado_real + (inv["aportacion_mensual"] * 12)) * (1 + rendimiento_real)
            proyeccion_real.append(acumulado_real)

    elif inv["tipo"] == "Rentabilidad Inmobiliaria (Ladrillo)":
        inv["valor_actual"] = inv["precio_compra"] + inv["gastos_iniciales"]
        patrimonio_inversiones_total += inv["valor_actual"]
        
        meses_con_renta = max(0, 12 - du["estres_vacancia"])
        ingreso_anual_alquiler = inv["alquiler_mensual"] * meses_con_renta
        
        flujo_neto_antes_impuestos = ingreso_anual_alquiler - (inv["gastos_mensuales_inv"] * 12) - inv["gastos_anuales"]
        flujo_neto_real = flujo_neto_antes_impuestos * (1 - (du["impuesto_inmobiliario"] / 100))
        
        capital_propio_invertido = inv["valor_actual"] - inv["financiacion_inmueble"]
        if capital_propio_invertido <= 0: capital_propio_invertido = inv["gastos_iniciales"] if inv["gastos_iniciales"] > 0 else 1.0
        
        cap_rate_bruto = (ingreso_anual_alquiler / inv["precio_compra"]) * 100 if inv["precio_compra"] > 0 else 0
        cap_rate_neto = (flujo_neto_real / inv["precio_compra"]) * 100 if inv["precio_compra"] > 0 else 0
        cash_on_cash = (flujo_neto_real / capital_propio_invertido) * 100
        
        metricas_ladrillo[inv["nombre"]] = {
            "cap_bruto": cap_rate_bruto,
            "cap_neto": cap_rate_neto,
            "coc": cash_on_cash,
            "equity_real": capital_propio_invertido
        }
        
        acumulado_nom, acumulado_real = inv["valor_actual"], inv["valor_actual"]
        for ano in cronologia_anos:
            acumulado_nom += flujo_neto_real
            proyeccion_nominal.append(acumulado_nom)
            acumulado_real += (flujo_neto_real / ((1 + (du["inflacion_anual"]/100)) ** ano))
            proyeccion_real.append(acumulado_real)

    elif inv["tipo"] in ["Activos Estáticos / Otros", "Activos Estáticos / Others"]:
        inv["valor_actual"] = inv["valor_final"]
        patrimonio_inversiones_total += inv["valor_actual"]
        for ano in cronologia_anos:
            proyeccion_nominal.append(inv["valor_actual"])
            proyeccion_real.append(inv["valor_actual"] / ((1 + (du["inflacion_anual"]/100)) ** ano))

    datos_grafica_nominal[inv["nombre"]] = proyeccion_nominal
    datos_grafica_real[inv["nombre"]] = proyeccion_real

for item in du.get("inversiones", []):
    dict_distribucion_activos[item["nombre"]] = item["valor_actual"]

patrimonio_neto_global = du["capital_inicial"] + patrimonio_inversiones_total
patrimonio_liquido_real_neto = patrimonio_neto_global - du["capital_pendiente"] - total_pendiente_deudas_extra

if cuota_hipotecaria_final > (du["capital_pendiente"] * tasa_mensual) and tasa_mensual > 0:
    meses_contrato = -math.log(1 - (du["capital_pendiente"] * tasa_mensual) / cuota_hipotecaria_final) / math.log(1 + tasa_mensual)
    anos_contrato_restantes = meses_contrato / 12
    intereses_totales_banco = (cuota_hipotecaria_final * meses_contrato) - du["capital_pendiente"]
else:
    anos_contrato_restantes, intereses_totales_banco = 0, 0

gastos_mensuales_totales = cuota_hipotecaria_final + total_cuotas_deudas_extra + gastos_mensuales_vivos
meses_cobertura = du["capital_inicial"] / gastos_mensuales_totales if gastos_mensuales_totales > 0 else 0

if meses_cobertura < 3:
    estado_seguridad = "Bajo Mínimos"
else:
    estado_seguridad = "Saludable / Estándar" if meses_cobertura <= 6 else "Excelente"


# ==========================================
# 📊 GENERACIÓN GLOBAL DE GRÁFICOS (DASHBOARD)
# ==========================================
df_pie = pd.DataFrame({"Activo": list(dict_distribucion_activos.keys()), "Valor (€)": list(dict_distribucion_activos.values())})
fig_pie = px.pie(df_pie, values="Valor (€)", names="Activo", hole=0.4, title="Asset Allocation Actual")
fig_pie.update_layout(height=260, margin=dict(t=30, b=10, l=10, r=10))

df_prep_nom = pd.DataFrame(datos_grafica_nominal).set_index("Año")
df_total_nom = pd.DataFrame({"Valor Nominal": df_prep_nom.sum(axis=1)})
df_prep_real = pd.DataFrame(datos_grafica_real).set_index("Año")
df_total_real = pd.DataFrame({"Valor Real Corregido": df_prep_real.sum(axis=1)})
df_melted = df_total_nom.join(df_total_real).reset_index().melt(id_vars=["Año"], var_name="Métrica", value_name="Capital (€)")

fig_lineas = px.line(df_melted, x="Año", y="Capital (€)", color="Métrica", title="Evolución del Patrimonio Bajo Inflación")

# --- HISTÓRICO DE EVOLUCIÓN PATRIMONIAL ---
meses_historico = ["Ene 26", "Feb 26", "Mar 26", "Abr 26", "May 26", "Jun 26"]
patrimonio_base_simulado = patrimonio_liquido_real_neto
valores_historicos = [
    patrimonio_base_simulado * 0.92,
    patrimonio_base_simulado * 0.94,
    patrimonio_base_simulado * 0.95,
    patrimonio_base_simulado * 0.97,
    patrimonio_base_simulado * 0.99,
    patrimonio_base_simulado
]
df_historico_real = pd.DataFrame({"Mes": meses_historico, "Patrimonio Neto (€)": valores_historicos})
fig_historico_linea = px.line(df_historico_real, x="Mes", y="Patrimonio Neto (€)", title="Línea de Tiempo: Evolución Real de tu Patrimonio Neto", markers=True)

# ✅ SOLUCIÓN AL VALUEERROR: Usamos line_width en lugar de width para que Plotly no falle
fig_historico_linea.update_traces(line_color="#0f172a", line_width=3)


# ==========================================
# 📥 FUNCIÓN EXPORTACIÓN PDF (ESTILO BANCA PRIVADA)
# ==========================================
def generar_pdf_premium_bytes():
    tasa_ahorro_aux = (du["ahorro_mensual_total"] / ingresos_totales) * 100 if ingresos_totales > 0 else 0

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()
    
    COLOR_PRIMARY = (15, 23, 42)     
    COLOR_SECONDARY = (71, 85, 105)  
    COLOR_BG_TABLE = (241, 245, 249) 
    COLOR_TEXT = (51, 65, 85)        
    
    # Cabecera
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, "MOVANA PATRIMONIAL", ln=True, align="L")
    
    pdf.set_text_color(*COLOR_SECONDARY)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(100, 5, "Terminal Avanzado de Gestión de Activos & Riesgos", align="L")
    pdf.cell(0, 5, "CÓDIGO DE AUDITORÍA: MV-2026-CONF", align="R", ln=True)
    
    pdf.set_draw_color(*COLOR_SECONDARY)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y() + 2, 200, pdf.get_y() + 2)
    pdf.ln(8)
    
    # Metadatos del informe bancario
    pdf.set_fill_color(*COLOR_BG_TABLE)
    pdf.rect(10, pdf.get_y(), 190, 15, "F")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.text(14, pdf.get_y() + 6, "INFORME PREPARADO PARA:")
    pdf.text(14, pdf.get_y() + 11, f"Titular del Canal ({st.session_state.usuario_actual})")
    pdf.text(120, pdf.get_y() + 6, "FECHA DE CERTIFICACIÓN:")
    pdf.text(120, pdf.get_y() + 11, "05 de Junio, 2026")
    pdf.ln(20)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*COLOR_TEXT)
    intro_txt = (
        "El presente dossier técnico consolida y audita las métricas de balance del solicitante. "
        "Ha sido estructurado bajo metodologías de scoring bancario de banca privada para medir la solidez de "
        "los flujos, la rentabilidad neta real post-impuestos y la resiliencia ante escenarios críticos de mercado."
    )
    pdf.multi_cell(0, 5, intro_txt.encode('latin-1', 'ignore').decode('latin-1'))
    pdf.ln(6)
    
    # Tabla estilo institucional
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Indicadores Base de Flujo de Caja", ln=True)
    pdf.ln(2)
    
    pdf.set_fill_color(*COLOR_PRIMARY)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(95, 7, " Concepto de Balance Analizado", border=0, fill=True)
    pdf.cell(95, 7, " Valor Certificado / Estado Actual", border=0, fill=True, ln=True)
    
    datos_tabla = [
        ["Entidad de Origen Declarada:", f" {du['nombre_empresa']} (Antigüedad: {du['antiguedad_trabajo']} años)"],
        ["Ingresos Netos Consolidados:", f" {ingresos_totales:,.2f} EUR/mes (Prorrateado con extras)"],
        ["Capacidad de Ahorro Limpia:", f" {du['ahorro_mensual_total']:,} EUR/mes (Tasa: {tasa_ahorro_aux:.1f}%)"],
        ["Fondo de Contingencia Neto:", f" {du['capital_inicial']:,} EUR ({meses_cobertura:.1f} meses - {estado_seguridad})"]
    ]
    
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_font("Helvetica", "", 9)
    alternar_color = False
    
    for fila in datos_tabla:
        pdf.set_fill_color(*COLOR_BG_TABLE) if alternar_color else pdf.set_fill_color(255, 255, 255)
        pdf.cell(95, 7, fila[0].encode('latin-1', 'ignore').decode('latin-1'), border="B", fill=True)
        pdf.cell(95, 7, fila[1].encode('latin-1', 'ignore').decode('latin-1'), border="B", fill=True, ln=True)
        alternar_color = not alternar_color
    pdf.ln(8)
    
    # Asset Allocation Grafico
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Asignación Patrimonial Dinámica (Asset Allocation)", ln=True)
    pdf.ln(2)
    
    try:
        from PIL import Image
        img_pie_bytes = fig_pie.to_image(format="png", width=700, height=320, scale=2)
        img_pie_pil = Image.open(io.BytesIO(img_pie_bytes))
        pdf.image(img_pie_pil, x=15, y=pdf.get_y(), w=180)
        pdf.ln(85)
    except Exception:
        pdf.ln(4)

    pdf.add_page()
    
    # Grafico de Proyección
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"3. Proyección de Capital a {du['anos_proyeccion']} años (Efecto Inflación e Impuestos)", ln=True)
    pdf.ln(2)
    
    try:
        from PIL import Image
        img_lines_bytes = fig_lineas.to_image(format="png", width=700, height=320, scale=2)
        img_lines_pil = Image.open(io.BytesIO(img_lines_bytes))
        pdf.image(img_lines_pil, x=15, y=pdf.get_y(), w=180)
        pdf.ln(85)
    except Exception:
        pdf.ln(4)
            
    # Sección 4: Dictamen Inteligente
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "4. Dictamen Avanzado de la Inteligencia Artificial", ln=True)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*COLOR_TEXT)
    
    dictamen_ia = st.session_state.get("auditoria_estatica", "")
    if dictamen_ia:
        texto_limpio = dictamen_ia.replace("**", "").replace("###", "").replace("*", "-")
        pdf.multi_cell(0, 5, texto_limpio.encode('latin-1', 'ignore').decode('latin-1'))
    else:
        deuda_total_calc = du['capital_pendiente'] + total_pendiente_deudas_extra
        texto_defecto = (
            f"DIAGNÓSTICO AUTOMÁTICO: Balance con un Objetivo de Retiro fijado en {num_libertad:,.0f} EUR. "
            f"El patrimonio líquido total de {du['capital_inicial']:,} EUR se enfrenta a una deuda agregada de "
            f"{deuda_total_calc:,.0f} EUR. El simulador fiscal aplica una tasa de retención del {du['impuesto_renta_variable']}% "
            f"en renta variable. Se sugiere ejecutar el motor de auditoría inteligente en la aplicación "
            f"para volcar el informe detallado de cuatro bloques en este informe oficial."
        )
        pdf.multi_cell(0, 5, texto_defecto.encode('latin-1', 'ignore').decode('latin-1'))
        
    # Pie corporativo
    pdf.set_y(-15)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, "DOCUMENTO ALTAMENTE CONFIDENCIAL - GENERADO MEDIANTE TERMINAL INTEGRADO MOVANA PRO", align="C")
    
    return bytes(pdf.output())


# ==========================================
# 📊 CREACIÓN Y DEFINICIÓN DE PESTAÑAS
# ==========================================
tab_resumen, tab_presupuesto, tab_inversion, tab_hipoteca, tab_libertad, tab_ia = st.tabs([
    "👑 Cuadro de Mandos", "🥗 Presupuesto y Deudas", "📈 Rentabilidad e Inversión", 
    "🏠 Consultor Hipotecario", "🕊️ Horizonte Independencia", "🤖 Dictamen e IA Chat"
])

# ----- PESTAÑA 1: CUADRO DE MANDOS -----
with tab_resumen:
    st.subheader("👑 Cuadro de Mandos Patrimonial Avanzado", anchor=False)
    c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
    with c_kpi1:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>PATRIMONIO NETO REAL (NET WORTH)</p>", unsafe_allow_html=True)
            st.markdown(f"## {patrimonio_liquido_real_neto:,.2f} €")
            st.caption(f"Efectivo: {du['capital_inicial']:,} € | Activos Vinculados: {patrimonio_inversiones_total:,.2f} €")
    with c_kpi2:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>TASA DE AHORRO NETO</p>", unsafe_allow_html=True)
            tasa_ahorro = (du["ahorro_mensual_total"] / ingresos_totales) * 100
            st.markdown(f"## {tasa_ahorro:.1f}%")
            st.caption(f"Ahorro de {du['ahorro_mensual_total']} € sobre ingresos reales.")
    with c_kpi3:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>PASIVOS RECONOCIDOS</p>", unsafe_allow_html=True)
            st.markdown(f"## {deuda_consolidada:,.0f} €")
            st.caption(f"Hipoteca: {du['capital_pendiente']:,} € | Otras deudas: {total_pendiente_deudas_extra:,.0f} €")

    st.markdown("<br>", unsafe_allow_html=True)
    col_dash1, col_dash2 = st.columns([2, 3])
    with col_dash1:
        with st.container(border=True):
            st.plotly_chart(fig_pie, use_container_width=True)
    with col_dash2:
        with st.container(border=True):
            st.plotly_chart(fig_historico_linea, use_container_width=True)
            
    with st.container(border=True):
        st.markdown("#### 🎯 Meta Independencia Financiera")
        porcentaje_meta = (patrimonio_liquido_real_neto / num_libertad) * 100 if num_libertad > 0 else 0
        st.progress(min(max(porcentaje_meta / 100, 0.0), 1.0))
        st.info(f"Objetivo: **{num_libertad:,.0f} €** (Regla del 4%). Llevas completado el **{porcentaje_meta:.1f}%** de tu meta definitiva.")

# ----- PESTAÑA 2: PRESUPUESTO Y DEUDAS -----
with tab_presupuesto:
    st.subheader("🥗 Optimización y Control de Riesgos Patrimoniales", anchor=False)
    st.markdown("### 🛡️ Escudo de Contingencias (Fondo de Emergencia)")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.metric("Tus Gastos Mensuales Reales", f"{gastos_mensuales_totales:,.2f} €")
    with col_f2:
        st.metric("Meses de Cobertura de tu Liquidez", f"{meses_cobertura:.1f} meses")
    with col_f3:
        if meses_cobertura < 3: st.error("🚨 Alerta: Fondo Insuficiente.")
        elif 3 <= meses_cobertura <= 6: st.warning("⚠️ Rango Estándar: Ajustado.")
        else: st.success("✅ Rango Óptimo: Excelente.")

    st.markdown("---")
    st.markdown("### 💳 Matriz de Pasivos (Deudas Actuales y Próximas)")
    if st.button("➕ Añadir Nueva Deuda / Próximo Gasto"):
        du["deudas"].append({"nombre": "Nueva Deuda", "tipo": "Actual", "cuota_mensual": 100.0, "pendiente": 2000.0, "horizonte": "Inmediato"})
        guardar_automatico()
        st.rerun()
        
    for d_idx, deuda in enumerate(du.get("deudas", [])):
        with st.container(border=True):
            col_d1, col_d2, col_d3, col_d4, col_d5 = st.columns([2, 2, 2, 2, 1])
            with col_d1: deuda["nombre"] = st.text_input("Concepto / Deuda:", value=deuda["nombre"], key=f"d_name_{d_idx}", on_change=guardar_automatico)
            with col_d2: deuda["tipo"] = st.selectbox("Estado temporal:", ["Actual", "Próxima"], index=["Actual", "Próxima"].index(deuda["tipo"]), key=f"d_tipo_{d_idx}", on_change=guardar_automatico)
            with col_d3: deuda["cuota_mensual"] = st.number_input("Cuota al mes (€):", value=float(deuda["cuota_mensual"]), key=f"d_cuota_{d_idx}", on_change=guardar_automatico)
            with col_d4:
                if deuda["tipo"] == "Actual":
                    deuda["pendiente"] = st.number_input("Capital Pendiente (€):", value=float(deuda["pendiente"]), key=f"d_pend_{d_idx}", on_change=guardar_automatico)
                else:
                    deuda["horizonte"] = st.selectbox("Llegada estimada:", ["En 3 meses", "En 6 meses", "En 12 meses", "Más de 1 año"], index=["En 3 meses", "En 6 meses", "En 12 meses", "Más de 1 año"].index(deuda["horizonte"] if deuda["horizonte"] in ["En 3 meses", "En 6 meses", "En 12 meses", "Más de 1 año"] else "En 3 meses"), key=f"d_horiz_{d_idx}", on_change=guardar_automatico)
                    deuda["pendiente"] = st.number_input("Gasto estimado (€):", value=float(deuda["pendiente"]), key=f"d_pend_{d_idx}", on_change=guardar_automatico)
            with col_d5:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("❌", key=f"d_del_{d_idx}"):
                    du["deudas"].pop(d_idx)
                    guardar_automatico()
                    st.rerun()

# ----- PESTAÑA 3: RENTABILIDAD E INVERSION -----
with tab_inversion:
    st.subheader("💼 Matriz Patrimonial y Asignación de Activos", anchor=False)
    
    # Cambiamos a una clave única blindada para que no choque con nada viejo
    if st.button("➕ Vincular Nuevo Activo/Inversión", key="key_unico_boton_tab_inversion"):
        du["inversiones"].append({
            "nombre": f"Nuevo Activo {len(du['inversiones']) + 1}",
            "tipo": "Interés Compuesto (ETFs / Fondos)",
            "valor_actual": 0.0, 
            "aportacion_mensual": 0.0, 
            "interes_anual": 7.0,
            "precio_compra": 0.0, 
            "alquiler_mensual": 0.0, 
            "financiacion_inmueble": 0.0,
            "valor_final": 0.0
        })
        guardar_automatico()
        st.rerun()

    # Bucle para renderizar tus tarjetas
    for idx, inv in enumerate(du.get("inversiones", [])):
        with st.container(border=True):
            col_inv1, col_inv2, col_inv3, col_inv4 = st.columns([2, 3, 3, 1])
            with col_inv1:
                inv["nombre"] = st.text_input("Nombre del Activo:", value=inv["nombre"], key=f"inv_nom_{idx}", on_change=guardar_automatico)
            with col_inv2:
                inv["tipo"] = st.selectbox(
                    "Naturaleza del Activo:", 
                    ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Otros"], 
                    index=["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Otros"].index(inv["tipo"] if inv["tipo"] in ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Otros"] else "Interés Compuesto (ETFs / Fondos)"), 
                    key=f"inv_tipo_{idx}", 
                    on_change=st.rerun
                )
            with col_inv3:
                if inv["tipo"] == "Interés Compuesto (ETFs / Fondos)":
                    inv["valor_actual"] = st.number_input("Capital Actual (€):", value=float(inv.get("valor_actual", 0.0)), key=f"inv_val_{idx}", on_change=guardar_automatico)
                    inv["aportacion_mensual"] = st.number_input("Aportación Mensual (€):", value=float(inv.get("aportacion_mensual", 0.0)), key=f"inv_apo_{idx}", on_change=guardar_automatico)
                    inv["interes_anual"] = st.number_input("Interés Anual Estimado (%):", value=float(inv.get("interes_anual", 7.0)), key=f"inv_int_{idx}", on_change=guardar_automatico)
                elif inv["tipo"] == "Rentabilidad Inmobiliaria (Ladrillo)":
                    inv["precio_compra"] = st.number_input("Precio de Compra (€):", value=float(inv.get("precio_compra", 0.0)), key=f"inv_pre_{idx}", on_change=guardar_automatico)
                    inv["alquiler_mensual"] = st.number_input("Alquiler Mensual percibido (€):", value=float(inv.get("alquiler_mensual", 0.0)), key=f"inv_alq_{idx}", on_change=guardar_automatico)
                    inv["financiacion_inmueble"] = st.number_input("Hipoteca pendiente sobre este inmueble (€):", value=float(inv.get("financiacion_inmueble", 0.0)), key=f"inv_fin_{idx}", on_change=guardar_automatico)
                else:
                    inv["valor_final"] = st.number_input("Valor de Liquidación Estático (€):", value=float(inv.get("valor_final", 0.0)), key=f"inv_fin_est_{idx}", on_change=guardar_automatico)
            with col_inv4:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("❌", key=f"inv_del_{idx}"):
                    du["inversiones"].pop(idx)
                    guardar_automatico()
                    st.rerun()
# ----- PESTAÑA 4: CONSULTOR HIPOTECARIO -----
with tab_hipoteca:
    st.subheader("🏠 Consultor y Optimizador de Carga Hipotecaria", anchor=False)
    
    col_h1, col_h2 = st.columns([2, 3])
    with col_h1:
        with st.container(border=True):
            st.markdown("#### Datos de la Hipoteca Principal")
            du["tipo_hipoteca"] = st.selectbox("Tipo de Estructura:", ["Fija", "Variable"], index=["Fija", "Variable"].index(du["tipo_hipoteca"]), on_change=st.rerun)
            du["capital_original"] = st.number_input("Capital Concedido Original (€)", value=int(du["capital_original"]), step=5000, on_change=guardar_automatico)
            du["capital_pendiente"] = st.number_input("Capital Pendiente de Amortizar (€)", value=int(du["capital_pendiente"]), step=5000, on_change=guardar_automatico)
            du["interes_anual_actual"] = st.number_input("Tipo de Interés Nominal Anual (%)", value=float(du["interes_anual_actual"]), step=0.1, on_change=guardar_automatico)
            du["cuota_mensual_actual"] = st.number_input("Cuota Mensual Actual (€)", value=int(du["cuota_mensual_actual"]), step=50, on_change=guardar_automatico)
            du["seguros_anuales_banco"] = st.number_input("Seguros obligatorios vinculados (Al año €)", value=int(du["seguros_anuales_banco"]), step=50, on_change=guardar_automatico)

    with col_h2:
        with st.container(border=True):
            st.markdown("#### ⚖️ Métricas de Sostenibilidad Bancaria")
            c_m1, c_m2 = st.columns(2)
            with c_m1:
                st.metric("Cuota Mensual Indexada (Con Riesgos)", f"{cuota_hipotecaria_final:,.2f} €")
                st.metric("Carga en Seguros (Mes)", f"{coste_mensual_seguros:,.2f} €")
            with c_m2:
                st.metric("Años de Contrato Restantes", f"{anos_contrato_restantes:.1f} años")
                st.metric("Intereses Pendientes al Banco", f"{intereses_totales_banco:,.2f} €")

# ----- PESTAÑA 5: HORIZONTE INDEPENDENCIA -----
with tab_libertad:
    st.subheader("🕊️ Horizonte de Independencia y Retiro", anchor=False)
    
    with st.container(border=True):
        st.plotly_chart(fig_lineas, use_container_width=True)
        
    st.markdown("### 📥 Descarga de Documentación Oficial")
    st.write("Genera el informe consolidado con formato ejecutivo listo para su presentación en banca privada o análisis patrimonial.")
    
    pdf_bytes = generar_pdf_premium_bytes()
    st.download_button(
        label="📥 Descargar Dossier Patrimonial Premium (PDF)",
        data=pdf_bytes,
        file_name="Informe_Patrimonial_Premium.pdf",
        mime="application/pdf"
    )

# ----- PESTAÑA 6: DICTAMEN E IA CHAT -----
with tab_ia:
    st.subheader("🤖 Auditoría Financiera Mediante Inteligencia Artificial", anchor=False)
    
    if not st.session_state.api_key_guardada:
        st.error("Falta la clave GEMINI_API_KEY en las variables del sistema (secrets).")
    else:
        if st.button("📊 Ejecutar Auditoría Patrimonial Inteligente", type="primary"):
            with st.spinner("Analizando matrices de flujos, pasivos y plusvalías..."):
                try:
                    genai.configure(api_key=st.session_state.api_key_guardada)
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    
                    prompt_auditoria = f"""
                    Actúa como un experto auditor de Banca Privada. Analiza la siguiente situación financiera y redacta un dictamen profesional estructurado en 4 bloques: 1. Diagnóstico de Salud Financiera, 2. Análisis del Nivel de Endeudamiento, 3. Optimización Fiscal y Eficiencia, 4. Plan de Acción Recomendado.
                    
                    DATOS DE BALANCE DEL USUARIO:
                    - Ingresos Netos al Mes (con extras): {ingresos_totales:.2f} €
                    - Ahorro Líquido al Mes: {du['ahorro_mensual_total']} €
                    - Fondo de Maniobra Actual (Efectivo): {du['capital_inicial']} €
                    - Gastos de Operación Mensuales Totales: {gastos_mensuales_totales:.2f} €
                    - Capital Pendiente Hipoteca: {du['capital_pendiente']} €
                    - Otras deudas consolidadas: {total_pendiente_deudas_extra} €
                    - Patrimonio en Activos/Inversiones: {patrimonio_inversiones_total:.2f} €
                    - Meta Numérica de Retiro: {num_libertad:.2f} €
                    - Inflación y Estrés Macroeconómico Aplicado: {du['inflacion_anual']}%
                    """
                    
                    respuesta = model.generate_content(prompt_auditoria)
                    st.session_state.auditoria_estatica = respuesta.text
                    st.success("¡Dictamen generado con éxito! Ya se ha integrado también en tu informe PDF.")
                except Exception as e:
                    st.error(f"Error en la conexión con la IA: {e}")
                    
        if st.session_state.auditoria_estatica:
            with st.container(border=True):
                st.markdown(st.session_state.auditoria_estatica)
