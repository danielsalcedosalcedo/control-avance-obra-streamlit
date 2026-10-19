"""
Módulo de Visualización y Gráficos Interactivos
Genera gráficos interactivos con Plotly para análisis de obra civil.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd


# Paleta de colores profesional para Ingeniería y Construcción
COLOR_PLAN = "#2b5c8f"       # Azul corporativo ingeniería
COLOR_REAL = "#00a896"       # Verde esmeralda / Teal (Avance real)
COLOR_DIFF_POS = "#2ec4b6"   # Positivo (Adelantado)
COLOR_DIFF_NEG = "#e71d36"   # Negativo (Atrasado)
COLOR_ACCENT = "#f4a261"     # Naranja / Dorado construcción
COLOR_BG_CARD = "rgba(255, 255, 255, 0.02)"


def generar_grafico_curva_s(df_resumen_semanal: pd.DataFrame) -> go.Figure:
    """
    Gráfico 1: Curva S de Avance Físico Acumulado (Planificado vs Real)
    con marcadores, sombreado y tooltips informativos.
    """
    fig = go.Figure()

    if df_resumen_semanal.empty:
        fig.update_layout(title="Sin datos para la Curva S")
        return fig

    # Línea de Avance Planificado Acumulado
    fig.add_trace(go.Scatter(
        x=df_resumen_semanal["semana"],
        y=df_resumen_semanal["avance_plan_acumulado"],
        mode="lines+markers",
        name="Avance Planificado Acumulado",
        line=dict(color=COLOR_PLAN, width=3, dash="dash"),
        marker=dict(size=8, symbol="diamond", color=COLOR_PLAN),
        hovertemplate="<b>Semana %{x}</b><br>Plan Acumulado: %{y:.2f}%<extra></extra>"
    ))

    # Línea de Avance Real Acumulado
    fig.add_trace(go.Scatter(
        x=df_resumen_semanal["semana"],
        y=df_resumen_semanal["avance_real_acumulado"],
        mode="lines+markers",
        name="Avance Real Acumulado",
        line=dict(color=COLOR_REAL, width=3.5),
        marker=dict(size=9, symbol="circle", color=COLOR_REAL),
        fill="tonexty",
        fillcolor="rgba(0, 168, 150, 0.12)",
        hovertemplate="<b>Semana %{x}</b><br>Real Acumulado: %{y:.2f}%<br>Estado: %{text}<extra></extra>",
        text=df_resumen_semanal["interpretacion"]
    ))

    # Meta 100%
    fig.add_hline(
        y=100,
        line_dash="dot",
        line_color="gray",
        annotation_text="Meta 100%",
        annotation_position="bottom right"
    )

    fig.update_layout(
        title="<b>Gráfico 1: Curva S de Avance Físico Acumulado (Planificado vs Real)</b>",
        xaxis_title="Semana de Ejecución",
        yaxis_title="Avance Acumulado (%)",
        xaxis=dict(tickmode="linear", tick0=1, dtick=1, gridcolor="rgba(200,200,200,0.15)"),
        yaxis=dict(gridcolor="rgba(200,200,200,0.15)", zeroline=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white"
    )

    return fig


def generar_grafico_produccion_semanal(df_resumen_semanal: pd.DataFrame) -> go.Figure:
    """
    Gráfico 2: Producción Semanal (Avance Planificado vs Avance Real)
    y Brecha Semanal (Diferencia Real - Plan).
    """
    if df_resumen_semanal.empty:
        fig = go.Figure()
        fig.update_layout(title="Sin datos de producción semanal")
        return fig

    fig = make_subplots(
        rows=1, cols=1,
        specs=[[{"secondary_y": True}]]
    )

    # Barras Planificado Semanal
    fig.add_trace(
        go.Bar(
            x=df_resumen_semanal["semana"],
            y=df_resumen_semanal["avance_plan_semanal"],
            name="Plan Semanal (%)",
            marker_color=COLOR_PLAN,
            opacity=0.85,
            hovertemplate="Semana %{x}<br>Plan Semanal: %{y:.2f}%<extra></extra>"
        ),
        secondary_y=False
    )

    # Barras Real Semanal
    fig.add_trace(
        go.Bar(
            x=df_resumen_semanal["semana"],
            y=df_resumen_semanal["avance_real_semanal"],
            name="Real Semanal (%)",
            marker_color=COLOR_REAL,
            opacity=0.95,
            hovertemplate="Semana %{x}<br>Real Semanal: %{y:.2f}%<extra></extra>"
        ),
        secondary_y=False
    )

    # Línea de Diferencia Semanal en el eje secundario
    colores_diff = [COLOR_DIFF_POS if v >= 0 else COLOR_DIFF_NEG for v in df_resumen_semanal["diferencia_semanal"]]
    
    fig.add_trace(
        go.Scatter(
            x=df_resumen_semanal["semana"],
            y=df_resumen_semanal["diferencia_semanal"],
            name="Diferencia Semanal (Real - Plan)",
            mode="lines+markers",
            line=dict(color=COLOR_ACCENT, width=2.5),
            marker=dict(size=8, color=colores_diff),
            hovertemplate="Semana %{x}<br>Diferencia: %{y:.2f}%<extra></extra>"
        ),
        secondary_y=True
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="rgba(100,100,100,0.5)",
        secondary_y=True
    )

    fig.update_layout(
        title="<b>Gráfico 2: Producción Semanal y Brecha de Avance (Planificado vs Real)</b>",
        xaxis_title="Semana",
        yaxis_title="Avance Semanal (%)",
        xaxis=dict(tickmode="linear", tick0=1, dtick=1, gridcolor="rgba(200,200,200,0.15)"),
        yaxis=dict(gridcolor="rgba(200,200,200,0.15)"),
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white"
    )

    fig.update_yaxes(title_text="Diferencia (%)", secondary_y=True, showgrid=False)

    return fig


def generar_grafico_especialidades(df_especialidad: pd.DataFrame) -> go.Figure:
    """
    Gráfico 3: Avance Físico y Contribución por Especialidad de Obra.
    Muestra barras horizontales de comparación Plan vs Real por cada especialidad.
    """
    if df_especialidad.empty:
        fig = go.Figure()
        fig.update_layout(title="Sin datos de especialidades")
        return fig

    fig = go.Figure()

    # Avance Planificado
    fig.add_trace(go.Bar(
        y=df_especialidad["especialidad"],
        x=df_especialidad["avance_plan_total"],
        name="Avance Planificado Total (%)",
        orientation="h",
        marker_color=COLOR_PLAN,
        hovertemplate="<b>%{y}</b><br>Plan: %{x:.2f}%<extra></extra>"
    ))

    # Avance Real
    fig.add_trace(go.Bar(
        y=df_especialidad["especialidad"],
        x=df_especialidad["avance_real_total"],
        name="Avance Real Total (%)",
        orientation="h",
        marker_color=COLOR_REAL,
        text=df_especialidad["avance_real_total"].apply(lambda v: f"{v:.1f}%"),
        textposition="auto",
        hovertemplate="<b>%{y}</b><br>Real: %{x:.2f}%<br>Partidas: " + df_especialidad["cantidad_partidas"].astype(str) + "<extra></extra>"
    ))

    fig.update_layout(
        title="<b>Gráfico 3: Avance Físico Acumulado por Especialidad (Plan vs Real)</b>",
        xaxis_title="Avance Total (%)",
        yaxis_title="Especialidad",
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(gridcolor="rgba(200,200,200,0.15)"),
        margin=dict(l=40, r=40, t=60, b=40),
        template="plotly_white"
    )

    return fig


def generar_grafico_encargados(df_encargados: pd.DataFrame) -> go.Figure:
    """
    Gráfico 4: Rendimiento y Desempeño por Encargado / Responsable de Frente
    Compara Avance Planificado vs Avance Real y destaca la cantidad de partidas a su cargo.
    """
    if df_encargados.empty:
        fig = go.Figure()
        fig.update_layout(title="Sin datos de encargados")
        return fig

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_encargados["encargado"],
        y=df_encargados["avance_plan_total"],
        name="Avance Planificado (%)",
        marker_color=COLOR_PLAN,
        hovertemplate="<b>%{x}</b><br>Plan: %{y:.2f}%<extra></extra>"
    ))

    fig.add_trace(go.Bar(
        x=df_encargados["encargado"],
        y=df_encargados["avance_real_total"],
        name="Avance Real (%)",
        marker_color=COLOR_REAL,
        text=df_encargados.apply(lambda r: f"{r['avance_real_total']:.1f}% ({int(r['cantidad_partidas'])} part.)", axis=1),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Real: %{y:.2f}%<br>Partidas: %{text}<extra></extra>"
    ))

    fig.update_layout(
        title="<b>Gráfico 4: Avance por Encargado (Planificado vs Real) y Partidas Asignadas</b>",
        xaxis_title="Responsable / Encargado",
        yaxis_title="Avance Físico Total (%)",
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(gridcolor="rgba(200,200,200,0.15)"),
        margin=dict(l=40, r=40, t=60, b=60),
        template="plotly_white"
    )

    return fig
