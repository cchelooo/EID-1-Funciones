# Utilidades generales

from dataclasses import dataclass
from typing import List, Tuple
from sympy import Interval, Union, EmptySet, Reals, FiniteSet

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

from sympy import Interval, Union, EmptySet, Reals, FiniteSet, oo

def fmt_set(s) -> str:
    """
    Convierte conjuntos SymPy (Interval, Union, FiniteSet, Reals, EmptySet)
    a texto matemático entendible (sin palabras de código).
    """
    try:
        # Conjunto vacío
        if s == EmptySet:
            return "∅"

        # Conjunto de todos los reales
        if s == Reals:
            return "ℝ"

        # Intervalo
        if isinstance(s, Interval):
            a = "-∞" if s.start == -oo else str(s.start)
            b = "∞" if s.end == oo else str(s.end)
            left = "(" if s.left_open else "["
            right = ")" if s.right_open else "]"
            return f"{left}{a}, {b}{right}"

        # Unión de intervalos
        if isinstance(s, Union):
            return " U ".join(fmt_set(arg) for arg in sorted(s.args, key=lambda x: str(x)))

        # Conjunto finito
        if isinstance(s, FiniteSet):
            return "{" + ", ".join(str(e) for e in sorted(s, key=lambda x: str(x))) + "}"

        # Fallback
        return str(s)

    except Exception:
        return "No disponible"

def pretty_power(expr: str) -> str:
    # Convierte potencias comunes a superíndices Unicode
    replacements = {
        "**1": "¹",
        "**2": "²",
        "**3": "³",
        "**4": "⁴",
        "**5": "⁵",
        "**6": "⁶",
        "**7": "⁷",
        "**8": "⁸",
        "**9": "⁹",
        "**0": "⁰",
    }
    for k, v in replacements.items():
        expr = expr.replace(k, v)
    return expr
