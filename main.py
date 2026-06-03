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
    "inyeccion_capital_unica": 0,
    "antiguedad_trabajo": 3,
    "antiguedad_empresa": 5,
    "es_autonomo_empresa": False,
    "facturacion_anual": 45000
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

# Blindaje anti-keyerror
for clave, valor in VALORES_POR_DEFECTO.items():
    if clave not in st.session_state.datos_usuario:
        st.session_state.datos_usuario[clave] = valor

du = st.session_state.datos_usuario

for item in du.get("inversiones", []):
    if item.get("tipo") == "ROI Simple":
        item["tipo"] = "Activos Estáticos / Otros"

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
    du["capital_inicial"] = st.number_input("Efectivo / Fondo Emergencia (€)", value=int(du["capital_inicial"]), step=500, on_change=guardar_automatico)

with st.sidebar.expander("💳 Perfil Crediticio y Laboral", expanded=True):
    du["antiguedad_trabajo"] = st.number_input("Tu antigüedad en el empleo actual (Años)", min_value=0, max_value=50, value=int(du["antiguedad_trabajo"]), on_change=guardar_automatico)
    du["antiguedad_empresa"] = st.number_input("Antigüedad de la empresa/pagadora (Años)", min_value=0, max_value=200, value=int(du["antiguedad_empresa"]), on_change=guardar_automatico)
    
    du["es_autonomo_empresa"] = st.toggle("💼 ¿Eres Autónomo o Empresa?", value=bool(du["es_autonomo_empresa"]), on_change=guardar_automatico)
    if du["es_autonomo_empresa"]:
        du["facturacion_anual"] = st.number_input("Facturación bruta anual (€)", value=int(du["facturacion_anual"]), step=5000, on_change=guardar_automatico)

with st.sidebar.expander("🛡️ Simulador de Entorno Económico", expanded=False):
    du["inflacion_anual"] = st.number_input("Inflación anual estimada (%)", value=float(du["inflacion_anual"]), step=0.1, on_change=guardar_automatico)
    du["anos_proyeccion"] = st.slider("Años a proyectar en el futuro", min_value=5, max_value=40, value=int(du["anos_proyeccion"]), step=1, on_change=guardar_automatico)
    du["activar_crisis"] = st.toggle("💥 Activar 'Test de Estrés'", value=bool(du["activar_crisis"]), on_change=guardar_automatico)

# Cálculos transversales
ingreso_extra_prorrateado = du["dinero_extra_anual"] / 12
ingresos_totales = du["ingresos_mensuales"] + ingreso_extra_prorrateado
gastos_mensuales = ingresos_totales - du["ahorro_mensual_total"]
gastos_anuales_proyectados = gastos_mensuales * 12
num_libertad = gastos_anuales_proyectados * 25

# Pestañas principales
tab_resumen, tab_presupuesto, tab_inversion, tab_hipoteca, tab_libertad, tab_ia = st.tabs([
    "👑 Cuadro de Mandos", "🥗 Presupuesto Interactivo", "📈 Rentabilidad e Inflación", 
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
            "precio_compra": 100000.0, "gastos_iniciales": 10000.0, "alquiler_mensual": 500.0, "gastos_anuales": 1000.0,
            "capital_invertido": 5000.0, "valor_final": 5000.0
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
                c1, c2, c3, c4 = st.columns(4)
                with c1: inv["precio_compra"] = st.number_input("Precio compra (€)", value=float(inv["precio_compra"]), key=f"l1_{idx}", on_change=guardar_automatico)
                with c2: inv["gastos_iniciales"] = st.number_input("Gastos e Impuestos (€)", value=float(inv["gastos_iniciales"]), key=f"l2_{idx}", on_change=guardar_automatico)
                with c3: inv["alquiler_mensual"] = st.number_input("Renta mensual líquida (€)", value=float(inv["alquiler_mensual"]), key=f"l3_{idx}", on_change=guardar_automatico)
                with c4: inv["gastos_anuales"] = st.number_input("Gastos explotación/año (€)", value=float(inv["gastos_anuales"]), key=f"l4_{idx}", on_change=guardar_automatico)

                inv["valor_actual"] = inv["precio_compra"] + inv["gastos_iniciales"]
                patrimonio_inversiones_total += inv["valor_actual"]
                flujo_neto = (inv["alquiler_mensual"] * 12) - inv["gastos_anuales"]
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
    st.subheader("🏠 Análisis Técnico y Estratégico de Deuda Bancaria", anchor=False)
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

    tasa_mensual = (du["interes_anual_actual"] / 100) / 12
    coste_mensual_seguros = du["seguros_anuales_banco"] / 12
    cuota_financiera_verdadera = du["cuota_mensual_actual"] + coste_mensual_seguros

    if du["cuota_mensual_actual"] > (du["capital_pendiente"] * tasa_mensual):
        interes_mes_actual = du["capital_pendiente"] * tasa_mensual
        meses_contrato = -math.log(1 - (du["capital_pendiente"] * tasa_mensual) / du["cuota_mensual_actual"]) / math.log(1 + tasa_mensual)
        anos_contrato_restantes = meses_contrato / 12
        intereses_totales_banco = (du["cuota_mensual_actual"] * meses_contrato) - du["capital_pendiente"]
    else:
        anos_contrato_restantes, intereses_totales_banco = 0, 0

# ==========================================
# 📊 VISUALIZACIÓN DE MÉTRICAS (PESTAÑA 1)
# ==========================================
with tab_resumen:
    st.subheader("👑 Cuadro de Mandos Patrimonial", anchor=False)
    c_kpi1, c_kpi2, c_kpi3 = st.columns(3)
    with c_kpi1:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>PATRIMONIO NETO ACTUAL</p>", unsafe_allow_html=True)
            st.markdown(f"## {patrimonio_neto_global:,.2f} €")
            st.caption(f"Líquido: {du['capital_inicial']:,} € | Activos: {patrimonio_inversiones_total:,.2f} €")
    with c_kpi2:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>TASA DE AHORRO MENSUAL</p>", unsafe_allow_html=True)
            tasa_ahorro = (du["ahorro_mensual_total"] / ingresos_totales) * 100
            st.markdown(f"## {tasa_ahorro:.1f}%")
            st.caption(f"Ahorras {du['ahorro_mensual_total']} € de {ingresos_totales:,.0f} € netos.")
    with c_kpi3:
        with st.container(border=True):
            st.markdown("<p style='color:#777; margin:0;'>SALUD DE LA HIPOTECA</p>", unsafe_allow_html=True)
            st.markdown(f"## {anos_contrato_restantes:.1f} años")
            st.caption(f"Pendiente: {du['capital_pendiente']:,} €")

    st.markdown("<br>", unsafe_allow_html=True)
    col_dash1, col_dash2 = st.columns([2, 3])
    with col_dash1:
        with st.container(border=True):
            df_pie = pd.DataFrame({"Activo": list(dict_distribucion_activos.keys()), "Valor (€)": list(dict_distribucion_activos.values())})
            fig_pie = px.pie(df_pie, values="Valor (€)", names="Activo", hole=0.4, title="Asset Allocation")
            fig_pie.update_layout(height=250, margin=dict(t=30, b=10, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)
    with col_dash2:
        with st.container(border=True):
            st.markdown("#### 🎯 Meta Independencia Financiera")
            porcentaje_meta = (patrimonio_neto_global / num_libertad) * 100 if num_libertad > 0 else 0
            st.progress(min(porcentaje_meta / 100, 1.0))
            st.info(f"Objetivo: **{num_libertad:,.0f} €** (Regla del 4% sobre gastos). Llevas el **{porcentaje_meta:.1f}%**.")

# ==========================================
# 🥗 PESTAÑA 2 Y 3 (PRESUPUESTO Y GRÁFICAS)
# ==========================================
with tab_presupuesto:
    st.subheader("🥗 Optimización Presupuestaria (Regla 50/30/20)", anchor=False)
    nec, cap, aho_rec = ingresos_totales * 0.5, ingresos_totales * 0.3, ingresos_totales * 0.2
    st.write(f"Necesidades básicas: {nec:,.0f} EUR/mes | Caprichos: {cap:,.0f} EUR/mes | Ahorro Objetivo: {aho_rec:,.0f} EUR/mes")

with tab_inversion:
    st.markdown("---")
    if len(du.get("inversiones", [])) > 0:
        df_prep_nom = pd.DataFrame(datos_grafica_nominal).set_index("Año")
        df_total_nom = pd.DataFrame({"Valor Nominal": df_prep_nom.sum(axis=1)})
        df_prep_real = pd.DataFrame(datos_grafica_real).set_index("Año")
        df_total_real = pd.DataFrame({"Valor Real Corregido": df_prep_real.sum(axis=1)})
        df_melted = df_total_nom.join(df_total_real).reset_index().melt(id_vars=["Año"], var_name="Métrica", value_name="Capital (€)")
        fig_lineas = px.line(df_melted, x="Año", y="Capital (€)", color="Métrica", title="Evolución del Patrimonio")
        st.plotly_chart(fig_lineas, use_container_width=True)

with tab_hipoteca:
    st.markdown("---")
    st.write("Análisis de rentabilidad de arbitraje activo entre coste de deuda e inversiones.")

with tab_libertad:
    st.subheader("🕊️ Tu Meta de Libertad Financiera (Regla del 4%)", anchor=False)
    st.error(f"## 🎯 TU NÚMERO OBJETIVO: {num_libertad:,.2f} €")

# ==========================================
# 🤖 PESTAÑA 6: AUDITORÍA + IA CHAT (ESTILO CONSOLA NATIVA)
# ==========================================
with tab_ia:
    st.subheader("🤖 Dictamen e Informe Estratégico de IA", anchor=False)
    
    if not st.session_state.get("api_key_guardada"):
        st.warning("🔒 Introduce tu Gemini API Key en la barra lateral para desbloquear la IA.")
    else:
        # Inyección automática de todo el escenario financiero actualizado
        resumen_activos = ""
        for i in du.get("inversiones", []):
            resumen_activos += f"- {i['nombre']} ({i['tipo']}): Valor: {i['valor_actual']} EUR. Rentabilidad: {i.get('interes_anual', 0)}%\n"

        perfil_laboral_txt = f"Asalariado (Antigüedad: {du['antiguedad_trabajo']} años, Antigüedad empresa: {du['antiguedad_empresa']} años)"
        if du["es_autonomo_empresa"]:
            perfil_laboral_txt = f"Autónomo/Empresa (Facturación: {du['facturacion_anual']} EUR, Negocio: {du['antiguedad_empresa']} años)"

        contexto_sistema = f"""
        Eres el mejor agente del mundo en asesoria financiera y gestion de patrimonio. Tu mision es orientar al usuario de forma analitica, logica y tactica basandote en su perfil financiero:
        - Flujos: Ingresos Netos {du['ingresos_mensuales']} EUR/mes, Ahorro {du['ahorro_mensual_total']} EUR/mes (Tasa: {tasa_ahorro:.1f}%), Pagas Extra Anuales: {du['dinero_extra_anual']} EUR.
        - Liquidez: {du['capital_inicial']} EUR en Efectivo.
        - Activos actuales:\n{resumen_activos}
        - Deuda Hipotecaria: Debe {du['capital_pendiente']} EUR (Original: {du['capital_original']} EUR) al {du['interes_anual_actual']}% (Cuota: {du['cuota_mensual_actual']} EUR/mes).
        - Perfil Crediticio/Laboral: {perfil_laboral_txt}.
        - Meta: {num_libertad:.0f} EUR.
        
        REGLAS DE CONVERSACIÓN:
        1. Propon distribuciones porcentuales concretas y logicas utilizando instrumentos reales y vigentes (ETFs globales como MSCI World, S&P 500, cuentas de alta remuneracion tipo Trade Republic, Revolut o neobancos).
        2. Diseña estrategias explicitas para las pagas extras/bonus anuales que menciona el usuario.
        3. Evalua su perfil laboral ante solicitudes de refinanciaciones o prestamos con garantia hipotecaria.
        4. Escribe siempre en Markdown profesional sin usar emojis ni simbolos de euro (usa la palabra 'EUR') para evitar roturas del codec 'latin-1' en la nube.
        """

        # ----------------------------------------------------
        # BLOQUE 1 (ARRIBA): Botón y despliegue de Auditoría Estática
        # ----------------------------------------------------
        col_btn, col_reset = st.columns([3, 1])
        with col_btn:
            if st.button("🚀 Generar Auditoría Patrimonial Completa", use_container_width=True):
                prompt_auditoria = f"""
                {contexto_sistema}
                Redacta un dictamen financiero macroeconomico inicial estructurado en 3 secciones claras:
                1. Evaluacion del Asset Allocation actual frente a la inflacion.
                2. Critica del coste de hipoteca vs rendimiento de inversiones.
                3. Una recomendacion tactica audaz para llegar a la meta de {num_libertad:.0f} EUR de forma acelerada.
                """
                prompt_seguro = prompt_auditoria.replace("€", "EUR")
                prompt_seguro = "".join([c for c in prompt_seguro if ord(c) < 256])

                try:
                    genai.configure(api_key=st.session_state.api_key_guardada, transport='rest')
                    model = genai.GenerativeModel('gemini-2.5-flash')
                    with st.spinner("La IA está auditando todo tu patrimonio consolidado..."):
                        response = model.generate_content(prompt_seguro)
                        st.session_state.auditoria_estatica = response.text
                except Exception as e:
                    st.error(f"Error al generar auditoría: {e}")
        
        with col_reset:
            if st.button("🗑️ Limpiar Conversación", use_container_width=True):
                st.session_state.historial_chat = []
                st.session_state.auditoria_estatica = ""
                st.rerun()

        # Si ya existe la auditoría generada, se dibuja fija arriba
        if st.session_state.auditoria_estatica:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown("### 📋 Dictamen Financiero Estratégico Inicial")
                st.markdown(st.session_state.auditoria_estatica)

        # ----------------------------------------------------
        # BLOQUE 2 (ABAJO): Chat conversacional continuo sobre la auditoría
        # ----------------------------------------------------
        st.markdown("---")
        st.markdown("#### 💬 Copiloto de Consultas Tácticas en Tiempo Real")
        st.caption("Pregúntale lo que quieras sobre el dictamen anterior, alternativas de neobancos, fondos o refinanciación.")

        # Imprimir los mensajes cruzados del historial del chat
        for msg in st.session_state.historial_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Caja de entrada de mensajes fija al fondo de la pantalla
        if usuario_input := st.chat_input("Pregúntale a tu Asesor Patrimonial... (Ej: ¿Qué harías exactamente con mis pagas extras en verano?)"):
            # Mostrar la duda del usuario de inmediato en pantalla
            with st.chat_message("user"):
                st.markdown(usuario_input)
            st.session_state.historial_chat.append({"role": "user", "content": usuario_input})

            # Montar todo el árbol conversacional (Contexto global + Auditoría de base + Historial acumulado)
            historial_formateado = f"Auditoria Patrimonial Base:\n{st.session_state.auditoria_estatica}\n\n"
            for m in st.session_state.historial_chat:
                role_label = "Usuario" if m["role"] == "user" else "Asesor"
                historial_formateado += f"\n{role_label}: {m['content']}\n"

            prompt_completo = f"{contexto_sistema}\n\nHistorial de la reunion:\n{historial_formateado}\nAsesor:"
            
            # Limpieza contra fallos de latin-1
            prompt_seguro = prompt_completo.replace("€", "EUR")
            prompt_seguro = "".join([c for c in prompt_seguro if ord(c) < 256])

            try:
                genai.configure(api_key=st.session_state.api_key_guardada, transport='rest')
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                with st.spinner("Analizando tu perfil financiero..."):
                    response = model.generate_content(prompt_seguro)
                    respuesta_ia = response.text
                
                st.session_state.historial_chat.append({"role": "assistant", "content": respuesta_ia})
                st.rerun()

            except Exception as e:
                st.error(f"Error en la respuesta del asesor: {e}")

# Indicador visual de estado de persistencia
st.sidebar.markdown("---")
st.sidebar.caption("✅ Autofijado activo. Tus datos se salvan solos con cada click.")
