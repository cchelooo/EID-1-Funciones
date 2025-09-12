# Interfaz grafica con CustomTkinter
# Responsabilidad: inputs de usuario, invocar analisis, mostrar resultados y dibujar grafico

import os
import customtkinter as ctk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from .analysis import FunctionAnalyzer
from .plotting import build_figure
from .utils import fmt_set, pretty_power
from sympy import pretty


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Analizador de Funciones")
        self.geometry("1000x680")

        # Configurar tema oscuro
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._last = None
        self._current_figure = None  # para guardar la figura actual
        self._build_ui()

    def _build_ui(self):
        # Barra superior
        top = ctk.CTkFrame(self, corner_radius=10)
        top.pack(side="top", fill="x", padx=10, pady=10)

        ctk.CTkLabel(top, text="f(x) =").grid(row=0, column=0, sticky="w")
        self.func_entry = ctk.CTkEntry(top, width=320)
        self.func_entry.grid(row=0, column=1, sticky="we", padx=6)

        ctk.CTkLabel(top, text="x =").grid(row=0, column=2, sticky="w")
        self.x_entry = ctk.CTkEntry(top, width=120)
        self.x_entry.grid(row=0, column=3, sticky="w", padx=6)

        # Boton analizar y graficar
        self.btn_run = ctk.CTkButton(top, text="Analizar y Graficar", command=self.on_run)
        self.btn_run.grid(row=0, column=4, padx=6)

        # Boton guardar captura
        self.btn_capture = ctk.CTkButton(top, text="Guardar Captura", command=self.save_screenshot)
        self.btn_capture.grid(row=0, column=5, padx=6)

        top.grid_columnconfigure(1, weight=1)

        # Panel dividido
        body = ctk.CTkFrame(self)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        # Izquierda: texto resultados
        left = ctk.CTkFrame(body)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.text = ctk.CTkTextbox(left, wrap="word")
        self.text.pack(fill="both", expand=True)
        self.text.configure(state="disabled")

        # Derecha: grafico
        right = ctk.CTkFrame(body)
        right.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.right = right

        # Barra de estado
        self.status = ctk.CTkLabel(self, text="Listo.", anchor="w")
        self.status.pack(side="bottom", fill="x")

    def write(self, content: str):
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", content)
        self.text.configure(state="disabled")

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

        # Mostrar resultados en texto
        lines = []
        lines.append("== RESULTADOS DEL ANALISIS ==\n")

        # Representaciones de la funcion
        lines.append("Funcion ingresada:\n")
        lines.append(f" - Texto: f(x) = {pretty_power(str(analyzer.f))}\n")
        lines.append(f" - Forma matematica:\n{pretty(analyzer.f)}\n")

        # Datos del analisis
        lines.append(f"Dominio: {dom_text}\n")
        lines.append(f"Recorrido (simbolico si es posible): {ran_text}\n")
        lines.append(f"Intersecciones con el eje X: {', '.join(f'{r:.6g}' for r in xints) if xints else '∅'}")
        lines.append(f"Interseccion con el eje Y: {'y=' + str(yint) if yint is not None else '∅'}\n")

        if steps:
            lines.append("== EVALUACION DETALLADA ==\n" + steps + "\n")

        lines.append("== NOTAS ==\n- Si el recorrido simbolico no esta disponible, puede estimarse visualmente en el grafico.\n- El punto evaluado se resalta con un color distinto sin alterar la curva original.")

        self.write("\n".join(lines))

        # Guardar datos
        self._last = dict(analyzer=analyzer, dom=dom, xints=xints, yint=yint, eval_point=eval_point)

        # Dibujar grafico
        fig = build_figure(analyzer.f, dom, xints, yint, eval_point)
        self._current_figure = fig  # guardamos la figura para exportar
        for child in self.right.winfo_children():
            child.destroy()
        canvas = FigureCanvasTkAgg(fig, master=self.right)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        self.status.configure(text="Analisis y grafico completados.")

    def save_screenshot(self):
        if not self._current_figure:
            messagebox.showwarning("Sin grafico", "Primero analice y grafique una funcion.")
            return

        # Asegurar carpeta assets/screenshots
        folder = os.path.join("assets", "screenshots")
        os.makedirs(folder, exist_ok=True)

        # Crear nombre automatico
        existing = [f for f in os.listdir(folder) if f.startswith("screenshot_") and f.endswith(".png")]
        next_num = len(existing) + 1
        filepath = os.path.join(folder, f"screenshot_{next_num}.png")

        # Guardar
        self._current_figure.savefig(filepath, dpi=150)
        self.status.configure(text=f"Captura guardada en {filepath}")
        messagebox.showinfo("Captura guardada", f"Se guardo la grafica en:\n{filepath}")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
