"""
Módulo de Control y Monitoreo de Avance Físico de Obra
Curso Python - AECODE
"""

from .calculos import (
    calcular_avance_semanal,
    calcular_avance_acumulado,
    calcular_resumen_semanal,
    calcular_resumen_especialidad,
    calcular_resumen_encargados,
    calcular_kpis_generales
)

from .graficos import (
    generar_grafico_curva_s,
    generar_grafico_produccion_semanal,
    generar_grafico_especialidades,
    generar_grafico_encargados
)

from .exportador import exportar_a_excel

from .datos import (
    cargar_datos_base,
    procesar_archivo_subido,
    generar_plantilla_excel,
    agregar_partida_manual,
    COLUMNAS_REQUERIDAS
)

__all__ = [
    "calcular_avance_semanal",
    "calcular_avance_acumulado",
    "calcular_resumen_semanal",
    "calcular_resumen_especialidad",
    "calcular_resumen_encargados",
    "calcular_kpis_generales",
    "generar_grafico_curva_s",
    "generar_grafico_produccion_semanal",
    "generar_grafico_especialidades",
    "generar_grafico_encargados",
    "exportar_a_excel",
    "cargar_datos_base",
    "procesar_archivo_subido",
    "generar_plantilla_excel",
    "agregar_partida_manual",
    "COLUMNAS_REQUERIDAS"
]
