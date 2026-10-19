"""
Módulo de Gestión de Datos, Carga de Archivos y Entrada Manual
"""

import io
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any
import pandas as pd


COLUMNAS_REQUERIDAS = [
    "semana",
    "codigo_partida",
    "partida",
    "especialidad",
    "encargado",
    "peso_partida",
    "avance_plan_semanal",
    "avance_real_semanal"
]


def _normalizar_columnas(cols: List[str]) -> List[str]:
    """Limpia nombres de columnas: minúsculas, sin espacios ni caracteres especiales."""
    limpias = []
    for c in cols:
        limpia = str(c).strip().lower().replace(" ", "_").replace(".", "")
        limpias.append(limpia)
    return limpias


def cargar_datos_base() -> pd.DataFrame:
    """
    Carga el dataset base del Entregable N° 1.
    Busca en varias rutas posibles dentro del proyecto.
    """
    rutas_posibles = [
        Path("data/avance_fisico_semanal_obra.csv"),
        Path("avance_fisico_semanal_obra.csv"),
        Path("Tarea_02/data/avance_fisico_semanal_obra.csv"),
        Path("Tarea_02/avance_fisico_semanal_obra.csv"),
        Path("Tarea_01/avance_fisico_semanal_obra.csv"),
        Path(__file__).parent.parent / "data" / "avance_fisico_semanal_obra.csv",
        Path(__file__).parent.parent / "avance_fisico_semanal_obra.csv"
    ]

    for ruta in rutas_posibles:
        if ruta.exists():
            try:
                df = pd.read_csv(ruta)
                df.columns = _normalizar_columnas(df.columns.tolist())
                # Asegurar tipos
                df["semana"] = pd.to_numeric(df["semana"], errors="coerce").fillna(1).astype(int)
                df["avance_plan_semanal"] = pd.to_numeric(df["avance_plan_semanal"], errors="coerce").fillna(0.0)
                df["avance_real_semanal"] = pd.to_numeric(df["avance_real_semanal"], errors="coerce").fillna(0.0)
                return df
            except Exception as e:
                print(f"Error al leer {ruta}: {e}")

    # Si no se encuentra archivo, retornar un DataFrame base sintético de seguridad
    return pd.DataFrame(columns=COLUMNAS_REQUERIDAS)


def procesar_archivo_subido(archivo) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """
    Lee y valida un archivo cargado por el usuario (CSV o Excel).
    
    Returns:
        (éxito: bool, mensaje: str, dataframe: Optional[pd.DataFrame])
    """
    try:
        nombre = archivo.name.lower()
        if nombre.endswith(".csv"):
            # Intentar primero con utf-8 y luego con latin-1
            try:
                df = pd.read_csv(archivo, encoding="utf-8")
            except UnicodeDecodeError:
                archivo.seek(0)
                df = pd.read_csv(archivo, encoding="latin-1")
        elif nombre.endswith((".xlsx", ".xls")):
            df = pd.read_excel(archivo)
        else:
            return False, "Formato no compatible. Por favor sube un archivo .CSV o .XLSX.", None

        # Normalizar columnas
        df.columns = _normalizar_columnas(df.columns.tolist())

        # Verificar columnas obligatorias
        faltantes = [col for col in COLUMNAS_REQUERIDAS if col not in df.columns]
        if faltantes:
            return (
                False,
                f"El archivo no contiene las siguientes columnas requeridas: {', '.join(faltantes)}",
                None
            )

        # Casteo y limpieza de datos
        df["semana"] = pd.to_numeric(df["semana"], errors="coerce")
        df["avance_plan_semanal"] = pd.to_numeric(df["avance_plan_semanal"], errors="coerce")
        df["avance_real_semanal"] = pd.to_numeric(df["avance_real_semanal"], errors="coerce")
        
        # Filtrar posibles nulos críticos
        df = df.dropna(subset=["semana", "avance_plan_semanal", "avance_real_semanal"])
        df["semana"] = df["semana"].astype(int)

        if "peso_partida" in df.columns:
            df["peso_partida"] = pd.to_numeric(df["peso_partida"], errors="coerce").fillna(0)

        # Convertir a texto las columnas categóricas
        for col_str in ["codigo_partida", "partida", "especialidad", "encargado"]:
            df[col_str] = df[col_str].fillna("N/A").astype(str)

        return True, f"¡Archivo cargado con éxito! ({len(df)} registros procesados)", df

    except Exception as e:
        return False, f"Ocurrió un error al procesar el archivo: {str(e)}", None


def agregar_partida_manual(
    df_actual: pd.DataFrame,
    semana: int,
    codigo_partida: str,
    partida: str,
    especialidad: str,
    encargado: str,
    peso_partida: float,
    avance_plan_semanal: float,
    avance_real_semanal: float
) -> pd.DataFrame:
    """
    Inserta o actualiza un registro manual en el DataFrame activo.
    """
    nueva_fila = {
        "semana": int(semana),
        "codigo_partida": str(codigo_partida).strip().upper(),
        "partida": str(partida).strip(),
        "especialidad": str(especialidad).strip(),
        "encargado": str(encargado).strip(),
        "peso_partida": float(peso_partida),
        "avance_plan_semanal": float(avance_plan_semanal),
        "avance_real_semanal": float(avance_real_semanal)
    }

    df_nuevo = pd.concat([df_actual, pd.DataFrame([nueva_fila])], ignore_index=True)
    return df_nuevo


def generar_plantilla_excel() -> bytes:
    """
    Genera un archivo Excel de plantilla con la estructura correcta y datos de ejemplo.
    """
    datos_ejemplo = [
        {
            "semana": 1,
            "codigo_partida": "P01",
            "partida": "Instalación de faenas y cierros",
            "especialidad": "Obras preliminares",
            "encargado": "Carlos Muñoz",
            "peso_partida": 5,
            "avance_plan_semanal": 1.33,
            "avance_real_semanal": 1.53
        },
        {
            "semana": 1,
            "codigo_partida": "P02",
            "partida": "Trazado y replanteo topográfico",
            "especialidad": "Obras preliminares",
            "encargado": "Carlos Muñoz",
            "peso_partida": 5,
            "avance_plan_semanal": 0.00,
            "avance_real_semanal": 0.00
        },
        {
            "semana": 2,
            "codigo_partida": "P03",
            "partida": "Excavaciones masivas",
            "especialidad": "Estructura",
            "encargado": "Andrés Rojas",
            "peso_partida": 10,
            "avance_plan_semanal": 2.50,
            "avance_real_semanal": 2.10
        }
    ]

    df_plantilla = pd.DataFrame(datos_ejemplo)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_plantilla.to_excel(writer, sheet_name="Plantilla_Obra", index=False)

    output.seek(0)
    return output.getvalue()
