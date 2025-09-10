# Interfaz grafica con Tkinter
# Responsabilidad: inputs de usuario, invocar analisis, mostrar resultados y dibujar grafico

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .analysis import FunctionAnalyzer
from .plotting import build_figure
from .utils import fmt_set

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizador de Funciones")
        self.geometry("1000x680")
        self._build_ui()
        self._last = None  # cache: ultimo analisis para reusar en grafico

    def _build_ui(self):
        # Barra superior con entradas y botones
        top = ttk.Frame(self, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top, text="f(x) =").grid(row=0, column=0, sticky="w")
        self.func_entry = ttk.Entry(top, width=56)
        self.func_entry.grid(row=0, column=1, sticky="we", padx=6)

        ttk.Label(top, text="x =").grid(row=0, column=2, sticky="w")
        self.x_entry = ttk.Entry(top, width=18)
        self.x_entry.grid(row=0, column=3, sticky="w", padx=6)

        self.btn_analyze = ttk.Button(top, text="Analizar", command=self.on_analyze)
        self.btn_analyze.grid(row=0, column=4, padx=4)

        self.btn_plot = ttk.Button(top, text="Graficar", command=self.on_plot)
        self.btn_plot.grid(row=0, column=5, padx=4)

        top.columnconfigure(1, weight=1)

        # Panel dividido: izquierda texto, derecha grafico
        body = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        body.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # Izquierda: resultados en texto
        left = ttk.Frame(body)
        body.add(left, weight=1)
        self.text = tk.Text(left, wrap="word")
        self.text.pack(fill=tk.BOTH, expand=True)
        self.text.configure(state="disabled")

        # Derecha: canvas del grafico
        right = ttk.Frame(body)
        body.add(right, weight=1)
        self.right = right

        # Barra de estado
        self.status = ttk.Label(self, text="Listo.", anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def write(self, content: str):
        # Utilidad: actualizar el panel de resultados
        self.text.configure(state="normal")
        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, content)
        self.text.configure(state="disabled")

    def on_analyze(self):
        # Handler: boton Analizar
        expr = self.func_entry.get().strip()
        if not expr:
            messagebox.showerror("Error de entrada", "Ingrese una funcion en x.")
            return

        try:
            analyzer = FunctionAnalyzer(expr)
        except Exception as e:
            messagebox.showerror("Error al interpretar", str(e))
            return

        # Dominio y recorrido
        dom = analyzer.domain()
        dom_text = fmt_set(dom)
        ran = analyzer.range(dom)
        ran_text = fmt_set(ran) if ran is not None else "No disponible (puede estimarse en el grafico)"

        # Intersecciones
        xints = analyzer.x_intercepts()
        yint = analyzer.y_intercept()

        # Evaluacion opcional
        xval_str = self.x_entry.get().strip()
        steps = ""
        eval_point = None
        if xval_str:
            ok, steps, xnum, ynum = analyzer.evaluate_with_steps(xval_str)
            if ok:
                eval_point = (xnum, ynum)

        # Armar reporte en espanol
        lines = []
        lines.append("== RESULTADOS DEL ANALISIS ==\n")
        lines.append(f"Funcion ingresada: f(x) = {analyzer.f}\n")
        lines.append(f"Dominio: {dom_text}\n")
        lines.append(f"Recorrido (simbolico si es posible): {ran_text}\n")
        lines.append(f"Intersecciones con el eje X: {', '.join(f'{r:.6g}' for r in xints) if xints else '∅'}")
        lines.append(f"Interseccion con el eje Y: {'y=' + str(yint) if yint is not None else '∅'}\n")
        if steps:
            lines.append("== EVALUACION DETALLADA ==\n" + steps + "\n")
        lines.append("== NOTAS ==\n- Si el recorrido simbolico no esta disponible, puede estimarse visualmente en el grafico.\n- El punto evaluado se resalta con un color distinto sin alterar la curva original.")
        self.write("\n".join(lines))

        # Guardar datos para graficar sin recalcular
        self._last = dict(analyzer=analyzer, dom=dom, xints=xints, yint=yint, eval_point=eval_point)
        self.status.config(text="Analisis completado.")

    def on_plot(self):
        # Handler: boton Graficar
        if not self._last:
            # Si el usuario no analizo aun, intentamos analizar
            self.on_analyze()
            if not self._last:
                return
        data = self._last
        fig = build_figure(
            data["analyzer"].f,
            data["dom"],
            data["xints"],
            data["yint"],
            data["eval_point"]
        )
        # Limpiar canvas anterior y dibujar el nuevo
        for child in self.right.winfo_children():
            child.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.right)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.status.config(text="Grafico actualizado.")

def main():
    # Punto de entrada del modulo
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
