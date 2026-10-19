"""
Módulo de Cálculos y Análisis de Avance Físico de Obra
Basado en la lógica desarrollada en el Entregable N° 1.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


def calcular_avance_semanal(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calcula el avance semanal planificado, real y su diferencia.
    
    Args:
        df: DataFrame con las columnas 'semana', 'avance_plan_semanal', 'avance_real_semanal'.
        
    Returns:
        Tupla con (avance_plan_semanal, avance_real_semanal, diferencia_semanal)
    """
    if df.empty:
        vacio = pd.Series(dtype=float)
        return vacio, vacio, vacio

    avance_plan_semanal = df.groupby("semana")["avance_plan_semanal"].sum()
    avance_real_semanal = df.groupby("semana")["avance_real_semanal"].sum()
    diferencia_semanal = avance_real_semanal - avance_plan_semanal

    return avance_plan_semanal, avance_real_semanal, diferencia_semanal


def calcular_avance_acumulado(avance_plan_semanal: pd.Series, avance_real_semanal: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calcula los avances acumulados para la Curva S y su brecha acumulada.
    
    Args:
        avance_plan_semanal: Serie con avance planificado semanal agrupado por semana.
        avance_real_semanal: Serie con avance real semanal agrupado por semana.
        
    Returns:
        Tupla con (avance_plan_acumulado, avance_real_acumulado, brecha_acumulada)
    """
    avance_plan_acumulado = avance_plan_semanal.cumsum()
    avance_real_acumulado = avance_real_semanal.cumsum()
    brecha_acumulada = avance_real_acumulado - avance_plan_acumulado

    return avance_plan_acumulado, avance_real_acumulado, brecha_acumulada


def interpretar_estado(real_acum: float, plan_acum: float, tolerancia: float = 0.0) -> str:
    """
    Determina si la obra está adelantada, atrasada o según lo previsto.
    
    Args:
        real_acum: Avance real acumulado en porcentaje.
        plan_acum: Avance planificado acumulado en porcentaje.
        tolerancia: Margen en porcentaje (+/-) para clasificar como 'Obra según lo previsto'.
        
    Returns:
        String descriptivo del estado de la obra.
    """
    diff = real_acum - plan_acum
    if diff > tolerancia:
        return "Obra Adelantada"
    elif diff < -tolerancia:
        return "Obra Atrasada"
    else:
        return "Obra según lo previsto"


def calcular_resumen_semanal(df: pd.DataFrame, tolerancia: float = 0.0) -> pd.DataFrame:
    """
    Genera la tabla unificada de resumen semanal con avances, acumulados e interpretación.
    
    Args:
        df: DataFrame original de partidas de obra.
        tolerancia: Umbral de tolerancia porcentual para el estado.
        
    Returns:
        DataFrame ordenado por semana con indicadores de desempeño.
    """
    if df.empty:
        return pd.DataFrame()

    plan_sem, real_sem, diff_sem = calcular_avance_semanal(df)
    plan_acum, real_acum, brecha_acum = calcular_avance_acumulado(plan_sem, real_sem)

    resumen = pd.DataFrame({
        "semana": plan_sem.index,
        "avance_plan_semanal": plan_sem.values,
        "avance_real_semanal": real_sem.values,
        "diferencia_semanal": diff_sem.values,
        "avance_plan_acumulado": plan_acum.values,
        "avance_real_acumulado": real_acum.values,
        "brecha_acumulada": brecha_acum.values,
    })

    # Indicador de Desempeño del Cronograma (SPI = Schedule Performance Index)
    # Si plan_acum == 0 se maneja de forma segura
    resumen["spi"] = np.where(
        resumen["avance_plan_acumulado"] > 0,
        resumen["avance_real_acumulado"] / resumen["avance_plan_acumulado"],
        1.0
    )

    # Interpretación aplicando la regla del entregable
    resumen["interpretacion"] = resumen.apply(
        lambda r: interpretar_estado(r["avance_real_acumulado"], r["avance_plan_acumulado"], tolerancia),
        axis=1
    )

    return resumen


def calcular_resumen_especialidad(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el avance real, planificado y número de partidas por especialidad.
    """
    if df.empty:
        return pd.DataFrame()

    resumen = df.groupby("especialidad").agg(
        avance_real_total=("avance_real_semanal", "sum"),
        avance_plan_total=("avance_plan_semanal", "sum"),
        cantidad_partidas=("codigo_partida", "nunique")
    ).reset_index()

    total_real = resumen["avance_real_total"].sum()
    resumen["porcentaje_contribucion"] = np.where(
        total_real > 0,
        (resumen["avance_real_total"] / total_real) * 100,
        0.0
    )
    resumen["diferencia"] = resumen["avance_real_total"] - resumen["avance_plan_total"]

    return resumen.sort_values(by="avance_real_total", ascending=False)


def calcular_resumen_encargados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula el avance, partidas y rendimiento por cada encargado o responsable.
    """
    if df.empty:
        return pd.DataFrame()

    resumen = df.groupby("encargado").agg(
        cantidad_partidas=("codigo_partida", "nunique"),
        avance_plan_total=("avance_plan_semanal", "sum"),
        avance_real_total=("avance_real_semanal", "sum")
    ).reset_index()

    resumen["diferencia"] = resumen["avance_real_total"] - resumen["avance_plan_total"]
    resumen["cumplimiento_pct"] = np.where(
        resumen["avance_plan_total"] > 0,
        (resumen["avance_real_total"] / resumen["avance_plan_total"]) * 100,
        100.0
    )

    return resumen.sort_values(by="avance_real_total", ascending=False)


def calcular_kpis_generales(df: pd.DataFrame, tolerancia: float = 0.0) -> Dict[str, Any]:
    """
    Calcula métricas clave de alto nivel (KPIs) para el dashboard ejecutivo.
    """
    if df.empty:
        return {
            "ultima_semana": 0,
            "total_plan_acumulado": 0.0,
            "total_real_acumulado": 0.0,
            "desviacion_global": 0.0,
            "estado_global": "Sin Datos",
            "spi_global": 1.0,
            "total_partidas": 0,
            "total_encargados": 0,
            "total_especialidades": 0
        }

    resumen_sem = calcular_resumen_semanal(df, tolerancia=tolerancia)
    ultima_fila = resumen_sem.iloc[-1]

    total_plan = ultima_fila["avance_plan_acumulado"]
    total_real = ultima_fila["avance_real_acumulado"]
    desviacion = total_real - total_plan
    estado = ultima_fila["interpretacion"]
    spi = ultima_fila["spi"]

    return {
        "ultima_semana": int(ultima_fila["semana"]),
        "total_plan_acumulado": round(float(total_plan), 2),
        "total_real_acumulado": round(float(total_real), 2),
        "desviacion_global": round(float(desviacion), 2),
        "estado_global": estado,
        "spi_global": round(float(spi), 2),
        "total_partidas": int(df["codigo_partida"].nunique()),
        "total_encargados": int(df["encargado"].nunique()),
        "total_especialidades": int(df["especialidad"].nunique())
    }
