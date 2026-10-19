import sys
from pathlib import Path
import pandas as pd
import streamlit as st

RUTA_RAIZ = Path(__file__).resolve().parent
if str(RUTA_RAIZ) not in sys.path:
    sys.path.insert(0, str(RUTA_RAIZ))

from modules import (
    cargar_datos_base,
    procesar_archivo_subido,
    generar_plantilla_excel,
    agregar_partida_manual,
    calcular_resumen_semanal,
    calcular_resumen_especialidad,
    calcular_resumen_encargados,
    calcular_kpis_generales,
    generar_grafico_curva_s,
    generar_grafico_produccion_semanal,
    generar_grafico_especialidades,
    generar_grafico_encargados,
    exportar_a_excel
)

st.set_page_config(
    page_title="Control de Avance Físico de Obra | Curva S",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .badge-adelantada {
        background-color: #065f46;
        color: #6ee7b7;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
    }
    .badge-atrasada {
        background-color: #991b1b;
        color: #fca5a5;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
    }
    .badge-previsto {
        background-color: #1e40af;
        color: #93c5fd;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
    }
    .section-header {
        font-size: 1.35rem;
        font-weight: 600;
        color: #e2e8f0;
        border-left: 4px solid #00a896;
        padding-left: 10px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

if "df_obra" not in st.session_state:
    st.session_state.df_obra = cargar_datos_base()

if "tolerancia_desviacion" not in st.session_state:
    st.session_state.tolerancia_desviacion = 0.5

if "nombre_proyecto" not in st.session_state:
    st.session_state.nombre_proyecto = "Edificio Habitacional de Chile"

ruta_infografia = RUTA_RAIZ / "assets" / "infografia_proyecto.png"
if not ruta_infografia.exists():
    ruta_infografia = RUTA_RAIZ / "infografia_proyecto.png"

if ruta_infografia.exists():
    st.image(str(ruta_infografia), caption="Infografía de Arquitectura y Operación del Sistema de Control de Obra", use_container_width=True)

st.markdown(f"<div class='main-title'>{st.session_state.nombre_proyecto}</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Plataforma de Monitoreo de Avance Físico de Obra y Curva S</div>", unsafe_allow_html=True)

df_actual = st.session_state.df_obra

if not df_actual.empty:
    min_sem = int(df_actual["semana"].min())
    max_sem = int(df_actual["semana"].max())
    especialidades_disponibles = sorted(df_actual["especialidad"].unique().tolist())
    encargados_disponibles = sorted(df_actual["encargado"].unique().tolist())
else:
    min_sem = 1
    max_sem = 12
    especialidades_disponibles = []
    encargados_disponibles = []

with st.expander("Parámetros y Filtros del Proyecto", expanded=False):
    col_par1, col_par2, col_par3 = st.columns(3)
    with col_par1:
        st.session_state.nombre_proyecto = st.text_input(
            "Nombre de la Obra / Proyecto:",
            value=st.session_state.nombre_proyecto,
            help="Permite personalizar el título y reportes generados"
        )
    with col_par2:
        st.session_state.tolerancia_desviacion = st.slider(
            "Tolerancia de Desviación (±%):",
            min_value=0.0,
            max_value=5.0,
            value=st.session_state.tolerancia_desviacion,
            step=0.1,
            help="Margen porcentual para clasificar como Obra según lo previsto"
        )
    with col_par3:
        meta_avance = st.number_input(
            "Meta Programada Final (%):",
            min_value=50.0,
            max_value=100.0,
            value=100.0,
            step=1.0
        )

    col_fil1, col_fil2, col_fil3 = st.columns(3)
    with col_fil1:
        rango_semanas = st.slider(
            "Filtrar por Rango de Semanas:",
            min_value=min_sem,
            max_value=max_sem,
            value=(min_sem, max_sem),
            step=1
        )
    with col_fil2:
        especialidades_sel = st.multiselect(
            "Especialidades a Evaluar:",
            options=especialidades_disponibles,
            default=especialidades_disponibles
        )
    with col_fil3:
        encargados_sel = st.multiselect(
            "Encargados / Frentes:",
            options=encargados_disponibles,
            default=encargados_disponibles
        )

    if st.button("Restablecer Datos Iniciales", use_container_width=True):
        st.session_state.df_obra = cargar_datos_base()
        st.success("Datos restablecidos al estado inicial!")
        st.rerun()

df_filtrado = df_actual.copy()
if not df_filtrado.empty:
    df_filtrado = df_filtrado[
        (df_filtrado["semana"] >= rango_semanas[0]) &
        (df_filtrado["semana"] <= rango_semanas[1]) &
        (df_filtrado["especialidad"].isin(especialidades_sel)) &
        (df_filtrado["encargado"].isin(encargados_sel))
    ]

resumen_semanal = calcular_resumen_semanal(df_filtrado, tolerancia=st.session_state.tolerancia_desviacion)
resumen_esp = calcular_resumen_especialidad(df_filtrado)
resumen_enc = calcular_resumen_encargados(df_filtrado)
kpis = calcular_kpis_generales(df_filtrado, tolerancia=st.session_state.tolerancia_desviacion)

col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)

with col_kpi1:
    st.metric(
        label="Semanas Evaluadas",
        value=f"Sem. {kpis['ultima_semana']}",
        delta=f"Total: {len(resumen_semanal)} sem."
    )

with col_kpi2:
    st.metric(
        label="Avance Planificado",
        value=f"{kpis['total_plan_acumulado']:.2f}%",
        delta=f"Meta: {meta_avance:.0f}%"
    )

with col_kpi3:
    st.metric(
        label="Avance Real Acumulado",
        value=f"{kpis['total_real_acumulado']:.2f}%",
        delta=f"{kpis['desviacion_global']:+.2f}% vs Plan",
        delta_color="normal" if kpis['desviacion_global'] >= 0 else "inverse"
    )

with col_kpi4:
    st.metric(
        label="SPI (Índice Cronograma)",
        value=f"{kpis['spi_global']:.2f}",
        delta="Eficiente (≥ 1.0)" if kpis['spi_global'] >= 1.0 else "Retraso (< 1.0)",
        delta_color="normal" if kpis['spi_global'] >= 1.0 else "inverse"
    )

with col_kpi5:
    estado = kpis['estado_global']
    badge_class = "badge-adelantada" if "Adelantada" in estado else ("badge-atrasada" if "Atrasada" in estado else "badge-previsto")
    st.markdown("**Estado General de Obra:**")
    st.markdown(f"<span class='{badge_class}'>{estado}</span>", unsafe_allow_html=True)
    st.caption(f"Tolerancia configurada: ±{st.session_state.tolerancia_desviacion}%")

st.markdown("<br>", unsafe_allow_html=True)

tab_graficos, tab_tablas, tab_datos = st.tabs([
    "Gráficos & Curva S ",
    "Tablas & Resumen de Cálculos",
    "Carga de Datos"
])

with tab_graficos:
    st.markdown("<div class='section-header'>Análisis Gráfico del Avance Físico de Obra</div>", unsafe_allow_html=True)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.plotly_chart(generar_grafico_curva_s(resumen_semanal), use_container_width=True)
        st.caption("**Curva S**: Muestra la evolución acumulativa del avance real frente a la línea base planificada.")
    
    with col_g2:
        st.plotly_chart(generar_grafico_produccion_semanal(resumen_semanal), use_container_width=True)
        st.caption("**Producción Semanal**: Compara el volumen producido por semana e ilustra la brecha de rendimiento.")

    col_g3, col_g4 = st.columns(2)
    with col_g3:
        st.plotly_chart(generar_grafico_especialidades(resumen_esp), use_container_width=True)
        st.caption("**Avance por Especialidad**: Identifica frentes críticos y distribución porcentual del trabajo físico.")
    
    with col_g4:
        st.plotly_chart(generar_grafico_encargados(resumen_enc), use_container_width=True)
        st.caption("**Avance por Encargado**: Evalúa la gestión de cada responsable y el número de partidas asignadas.")

    st.markdown("---")
    st.subheader("Descargar Resultados Consolidados")
    excel_data = exportar_a_excel(
        df_base=df_filtrado,
        df_resumen_semanal=resumen_semanal,
        df_especialidad=resumen_esp,
        df_encargados=resumen_enc,
        kpis=kpis
    )
    st.download_button(
        label="Exportar Resultados a EXCEL (.xlsx)",
        data=excel_data,
        file_name=f"Reporte_Control_Obra_{st.session_state.nombre_proyecto.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with tab_tablas:
    st.markdown("<div class='section-header'>Tablas Consolidadas </div>", unsafe_allow_html=True)

    st.subheader("1. Control Semanal y Curva S")
    if not resumen_semanal.empty:
        df_mostrar_sem = resumen_semanal.copy()
        df_mostrar_sem = df_mostrar_sem.rename(columns={
            "semana": "Semana",
            "avance_plan_semanal": "Plan Sem. (%)",
            "avance_real_semanal": "Real Sem. (%)",
            "diferencia_semanal": "Diferencia (%)",
            "avance_plan_acumulado": "Plan Acum. (%)",
            "avance_real_acumulado": "Real Acum. (%)",
            "brecha_acumulada": "Brecha Acum. (%)",
            "spi": "SPI",
            "interpretacion": "Interpretación de Estado"
        })
        st.dataframe(
            df_mostrar_sem.style.format({
                "Plan Sem. (%)": "{:.2f}%",
                "Real Sem. (%)": "{:.2f}%",
                "Diferencia (%)": "{:+.2f}%",
                "Plan Acum. (%)": "{:.2f}%",
                "Real Acum. (%)": "{:.2f}%",
                "Brecha Acum. (%)": "{:+.2f}%",
                "SPI": "{:.2f}"
            }),
            use_container_width=True
        )
    else:
        st.info("No hay datos para mostrar con los filtros seleccionados.")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("2. Desempeño por Especialidad")
        if not resumen_esp.empty:
            df_mostrar_esp = resumen_esp.rename(columns={
                "especialidad": "Especialidad",
                "avance_real_total": "Real Total (%)",
                "avance_plan_total": "Plan Total (%)",
                "cantidad_partidas": "N° Partidas",
                "porcentaje_contribucion": "Contribución (%)",
                "diferencia": "Diferencia (%)"
            })
            st.dataframe(
                df_mostrar_esp.style.format({
                    "Real Total (%)": "{:.2f}%",
                    "Plan Total (%)": "{:.2f}%",
                    "Contribución (%)": "{:.1f}%",
                    "Diferencia (%)": "{:+.2f}%"
                }),
                use_container_width=True
            )

    with col_t2:
        st.subheader("3. Desempeño por Encargado")
        if not resumen_enc.empty:
            df_mostrar_enc = resumen_enc.rename(columns={
                "encargado": "Encargado",
                "cantidad_partidas": "Partidas",
                "avance_plan_total": "Plan Total (%)",
                "avance_real_total": "Real Total (%)",
                "diferencia": "Brecha (%)",
                "cumplimiento_pct": "Cumplimiento (%)"
            })
            st.dataframe(
                df_mostrar_enc.style.format({
                    "Plan Total (%)": "{:.2f}%",
                    "Real Total (%)": "{:.2f}%",
                    "Brecha (%)": "{:+.2f}%",
                    "Cumplimiento (%)": "{:.1f}%"
                }),
                use_container_width=True
            )

    with st.expander("Ver Base de Datos Detallada de Partidas"):
        st.write(f"Total de registros filtrados: **{len(df_filtrado)} partidas**")
        st.dataframe(df_filtrado, use_container_width=True)

    
with tab_datos:
    st.markdown("<div class='section-header'>Carga y Actualización de Parámetros de Obra</div>", unsafe_allow_html=True)
    st.write("Esta sección permite ingresar nuevos registros manualmente mediante widgets editables o cargar conjuntos completos de datos vía archivos Excel/CSV.")

    col_izq, col_der = st.columns([1, 1], gap="large")

    with col_izq:
        st.subheader("Carga Manual de Nuevas Partidas")
        st.caption("Ingrese los parámetros de la partida y presione el botón para actualizar el modelo en tiempo real.")

        with st.form("form_carga_manual", clear_on_submit=False):
            nueva_semana = st.number_input(
                "1. Semana de Ejecución (N°):",
                min_value=1,
                max_value=52,
                value=13,
                step=1
            )

            nuevo_codigo = st.text_input(
                "2. Código de Partida (ej. P21, P22):",
                value="P21"
            )

            nuevo_nombre = st.text_input(
                "3. Descripción / Nombre de la Partida:",
                value="Hormigonado de vigas y losas de entrepiso"
            )

            opciones_esp = ["Estructura", "Arquitectura", "Instalaciones", "Obras preliminares", "Terminaciones", "Movimiento de tierras"]
            nueva_especialidad = st.selectbox(
                "4. Especialidad Técnica:",
                options=opciones_esp,
                index=0
            )

            nuevo_encargado = st.text_input(
                "5. Encargado / Residente Responsable:",
                value="Carlos Muñoz"
            )

            nuevo_peso = st.number_input(
                "6. Peso Ponderado de la Partida (%):",
                min_value=0.0,
                max_value=100.0,
                value=5.0,
                step=0.5
            )

            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                nuevo_plan = st.number_input(
                    "7. Avance Plan. Semanal (%):",
                    min_value=0.0,
                    max_value=100.0,
                    value=2.50,
                    step=0.1
                )
            with col_sub2:
                nuevo_real = st.number_input(
                    "8. Avance Real Semanal (%):",
                    min_value=0.0,
                    max_value=100.0,
                    value=2.85,
                    step=0.1
                )

            btn_agregar = st.form_submit_button("Registrar / Actualizar Partida Manual", use_container_width=True)

        if btn_agregar:
            if not nuevo_codigo or not nuevo_nombre:
                st.error("Por favor ingrese código y nombre de partida válidos.")
            else:
                st.session_state.df_obra = agregar_partida_manual(
                    df_actual=st.session_state.df_obra,
                    semana=nueva_semana,
                    codigo_partida=nuevo_codigo,
                    partida=nuevo_nombre,
                    especialidad=nueva_especialidad,
                    encargado=nuevo_encargado,
                    peso_partida=nuevo_peso,
                    avance_plan_semanal=nuevo_plan,
                    avance_real_semanal=nuevo_real
                )
                st.success(f"Partida '{nuevo_codigo} - {nuevo_nombre}' registrada exitosamente en Semana {nueva_semana}!")
                st.rerun()

    with col_der:
        st.subheader("Carga de Datos desde Archivo")
        st.caption("Cargue un archivo en formato **.CSV** o **.XLSX** con la estructura de partidas de obra.")

        archivo_cargado = st.file_uploader(
            "Seleccionar archivo de obra (.csv o .xlsx):",
            type=["csv", "xlsx", "xls"],
            help="El archivo debe contener las columnas: semana, codigo_partida, partida, especialidad, encargado, peso_partida, avance_plan_semanal, avance_real_semanal"
        )

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            btn_procesar = st.button("Procesar y Cargar Archivo", use_container_width=True)
        with col_b2:
            plantilla_bytes = generar_plantilla_excel()
            st.download_button(
                label="Descargar Plantilla Excel",
                data=plantilla_bytes,
                file_name="plantilla_control_avance_obra.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        if btn_procesar:
            if archivo_cargado is None:
                st.warning("Primero debes seleccionar un archivo utilizando el selector superior.")
            else:
                exito, msg, df_subido = procesar_archivo_subido(archivo_cargado)
                if exito and df_subido is not None:
                    st.session_state.df_obra = df_subido
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        with st.expander("Ver Estructura Requerida de Columnas"):
            st.markdown("""
            El archivo cargado debe incluir obligatoriamente las siguientes columnas:
            - `semana` (Número entero de 1 a N)
            - `codigo_partida` (Texto, ej: P01, P02)
            - `partida` (Texto descriptivo)
            - `especialidad` (Texto: Estructura, Arquitectura, Instalaciones, etc.)
            - `encargado` (Texto con el nombre del responsable)
            - `peso_partida` (Número con la ponderación)
            - `avance_plan_semanal` (Número en porcentaje)
            - `avance_real_semanal` (Número en porcentaje)
            """)
