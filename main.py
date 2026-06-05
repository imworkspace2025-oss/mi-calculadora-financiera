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

    # Frenamos la app aquí para que no enseñe nada si no ha iniciado sesión
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

st.session_state.api_key_guardada = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar.expander("🔑 Inteligencia Artificial (Gemini)", expanded=False):
    if st.session_state.api_key_guardada:
        st.success("✅ API Key vinculada y activa")
    else:
        st.error("❌ No se encontró la clave GEMINI_API_KEY en Secrets.")

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
# 🧮 MOTOR MATEMÁTICO GLOBAL Y GRÁFICOS
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

for item in du.get("inversiones", []):
    dict_distribucion_activos[item["nombre"]] = item["valor_actual"]

patrimonio_neto_global = du["capital_inicial"] + patrimonio_inversiones_total

tasa_mensual = (du["interes_anual_actual"] / 100) / 12
coste_mensual_seguros = du["seguros_anuales_banco"] / 12
cuota_financiera_verdadera = du["cuota_mensual_actual"] + coste_mensual_seguros

if du["cuota_mensual_actual"] > (du["capital_pendiente"] * tasa_mensual):
    meses_contrato = -math.log(1 - (du["capital_pendiente"] * tasa_mensual) / du["cuota_mensual_actual"]) / math.log(1 + tasa_mensual)
    anos_contrato_restantes = meses_contrato / 12
    intereses_totales_banco = (du["cuota_mensual_actual"] * meses_contrato) - du["capital_pendiente"]
else:
    anos_contrato_restantes, intereses_totales_banco = 0, 0

gastos_mensuales_totales = du["cuota_mensual_actual"] + total_cuotas_deudas_extra + gastos_mensuales_vivos
meses_cobertura = du["capital_inicial"] / gastos_mensuales_totales if gastos_mensuales_totales > 0 else 0

if meses_cobertura < 3:
    estado_seguridad = "Bajo Mínimos"
else:
    estado_seguridad = "Saludable / Estándar" if meses_cobertura <= 6 else "Excelente"

# --- GENERACIÓN GLOBAL DE GRÁFICOS (Para que los lea el PDF y las Tabs) ---
df_pie = pd.DataFrame({"Activo": list(dict_distribucion_activos.keys()), "Valor (€)": list(dict_distribucion_activos.values())})
fig_pie = px.pie(df_pie, values="Valor (€)", names="Activo", hole=0.4, title="Asset Allocation Actual")
fig_pie.update_layout(height=250, margin=dict(t=30, b=10, l=10, r=10))

fig_lineas = None
if len(du.get("inversiones", [])) > 0:
    df_prep_nom = pd.DataFrame(datos_grafica_nominal).set_index("Año")
    df_total_nom = pd.DataFrame({"Valor Nominal": df_prep_nom.sum(axis=1)})
    df_prep_real = pd.DataFrame(datos_grafica_real).set_index("Año")
    df_total_real = pd.DataFrame({"Valor Real Corregido": df_prep_real.sum(axis=1)})
    df_melted = df_total_nom.join(df_total_real).reset_index().melt(id_vars=["Año"], var_name="Métrica", value_name="Capital (€)")
    fig_lineas = px.line(df_melted, x="Año", y="Capital (€)", color="Métrica", title="Evolución del Patrimonio Bajo Inflación")


# ==========================================
# 📥 FUNCIÓN EXPORTACIÓN PDF
# ==========================================
def generar_pdf_premium_bytes():
    tasa_ahorro_aux = (du["ahorro_mensual_total"] / ingresos_totales) * 100 if ingresos_totales > 0 else 0

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    COLOR_PRIMARY = (26, 36, 43)    
    COLOR_SECONDARY = (70, 100, 120) 
    COLOR_TEXT = (50, 50, 50)       
    
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, "MOVANA PRO | REPORTING PATRIMONIAL", ln=True, align="C")
    
    pdf.set_text_color(*COLOR_SECONDARY)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, "Dossier Ejecutivo de Planificación Financiera", ln=True, align="C")
    pdf.ln(4)
    
    pdf.set_draw_color(*COLOR_SECONDARY)
    pdf.set_line_width(0.4)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)
    
    pdf.set_text_color(*COLOR_TEXT)
    pdf.set_font("Helvetica", "", 10)
    intro_txt = (
        f"Este informe técnico consolida métricas clave del perfil patrimonial del usuario. "
        f"Ha sido estructurado bajo estándares bancarios y de auditoría para facilitar la evaluación "
        f"de flujos de caja, distribución de activos y la resiliencia financiera a largo plazo."
    )
    pdf.multi_cell(0, 5, intro_txt)
    pdf.ln(4)
    
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Indicadores Base de Flujo de Caja", ln=True)
    
    datos_tabla = [
        ["Entidad Laboral Declarada:", f"{du['nombre_empresa']} (Antigüedad: {du['antiguedad_trabajo']} años)"],
        ["Ingresos Líquidos Mensuales:", f"{du['ingresos_mensuales']:,} EUR/mes"],
        ["Capacidad de Ahorro Neto:", f"{du['ahorro_mensual_total']:,} EUR/mes (Tasa: {tasa_ahorro_aux:.1f}%)"],
        ["Colchón de Contingencia Real:", f"{du['capital_inicial']:,} EUR ({meses_cobertura:.1f} meses de cobertura - {estado_seguridad})"]
    ]
    
    for fila in datos_tabla:
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(60, 6, fila[0], border="B")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(130, 6, fila[1], border="B", ln=True)
    pdf.ln(6)
    
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Distribución y Asignación de Activos (Asset Allocation)", ln=True)
    pdf.ln(2)
    
    try:
        from PIL import Image
        img_pie_bytes = fig_pie.to_image(format="png", width=650, height=300, scale=2)
        img_pie_pil = Image.open(io.BytesIO(img_pie_bytes))
        pdf.image(img_pie_pil, x=20, y=pdf.get_y(), w=170)
        pdf.ln(82)  
    except Exception as e:
        pdf.ln(4)

    pdf.add_page()
    
    if fig_lineas is not None:
        pdf.set_text_color(*COLOR_PRIMARY)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, f"3. Evolución del Capital Proyectado a {du['anos_proyeccion']} años vista", ln=True)
        pdf.ln(2)
        
        try:
            from PIL import Image
            img_lines_bytes = fig_lineas.to_image(format="png", width=650, height=300, scale=2)
            img_lines_pil = Image.open(io.BytesIO(img_lines_bytes))
            pdf.image(img_lines_pil, x=20, y=pdf.get_y(), w=170)
            pdf.ln(82)
        except Exception as e:
            pdf.ln(4)
            
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "4. Dictamen de Previsión Estratégica", ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*COLOR_TEXT)
    
    deuda_total_calc = du['capital_pendiente'] + total_pendiente_deudas_extra
    conclusion_txt = (
        f"Evaluación final del escenario patrimonial: Con un Objetivo de Independencia Financiera establecido en "
        f"{num_libertad:,.0f} EUR, el perfil actual presenta una tasa de ahorro del {tasa_ahorro_aux:.1f}%. "
        f"La carga total de pasivos reconocidos asciende a {deuda_total_calc:,.0f} EUR. El motor de simulación "
        f"recomienda optimizar el arbitraje de tipos de interés frente a la inflación estimada del "
        f"{du['inflacion_anual']}%, canalizando los excedentes mensuales de forma diversificada hacia los "
        f"vehículos indexados de inversión de manera eficiente y proactiva."
    )
    pdf.multi_cell(0, 5, conclusion_txt)
    
    pdf_out = pdf.output()
    if isinstance(pdf_out, str):
        return pdf_out.encode("latin-1")
    return bytes(pdf_out)


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
        st.metric("Tus Gastos Mensuales Reales", f"{gastos_mensuales_totales:,.2f} €")
    with col_f2:
        st.metric("Meses de Cobertura de tu Liquidez", f"{meses_cobertura:.1f} meses")
    with col_f3:
        if meses_cobertura < 3:
            st.error("🚨 Alerta: Fondo Insuficiente.")
        elif 3 <= meses_cobertura <= 6:
            st.warning("⚠️ Rango Estándar: Ajustado.")
        else:
            st.success("✅ Rango Óptimo: Excelente.")

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
            with col_c2: inv["tipo"] = st.selectbox("Naturaleza:", ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Otros"], index=["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Otros"].index(inv["tipo"] if inv["tipo"] in ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "Activos Estáticos / Others", "Activos Estáticos / Otros"] else "Activos Estáticos / Otros"), key=f"inv_tipo_{idx}", on_change=guardar_automatico)
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
                with c3: inv["interes_anual"] = st.number_input("Rendimiento Neto (%)", value=float(inv["interes_anual"]), key=f"f3_{idx}", on_change=guardar_automatico)

            elif inv["tipo"] == "Rentabilidad Inmobiliaria (Ladrillo)":
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1: inv["precio_compra"] = st.number_input("Precio compra (€)", value=float(inv["precio_compra"]), key=f"l1_{idx}", on_change=guardar_automatico)
                with c2: inv["gastos_iniciales"] = st.number_input("Gastos iniciales (€)", value=float(inv["gastos_iniciales"]), key=f"l2_{idx}", on_change=guardar_automatico)
                with c3: inv["alquiler_mensual"] = st.number_input("Renta al mes (€)", value=float(inv["alquiler_mensual"]), key=f"l3_{idx}", on_change=guardar_automatico)
                with c4: inv["gastos_mensuales_inv"] = st.number_input("Gastos fijos MES (€)", value=float(inv["gastos_mensuales_inv"]), key=f"l5_{idx}", on_change=guardar_automatico)
                with c5: inv["gastos_anuales"] = st.number_input("Gastos fijos AÑO (€)", value=float(inv["gastos_anuales"]), key=f"l4_{idx}", on_change=guardar_automatico)

            elif inv["tipo"] in ["Activos Estáticos / Otros", "Activos Estáticos / Others"]:
                c1, c2 = st.columns(2)
                with c1: inv["capital_invertido"] = st.number_input("Original invertido (€)", value=float(inv["capital_invertido"]), key=f"r1_{idx}", on_change=guardar_automatico)
                with c2: inv["valor_final"] = st.number_input("Valor mercado (€)", value=float(inv["valor_final"]), key=f"r2_{idx}", on_change=guardar_automatico)

    st.markdown("---")
    if fig_lineas is not None:
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
    with col8: du["inyeccion_capital_unica"] = st.number_input("Inyección puntual (€)", value=int(du["inyeccion_capital_unica"]), on_change=guardar_automatico)

    if anos_contrato_restantes > 0:
        st.info(f"📆 Tiempo restante estimado: **{anos_contrato_restantes:.1f} años** | Intereses pendientes al banco: **{intereses_totales_banco:,.2f} €**")

# ----- PESTAÑA 5: HORIZONTE INDEPENDENCIA -----
with tab_libertad:
    st.subheader("🕊️ Tu Meta de Libertad Financiera (Regla del 4%)", anchor=False)
    st.error(f"## 🎯 TU NÚMERO OBJETIVO: {num_libertad:,.2f} €")
    st.write("Capital total necesario invertido para retirar un 4% anual perpetuo que cubra tus costes sin depender de un trabajo.")

# ----- PESTAÑA 6: DICTAMEN E IA CHAT -----
with tab_ia:
    st.subheader("💬 Consultor de Estrategia Patrimonial", anchor=False)
    
    if st.session_state.get("api_key_guardada"):
        try:
            genai.configure(api_key=st.session_state.api_key_guardada)
            
            if "mensajes_chat" not in st.session_state:
                st.session_state.mensajes_chat = []
                
            for msg in st.session_state.mensajes_chat:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
            if prompt_usuario := st.chat_input("Plantea una consulta sobre optimización patrimonial..."):
                with st.chat_message("user"):
                    st.write(prompt_usuario)
                st.session_state.mensajes_chat.append({"role": "user", "content": prompt_usuario})
                
                contexto_patrimonial = (
                    f"Actúa como un auditor patrimonial privado de élite. Datos actuales:\n"
                    f"- Ingresos Netos: {ingresos_totales:.2f} EUR/mes\n"
                    f"- Capacidad de Ahorro: {du['ahorro_mensual_total']} EUR/mes\n"
                    f"- Colchón Liquidez: {du['capital_inicial']} EUR\n"
                    f"- Pasivos/Deudas Consolidadas: {deuda_consolidada:.2f} EUR\n"
                    f"Pregunta del inversor: {prompt_usuario}"
                )
                
                model = genai.GenerativeModel("gemini-1.5-flash")
                respuesta_ia = model.generate_content(contexto_patrimonial)
                
                with st.chat_message("assistant"):
                    st.write(respuesta_ia.text)
                st.session_state.mensajes_chat.append({"role": "assistant", "content": respuesta_ia.text})
                
        except Exception as e:
            st.warning(f"Esperando inicialización del modelo de IA: {e}")
    else:
        st.info("💡 Vincula la clave GEMINI_API_KEY en los Secrets para activar este consultor dinámico.")


# ==========================================
# 🚪 RENDERIZADO DEL BOTÓN PDF EN LA SIDEBAR (ABAJO)
# ==========================================
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📥 Exportación")
    try:
        pdf_bytes = generar_pdf_premium_bytes()
        st.download_button(
            label="🚀 Descargar Proyecto PDF",
            data=pdf_bytes,
            file_name="Auditoria_Patrimonial_Movana.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as err:
        st.error(f"Error preparando la descarga: {err}")
