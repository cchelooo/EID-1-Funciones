# Utilidades generales

from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class EvalResult:
    # Representa el resultado de una operacion simple con un mensaje
    ok: bool
    message: str

def ok(msg: str) -> EvalResult:
    # Crea un resultado satisfactorio
    return EvalResult(True, msg)

def err(msg: str) -> EvalResult:
    # Crea un resultado de error
    return EvalResult(False, msg)

def stringify_points(points: List[Tuple[float, float]]) -> str:
    # Devuelve puntos como texto (x, y). Para reportes.
    if not points:
        return "∅"
    return ", ".join(f"({x:.6g}, {y:.6g})" for x, y in points)

def fmt_set(s) -> str:
    # Convierte conjuntos SymPy (Interval, Union, FiniteSet, Reals, EmptySet) a texto.
    # Nota: str() es suficiente para proposito educativo en esta app.
    
    try:
        return str(s)
    except Exception:
        return "No disponible"
