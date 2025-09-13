# ==== IMPORTS ====
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Interfaz grafica con CustomTkinter
import customtkinter as ctk
from tkinter import messagebox, filedialog

# Matplotlib para graficar dentro de la ventana
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
from matplotlib.figure import Figure 

# SymPy para manejo simbolico de funciones matematicas
from sympy import ( # Simbolos, string, ecuaciones, reales, numeros, conjuntos, intervalos, uniones, vacios, infinito (en orden)
    Symbol, sympify, Eq, Reals, N, FiniteSet, Interval,
    Union, EmptySet, oo
)
from sympy.calculus.util import continuous_domain, function_range
from sympy.sets import Reals as SymReals


# ============================================================
# UTILS 
# ============================================================

# Objeto simple para guardar resultados de operaciones
@dataclass
class EvalResult:
    ok: bool     # True si la operacion es correcta
    message: str # Mensaje de error si la operacion es incorrecta

# Crear resultado correcto
def ok(msg: str) -> EvalResult:
    return EvalResult(True, msg)

# Crear resultado con error
def err(msg: str) -> EvalResult:
    return EvalResult(False, msg)

# Pasar lista de puntos (x, y) a texto
def stringify_points(points: List[Tuple[float, float]]) -> str:
    if not points: # Si no hay puntos, devolver ∅
        return "∅"
    return ", ".join(f"({x:.6g}, {y:.6g})" for x, y in points)

# Formato legible para intervalos, uniones y conjuntos
def fmt_set(s) -> str:
    try:
        if s == EmptySet:
            return "∅"
        if s == Reals or s == SymReals:
            return "ℝ"
        if isinstance(s, Interval):
            a = "-∞" if s.start == -oo else str(s.start)
            b = "∞" if s.end == oo else str(s.end)
            left = "(" if s.left_open else "["
            right = ")" if s.right_open else "]"
            return f"{left}{a}, {b}{right}"
        if isinstance(s, Union): # Si es una union, devolver los elementos ordenados
            return " U ".join(fmt_set(arg) for arg in sorted(s.args, key=lambda x: str(x)))
        if isinstance(s, FiniteSet): # Si es un conjunto finito, devolver los elementos ordenados
            return "{" + ", ".join(str(e) for e in sorted(s, key=lambda x: str(x))) + "}"
        return str(s)
    except Exception:
        return "No disponible"

# Reemplaza **n por superindices Unicode para que se vea mas claro
def pretty_power(expr: str) -> str:
    replacements = {
        "**1": "¹", "**2": "²", "**3": "³",
        "**4": "⁴", "**5": "⁵", "**6": "⁶",
        "**7": "⁷", "**8": "⁸", "**9": "⁹",
        "**0": "⁰",
    }
    for k, v in replacements.items():
        expr = expr.replace(k, v)
    return expr


# ============================================================
# ANALISIS
# ============================================================

# Variable simbolica que se usara en las funciones
x = Symbol("x")

class FunctionAnalyzer:
    # Esta clase analiza funciones matematicas dadas como texto
    def __init__(self, func_str: str):
        func_str = (func_str or "").strip()
        if not func_str:
            raise ValueError("La funcion no puede estar vacia.")
        # sympify convierte el string en expresion matematica
        # convert_xor=True hace que ^ se tome como potencia
        self.f = sympify(func_str, convert_xor=True)
        self.func_str = func_str

    # Dominio de la funcion
    def domain(self):
        try:
            return continuous_domain(self.f, x, Reals)
        except Exception:
            return Reals

    # Recorrido de la funcion (si se puede calcular)
    def range(self, dom=None):
        if dom is None:
            dom = self.domain()
        try:
            return function_range(self.f, x, dom)
        except Exception:
            return None

    # Raices reales de la funcion
    def x_intercepts(self) -> List[float]:
        try:
            from sympy import solveset
            sol = solveset(Eq(self.f, 0), x, domain=Reals)
            roots: List[float] = []
            if isinstance(sol, FiniteSet):
                for r in sol:
                    if r.is_real:
                        roots.append(float(N(r)))
            return sorted(roots)
        except Exception:
            return []

    # Interseccion con eje Y (si existe)
    def y_intercept(self) -> Optional[float]:
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

    # Evaluar funcion en un punto y mostrar pasos
    def evaluate_with_steps(self, x_value_str: str) -> Tuple[bool, str, Optional[float], Optional[float]]:
        try:
            x_val = sympify(x_value_str)
        except Exception:
            return (False, "El valor de x no es valido.", None, None)

        try:
            dom = self.domain()
            if x_val not in dom:
                return (False, f"x = {x_val} no pertenece al dominio {dom}.", None, None)
        except Exception:
            pass

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


# ============================================================
# GRAFICOS
# ============================================================

# Establecer ventana de dibujo segun el dominio
def _infer_window(dom) -> Tuple[float, float]:
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

# Genera puntos para dibujar la funcion
def _sample(expr, dom, n=600) -> Tuple[List[float], List[float]]:
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

# Crea figura de Matplotlib con funcion y puntos clave
def build_figure(expr, dom, xints: List[float], yint: Optional[float], eval_point: Optional[Tuple[float, float]]):
    fig = Figure(figsize=(6.6, 4.2), dpi=100)
    ax = fig.add_subplot(111)

    xs, ys = _sample(expr, dom)
    ax.plot(xs, ys, linewidth=2, label="f(x)")

    # Ejes
    ax.axhline(0, linewidth=1)
    ax.axvline(0, linewidth=1)

    # Raices
    for r in xints:
        ax.plot([r], [0], marker="o", markersize=6, label=None)

    # Corte con Y
    if yint is not None:
        ax.plot([0], [yint], marker="o", markersize=6, label=None)

    # Punto evaluado
    if eval_point is not None:
        ax.plot([eval_point[0]], [eval_point[1]], marker="o", markersize=8, label="Punto evaluado")

    ax.set_title("Grafico de la funcion y sus intersecciones")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    return fig


# ============================================================
# GUI (Interfaz grafica)
# ============================================================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Analizador de Funciones")
        self.geometry("1000x680")

        # Tema oscuro para la vista
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._last = None
        self._current_figure = None
        self._build_ui()

    # Construccion de la interfaz
    def _build_ui(self):
        # Parte superior con entradas y botones
        top = ctk.CTkFrame(self, corner_radius=10)
        top.pack(side="top", fill="x", padx=10, pady=10)

        ctk.CTkLabel(top, text="f(x) =").grid(row=0, column=0, sticky="w")
        self.func_entry = ctk.CTkEntry(top, width=320)
        self.func_entry.grid(row=0, column=1, sticky="we", padx=6)

        ctk.CTkLabel(top, text="x =").grid(row=0, column=2, sticky="w")
        self.x_entry = ctk.CTkEntry(top, width=120)
        self.x_entry.grid(row=0, column=3, sticky="w", padx=6)

        self.btn_run = ctk.CTkButton(top, text="Analizar y Graficar", command=self.on_run)
        self.btn_run.grid(row=0, column=4, padx=6)

        self.btn_capture = ctk.CTkButton(top, text="Guardar Captura", command=self.save_screenshot)
        self.btn_capture.grid(row=0, column=5, padx=6)

        top.grid_columnconfigure(1, weight=1)

        # Cuerpo dividido en resultados y grafico
        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        left = ctk.CTkFrame(body)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.text = ctk.CTkTextbox(left, wrap="word")
        self.text.pack(fill="both", expand=True)
        self.text.configure(state="disabled")

        right = ctk.CTkFrame(body)
        right.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.right = right

        self.status = ctk.CTkLabel(self, text="Listo.", anchor="w")
        self.status.pack(side="bottom", fill="x")

    # Escribir en el panel de resultados
    def write(self, content: str):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", content)
        self.text.configure(state="disabled")

    # Boton principal: analiza y grafica
    def on_run(self):
        expr = self.func_entry.get().strip()
        if not expr:
            messagebox.showerror("Error de entrada", "Ingrese una funcion en x.")
            return

        try:
            analyzer = FunctionAnalyzer(expr)
        except Exception as e:
            messagebox.showerror("Error al interpretar", str(e))
            return

        dom = analyzer.domain()
        dom_text = fmt_set(dom)
        ran = analyzer.range(dom)
        ran_text = fmt_set(ran) if ran is not None else "No disponible (puede estimarse en el grafico)"

        xints = analyzer.x_intercepts()
        yint = analyzer.y_intercept()

        # Evaluar en punto si se ingresa
        xval_str = self.x_entry.get().strip()
        steps = ""
        eval_point = None
        if xval_str: # Si se ingresa un punto, evaluar la funcion en ese punto
            ok, steps, xnum, ynum = analyzer.evaluate_with_steps(xval_str)
            if ok:
                eval_point = (xnum, ynum)

        # Armar salida de texto
        lines = []
        lines.append("== RESULTADOS DEL ANALISIS ==\n")
        lines.append("Funcion ingresada:\n")
        lines.append(f" - f(x) = {pretty_power(str(analyzer.f))}\n")
        lines.append(f"Dominio: {dom_text}\n")
        lines.append(f"Recorrido (simbolico si es posible): {ran_text}\n")
        lines.append(f"Intersecciones con el eje X: {', '.join(f'{r:.6g}' for r in xints) if xints else '∅'}")
        lines.append(f"Interseccion con el eje Y: {'y=' + str(yint) if yint is not None else '∅'}\n")
        if steps:
            lines.append("== EVALUACION DETALLADA ==\n" + steps + "\n")
        lines.append("== NOTAS ==\n- Si el recorrido simbolico no esta disponible, puede estimarse visualmente en el grafico.\n- El punto evaluado se resalta con un color distinto sin alterar la curva original.")
        self.write("\n".join(lines))

        self._last = dict(analyzer=analyzer, dom=dom, xints=xints, yint=yint, eval_point=eval_point)

        # Dibujar grafico
        fig = build_figure(analyzer.f, dom, xints, yint, eval_point)
        self._current_figure = fig

        # Limpiar y mostrar grafico
        for child in self.right.winfo_children():
            child.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.right)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Agregar barra con zoom y pan
        toolbar = NavigationToolbar2Tk(canvas, self.right)
        toolbar.update()
        toolbar.pack(fill="x")

        self.status.configure(text="Analisis y grafico completados.")

    # Boton guardar captura
    def save_screenshot(self):
        if not self._current_figure:
            messagebox.showwarning("Sin grafico", "Primero analice y grafique una funcion.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagen PNG", "*.png"), ("Todos los archivos", "*.*")]
        )
        if not filepath:
            return

        self._current_figure.savefig(filepath, dpi=150)
        self.status.configure(text=f"Captura guardada en {filepath}")
        messagebox.showinfo("Captura guardada", f"Se guardo la grafica en:\n{filepath}")


# ============================================================
# MAIN
# ============================================================

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__": # Si se ejecuta directamente, ejecutar la funcion main
    main()
