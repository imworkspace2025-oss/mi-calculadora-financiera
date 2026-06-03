import streamlit as st
import google.generativeai as genai
import pandas as pd
import math
import json

# Configuración de página limpia y ancha
st.set_page_config(page_title="Cuadro de Mandos Financiero Pro", layout="wide")

# CSS para centrar las pestañas en la pantalla
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 TU DASHBOARD FINANCIERO INTEGRAL")
st.write("Gestiona tu patrimonio. Cualquier cambio que hagas se guarda automáticamente en la memoria de este PC.")

# ==========================================
# 💾 MOTOR DE MEMORIA AUTOMÁTICA (PERSISTENCIA RECOIL)
# ==========================================
VALORES_POR_DEFECTO = {
    "ingresos_mensuales": 2000,
    "dinero_extra_anual": 0,
    "ahorro_mensual_total": 500,
    "capital_inicial": 5000,
    "inversiones": [
        {
            "nombre": "Mi Primer Fondo Indexado",
            "tipo": "Interés Compuesto (ETFs / Fondos)",
            "valor_actual": 5000.0,
            "aportacion_mensual": 200.0,
            "interes_anual": 7.0,
            "precio_compra": 100000.0,
            "gastos_iniciales": 12000.0,
            "alquiler_mensual": 600.0,
            "gastos_anuales": 1000.0,
            "capital_invertido": 10000.0,
            "valor_final": 13500.0
        }
    ],
    "tipo_hipoteca": "Fija",
    "capital_original": 150000,
    "capital_pendiente": 120000,
    "interes_anual_actual": 3.5,
    "cuota_mensual_actual": 600,
    "seguros_anuales_banco": 400,
    "amortizacion_extra": 0,
    "inyeccion_capital_unica": 0
}

# Inicialización de la sesión interna
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

# Función mágica: Guarda en la URL silenciosamente cada vez que hay un cambio
def guardar_automatico():
    st.query_params["db"] = json.dumps(st.session_state.datos_usuario)

# ==========================================
# ⚙️ 2. BARRA LATERAL (DATOS GLOBALES E IA)
# ==========================================
st.sidebar.title("⚙️ Datos Globales")

with st.sidebar.expander("🔑 Configuración de IA", expanded=False):
    api_key_input = st.text_input("Introduce tu Gemini API Key:", type="password")

with st.sidebar.expander("📥 Tus datos económicos", expanded=True):
    du["ingresos_mensuales"] = st.number_input("Ingresos mensuales netos (€)", value=du["ingresos_mensuales"], step=100, on_change=guardar_automatico)
    du["dinero_extra_anual"] = st.number_input("Ingresos extras anuales (€)", value=du["dinero_extra_anual"], step=500, on_change=guardar_automatico)
    du["ahorro_mensual_total"] = st.number_input("Ahorro neto total al mes (€)", value=du["ahorro_mensual_total"], step=50, on_change=guardar_automatico)
    du["capital_inicial"] = st.number_input("Dinero líquido en cuenta (€)", value=du["capital_inicial"], step=500, on_change=guardar_automatico)

# Cálculos globales automáticos basados en la memoria
ingreso_mensual_extra_prorrateado = du["dinero_extra_anual"] / 12
ingresos_totales_calculados = du["ingresos_mensuales"] + ingreso_mensual_extra_prorrateado
gastos_mensuales_calculados = ingresos_totales_calculados - du["ahorro_mensual_total"]
gastos_anuales_estimados = gastos_mensuales_calculados * 12
num_libertad = gastos_anuales_estimados * 25

# ==========================================
# 🗂️ 3. PESTAÑAS PRINCIPALES
# ==========================================
tab_resumen, tab_presupuesto, tab_inversion, tab_hipoteca, tab_libertad, tab_ia = st.tabs([
    "📊 Vista General", "🥗 Presupuesto 50/30/20", "📈 Rendimiento de Inversiones", 
    "🏠 Escáner Hipoteca", "🕊️ Libertad Financiera", "🤖 Consultor IA"
])

# ==========================================
# 📥 4. PESTAÑA: RENDIMIENTO DE INVERSIONES
# ==========================================
with tab_inversion:
    st.subheader("💼 Tus Activos Actuales e Inversiones")

    if st.button("➕ Añadir Nueva Inversión"):
        du["inversiones"].append({
            "nombre": f"Inversión Nueva {len(du['inversiones']) + 1}",
            "tipo": "Interés Compuesto (ETFs / Fondos)",
            "valor_actual": 0.0, "aportacion_mensual": 0.0, "interes_anual": 7.0,
            "precio_compra": 100000.0, "gastos_iniciales": 12000.0, "alquiler_mensual": 600.0, "gastos_anuales": 1000.0,
            "capital_invertido": 10000.0, "valor_final": 13500.0
        })
        guardar_automatico()
        st.rerun()

    patrimonio_inversiones_total = 0.0
    cronologia_anos = list(range(1, 16))
    datos_grafica_global = {"Año": cronologia_anos}
    dict_graficas_individuales = {}

    for idx, inv in enumerate(du["inversiones"]):
        with st.container(border=True):
            col_cab1, col_cab2, col_cab3 = st.columns([2, 2, 1])
            with col_cab1:
                inv["nombre"] = st.text_input("Nombre identificativo:", value=inv["nombre"], key=f"inv_name_{idx}", on_change=guardar_automatico)
            with col_cab2:
                inv["tipo"] = st.selectbox(
                    "Tipo de activo / Filtro:", 
                    ["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "ROI Simple"],
                    index=["Interés Compuesto (ETFs / Fondos)", "Rentabilidad Inmobiliaria (Ladrillo)", "ROI Simple"].index(inv["tipo"]),
                    key=f"inv_tipo_{idx}",
                    on_change=guardar_automatico
                )
            with col_cab3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("❌ Eliminar", key=f"inv_del_{idx}"):
                    du["inversiones"].pop(idx)
                    guardar_automatico()
                    st.rerun()

            proyeccion_activo_lista = []
            
            if inv["tipo"] == "Interés Compuesto (ETFs / Fondos)":
                c_f1, c_f2, c_f3 = st.columns(3)
                with c_f1: inv["valor_actual"] = st.number_input("Capital inicial (€)", value=float(inv["valor_actual"]), key=f"f1_{idx}", step=500.0, on_change=guardar_automatico)
                with c_f2: inv["aportacion_mensual"] = st.number_input("Aportación mensual (€)", value=float(inv["aportacion_mensual"]), key=f"f2_{idx}", step=50.0, on_change=guardar_automatico)
                with c_f3: inv["interes_anual"] = st.number_input("Rentabilidad anual (%)", value=float(inv["interes_anual"]), key=f"f3_{idx}", step=0.5, on_change=guardar_automatico)
                
                patrimonio_inversiones_total += inv["valor_actual"]
                acumulado = inv["valor_actual"]
                for ano in cronologia_anos:
                    acumulado = (acumulado + (inv["aportacion_mensual"] * 12)) * (1 + (inv["interes_anual"] / 100))
                    proyeccion_activo_lista.append(acumulado)

            elif inv["tipo"] == "Rentabilidad Inmobiliaria (Ladrillo)":
                c_l1, c_l2, c_l3, c_l4 = st.columns(4)
                with c_l1: inv["precio_compra"] = st.number_input("Precio compra (€)", value=float(inv["precio_compra"]), key=f"l1_{idx}", step=5000.0, on_change=guardar_automatico)
                with c_l2: inv["gastos_iniciales"] = st.number_input("Gastos/Reformas (€)", value=float(inv["gastos_iniciales"]), key=f"l2_{idx}", step=1000.0, on_change=guardar_automatico)
                with c_l3: inv["alquiler_mensual"] = st.number_input("Alquiler mensual (€)", value=float(inv["alquiler_mensual"]), key=f"l3_{idx}", step=50.0, on_change=guardar_automatico)
                with c_l4: inv["gastos_anuales"] = st.number_input("Gastos anuales (€)", value=float(inv["gastos_anuales"]), key=f"l4_{idx}", step=100.0, on_change=guardar_automatico)
                
                inv["valor_actual"] = inv["precio_compra"] + inv["gastos_iniciales"]
                patrimonio_inversiones_total += inv["valor_actual"]
                flujo_anual_neto = (inv["alquiler_mensual"] * 12) - inv["gastos_anuales"]
                acumulado = inv["valor_actual"]
                for ano in cronologia_anos:
                    acumulado += flujo_anual_neto
                    proyeccion_activo_lista.append(acumulado)

            elif inv["tipo"] == "ROI Simple":
                c_r1, c_r2 = st.columns(2)
                with c_r1: inv["capital_invertido"] = st.number_input("Dinero invertido (€)", value=float(inv["capital_invertido"]), key=f"r1_{idx}", step=500.0, on_change=guardar_automatico)
                with c_r2: inv["valor_final"] = st.number_input("Valor de mercado (€)", value=float(inv["valor_final"]), key=f"r2_{idx}", step=500.0, on_change=guardar_automatico)
                
                inv["valor_actual"] = inv["valor_final"]
                patrimonio_inversiones_total += inv["valor_actual"]
                for ano in cronologia_anos:
                    proyeccion_activo_lista.append(inv["valor_actual"])

            datos_grafica_global[inv["nombre"]] = proyeccion_activo_lista
            dict_graficas_individuales[inv["nombre"]] = proyeccion_activo_lista

    patrimonio_neto_total = du["capital_inicial"] + patrimonio_inversiones_total

# ==========================================
# 🏠 5. PESTAÑA: ESCÁNER HIPOTECA
# ==========================================
with tab_hipoteca:
    st.subheader("🏠 Configuración y Escáner de tu Hipoteca")
    
    col_h1, col_h2, col_h3, col_h4 = st.columns(4)
    with col_h1: du["tipo_hipoteca"] = st.selectbox("Tipo de Hipoteca", ["Fija", "Variable", "Mixta"], index=["Fija", "Variable", "Mixta"].index(du["tipo_hipoteca"]), on_change=guardar_automatico)
    with col_h2: du["capital_original"] = st.number_input("Préstamo original (€)", value=int(du["capital_original"]), step=5000, on_change=guardar_automatico)
    with col_h3: du["capital_pendiente"] = st.number_input("Capital pendiente actual (€)", value=int(du["capital_pendiente"]), step=5000, on_change=guardar_automatico)
    with col_h4: du["interes_anual_actual"] = st.number_input("Interés anual (%)", value=float(du["interes_anual_actual"]), step=0.1, on_change=guardar_automatico)
    
    col_h5, col_h6, col_h7, col_h8 = st.columns(4)
    with col_h5: du["cuota_mensual_actual"] = st.number_input("Cuota mensual recibo (€)", value=int(du["cuota_mensual_actual"]), step=50, on_change=guardar_automatico)
    with col_h6: du["seguros_anuales_banco"] = st.number_input("Seguros anuales (€)", value=int(du["seguros_anuales_banco"]), step=50, on_change=guardar_automatico)
    with col_h7: du["amortizacion_extra"] = st.number_input("Amortización mensual extra (€)", value=int(du["amortizacion_extra"]), step=50, on_change=guardar_automatico)
    with col_h8: du["inyeccion_capital_unica"] = st.number_input("Inyección puntual única (€)", value=int(du["inyeccion_capital_unica"]), step=1000, on_change=guardar_automatico)

    # Matemáticas de la hipoteca
    tasa_m = (du["interes_anual_actual"] / 100) / 12
    coste_mensual_seguros = du["seguros_anuales_banco"] / 12
    cuota_real_total = du["cuota_mensual_actual"] + coste_mensual_seguros

    if du["cuota_mensual_actual"] > (du["capital_pendiente"] * tasa_m):
        interes_este_mes = du["capital_pendiente"] * tasa_m
        capital_este_mes = du["cuota_mensual_actual"] - interes_este_mes
        meses_restantes_normal = -math.log(1 - (du["capital_pendiente"] * tasa_m) / du["cuota_mensual_actual"]) / math.log(1 + tasa_m)
        anos_normal = meses_restantes_normal / 12
        intereses_totales_normal = (du["cuota_mensual_actual"] * meses_restantes_normal) - du["capital_pendiente"]
    else:
        interes_este_mes, capital_este_mes, anos_normal, intereses_totales_normal = 0, 0, 0, 0

# ==========================================
# 📊 6. RENDERIZADO GLOBAL DE RESULTADOS
# ==========================================

# --- Vista General ---
with tab_resumen:
    st.subheader("🏁 Resumen Ejecutivo de tu Salud Financiera")
    c_v1, c_v2 = st.columns(2)
    with c_v1:
        with st.container(border=True):
            st.markdown("#### 1. Presupuesto Inteligente (50/30/20)")
            tasa_ahorro = (du["ahorro_mensual_total"] / ingresos_totales_calculados) * 100
            st.metric("Tu Tasa de Ahorro Real", f"{tasa_ahorro:.1f}%", f"{du['ahorro_mensual_total']} €/mes guardados")
        with st.container(border=True):
            st.markdown("#### 2. Tu Patrimonio e Inversión Colectiva")
            st.metric("Patrimonio Neto Calculado", f"{patrimonio_neto_total:,.2f} €", f"Total en activos: {patrimonio_inversiones_total:,.2f} €")
    with c_v2:
        with st.container(border=True):
            st.markdown("#### 3. Estado de tu Hipoteca")
            st.metric("Cuota Real Mensual", f"{cuota_real_total:,.2f} €", f"Recibo + {coste_mensual_seguros:.1f} €/mes de seguros", delta_color="inverse")
            st.metric("Tiempo restante", f"{anos_normal:.1f} años", f"{intereses_totales_normal:,.2f} € pendientes", delta_color="inverse")
        with st.container(border=True):
            st.markdown("#### 4. Tu Libertad Financiera")
            st.metric("Meta de Capital (Regla del 4%)", f"{num_libertad:,.0f} €")
            porcentaje_meta = (patrimonio_neto_total / num_libertad) * 100 if num_libertad > 0 else 0
            st.progress(min(porcentaje_meta / 100, 1.0))

# --- Gráficas de Presupuesto ---
with tab_presupuesto:
    st.markdown("### 📊 Gráficas y Distribución del Presupuesto")
    nec, cap, aho = ingresos_totales_calculados * 0.5, ingresos_totales_calculados * 0.3, ingresos_totales_calculados * 0.2
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.info(f"• **🏠 Necesidades (50%):** {nec:,.2f} €/mes\n\n• **🎉 Caprichos (30%):** {cap:,.2f} €/mes\n\n• **🐷 Ahorro Rec. (20%):** {aho:,.2f} €/mes")
    with col_p2:
        df_p = pd.DataFrame({"Importe (€)": [nec, cap, aho, du["ahorro_mensual_total"]]}, index=["Necesidades", "Caprichos", "Ahorro Rec.", "Tu Ahorro Real"])
        st.bar_chart(df_p)

# --- Gráficas de Inversiones ---
with tab_inversion:
    if len(du["inversiones"]) > 0:
        col_g_ind, col_g_glob = st.columns(2)
        with col_g_ind:
            st.markdown("#### 📈 Evolución Individual")
            st.line_chart(pd.DataFrame(dict_graficas_individuales, index=cronologia_anos))
        with col_g_glob:
            st.markdown("#### 🌍 Cartera Total (Acumulado)")
            df_glob_prep = pd.DataFrame(datos_grafica_global).set_index("Año")
            st.area_chart(pd.DataFrame({"Patrimonio Invertido Total (€)": df_glob_prep.sum(axis=1)}, index=cronologia_anos))

# --- Gráficas de Hipoteca ---
with tab_hipoteca:
    if anos_normal > 0:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.bar_chart(pd.DataFrame({"Euros (€)": [capital_este_mes, interes_este_mes, coste_mensual_seguros]}, index=["Capital", "Intereses", "Seguros"]))
        with col_g2:
            st.info(f"• **Años contrato:** {anos_normal:.1f}\n\n• **Intereses pendientes:** {intereses_totales_normal:,.2f} €")
            
        capital_pendiente_neto = du["capital_pendiente"] - du["inyeccion_capital_unica"]
        if du["amortizacion_extra"] > 0 or du["inyeccion_capital_unica"] > 0:
            cuota_con_extra = du["cuota_mensual_actual"] + du["amortizacion_extra"]
            if cuota_con_extra > (capital_pendiente_neto * tasa_m):
                meses_restantes_extra = -math.log(1 - (capital_pendiente_neto * tasa_m) / cuota_con_extra) / math.log(1 + tasa_m)
                anos_extra = meses_restantes_extra / 12
                intereses_totales_extra = (du["inyeccion_capital_unica"] + (cuota_con_extra * meses_restantes_extra)) - du["capital_pendiente"]
                st.success(f"🔥 ¡Acelerador activo! Te ahorras {(anos_normal - anos_extra):.1f} años y {(intereses_totales_normal - intereses_totales_extra):,.2f} € en intereses.")

# --- Libertad Financiera ---
with tab_libertad:
    st.error(f"## 🎯 TU NÚMERO OBJETIVO: {num_libertad:,.2f} €")

# --- Consultor IA ---
with tab_ia:
    if not api_key_input:
        st.warning("🔒 Introduce tu Gemini API Key en la barra lateral.")
    else:
        if st.button("🚀 Solicitar Dictamen Financiero"):
            genai.configure(api_key=api_key_input)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"Analiza de forma ultra-resumida: Ingresos {ingresos_totales_calculados}, Ahorro {du['ahorro_mensual_total']}, Patrimonio {patrimonio_neto_total}.")
            st.markdown(response.text)

# Indicador visual discreto en el lateral
st.sidebar.markdown("---")
st.sidebar.caption("✅ Autofijado activo. Tus datos se salvan solos con cada click.")
