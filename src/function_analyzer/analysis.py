# Capa de analisis simbolico con SymPy
# Objetivo: dado un string de funcion en x, calcular dominio, recorrido, intersecciones y evaluacion paso a paso

from typing import Optional, List, Tuple
from sympy import (
    Symbol, sympify, S, solveset, Eq, Reals, N, FiniteSet
)
from sympy.calculus.util import continuous_domain, function_range

# Variable simbolica unica admitida por la app
x = Symbol("x")

class FunctionAnalyzer:
    # Recibe un string como 'x**2-4', 'sin(x)/x', 'sqrt(x-1)' y expone:
    #   - domain()
    #   - range()
    #   - x_intercepts()
    #   - y_intercept()
    #   - evaluate_with_steps(x_value_str)

    def __init__(self, func_str: str):
        # Validar entrada basica
        func_str = (func_str or "").strip()
        if not func_str:
            raise ValueError("La funcion no puede estar vacia.")
        # sympify parsea de forma segura y soporta funciones clasicas de SymPy
        # convert_xor=True permite que ^ se interprete como ** si el usuario lo ingresa
        self.f = sympify(func_str, convert_xor=True)
        self.func_str = func_str

    # ---- Dominio ----
    def domain(self):
        # Dominio donde la funcion es continua sobre los reales
        try:
            dom = continuous_domain(self.f, x, Reals)
            return dom
        except Exception:
            # Fallback conservador si algo falla
            return Reals

    # ---- Recorrido ----
    def range(self, dom=None):
        # Intentar calcular el recorrido real usando function_range
        if dom is None:
            dom = self.domain()
        try:
            return function_range(self.f, x, dom)
        except Exception:
            # Puede fallar en funciones complejas; la GUI mostrara un mensaje amigable
            return None

    # ---- Intersecciones ----
    def x_intercepts(self) -> List[float]:
        # Raices reales de f(x) = 0 si el resultado es un conjunto finito.
        # Para casos no finitos (p. ej. infinitas raices), se omite por simplicidad en esta version.

        try:
            sol = solveset(Eq(self.f, 0), x, domain=Reals)
            roots: List[float] = []
            if isinstance(sol, FiniteSet):
                for r in sol:
                    if r.is_real:
                        roots.append(float(N(r)))
            return sorted(roots)
        except Exception:
            return []

    def y_intercept(self) -> Optional[float]:
        # Interseccion con eje Y: f(0) solo si 0 pertenece al dominio.

        try:
            dom = self.domain()
            if 0 in dom:
                val = self.f.subs(x, 0)
                valN = N(val)
                if valN.is_real:
                    return float(valN)
        except Exception:
            pass
        return None

    # ---- Evaluacion con pasos ----
    def evaluate_with_steps(self, x_value_str: str) -> Tuple[bool, str, Optional[float], Optional[float]]:
        # Devuelve (ok, texto_pasos, x_val, y_val).
        # - ok: True si toda la evaluacion es valida
        # - texto_pasos: detalle paso a paso en espanol
        # - x_val, y_val: floats si aplica
        
        # Parsear el valor ingresado para x
        try:
            x_val = sympify(x_value_str)
        except Exception:
            return (False, "El valor de x no es valido.", None, None)

        # Verificar que x_val pertenece al dominio
        try:
            dom = self.domain()
            if x_val not in dom:
                return (False, f"x = {x_val} no pertenece al dominio {dom}.", None, None)
        except Exception:
            # Si falla la pertenencia, seguimos con evaluacion y capturamos cualquier excepcion mas abajo
            pass

        # Armar el texto paso a paso
        steps = [
            f"Funcion: f(x) = {self.f}",
            f"Sustitucion: x = {x_val}",
        ]
        try:
            expr = self.f.subs(x, x_val)
            steps.append(f"f({x_val}) = {expr}")
            val = N(expr)
            steps.append(f"Valor numerico: {val}")
            return (True, "\n".join(steps), float(N(x_val)), float(N(val)))
        except Exception as e:
            return (False, f"Error al evaluar: {e}", None, None)
