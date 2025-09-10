# Modulo de graficacion con Matplotlib sin usar NumPy
# Objetivo: generar figura con la funcion, ejes, intersecciones y punto evaluado destacado

from typing import List, Tuple, Optional
from sympy import N
from matplotlib.figure import Figure

def _infer_window(dom) -> Tuple[float, float]:
    # Define una ventana de dibujo a partir del dominio.
    # Si el dominio es infinito, recorta por defecto a [-10, 10].

    a, b = -10.0, 10.0
    try:
        if getattr(dom, "is_Interval", False):
            a = float(dom.start) if dom.start.is_finite else -10.0
            b = float(dom.end) if dom.end.is_finite else 10.0
            if a == b:
                b = a + 1.0
    except Exception:
        pass
    return a, b

def _sample(expr, dom, n=600) -> Tuple[List[float], List[float]]:
    # Muestreo manual en listas nativas de Python (sin NumPy).
    # Maneja errores puntuales como discontinuidades con NaN.

    xs: List[float] = []
    ys: List[float] = []
    a, b = _infer_window(dom)
    step = (b - a) / float(n)
    for i in range(n + 1):
        xi = a + i * step
        try:
            yi = N(expr.subs({"x": xi}))
            if yi.is_real:
                xs.append(float(xi))
                ys.append(float(yi))
        except Exception:
            xs.append(float(xi))
            ys.append(float("nan"))
    return xs, ys

def build_figure(expr, dom, xints: List[float], yint: Optional[float], eval_point: Optional[Tuple[float, float]]):
    # Crea y devuelve una Figure con:
    #   - Curva de la funcion
    #   - Ejes X e Y
    #   - Intersecciones con los ejes marcadas
    #   - Punto evaluado en color distinto
    
    fig = Figure(figsize=(6.6, 4.2), dpi=100)
    ax = fig.add_subplot(111)

    xs, ys = _sample(expr, dom)
    ax.plot(xs, ys, linewidth=2, label="f(x)")

    # Ejes cartesianos
    ax.axhline(0, linewidth=1)
    ax.axvline(0, linewidth=1)

    # Intersecciones con X
    for r in xints:
        ax.plot([r], [0], marker="o", markersize=6, label=None)

    # Interseccion con Y
    if yint is not None:
        ax.plot([0], [yint], marker="o", markersize=6, label=None)

    # Punto evaluado (Matplotlib asigna color distinto por defecto)
    if eval_point is not None:
        ax.plot([eval_point[0]], [eval_point[1]], marker="o", markersize=8, label="Punto evaluado")

    # Textos visibles en espanol
    ax.set_title("Grafico de la funcion y sus intersecciones")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    return fig
