# EID-1-Funciones  
Analizador de funciones matemáticas en Python con interfaz gráfica moderna.  

Este proyecto implementa una aplicación de escritorio que permite:  
- Ingresar una función matemática en `x`.  
- Calcular **dominio, recorrido, intersecciones con los ejes**.  
- Evaluar la función en un punto con **explicación paso a paso**.  
- Generar un **gráfico claro y profesional** con la curva, sus intersecciones y el punto evaluado resaltado.  
- Guardar capturas del gráfico en la carpeta `assets/screenshots/`.  

---

## Instalación y ejecución

1. Clona este repositorio:  
   ```bash
   git clone https://github.com/cchelooo/EID-1-Funciones.git
   cd EID-1-Funciones
   ```

2. Crea un entorno virtual (recomendado):  
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # en Windows
   source .venv/bin/activate   # en Linux/Mac
   ```

3. Instala dependencias:  
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecuta la aplicación:  
   ```bash
   cd src
   python -m function_analyzer.main
   ```

---

## Tecnologías utilizadas
- **Python 3.10+**  
- **CustomTkinter** → interfaz gráfica moderna con modo oscuro  
- **SymPy** → análisis matemático simbólico (dominio, rango, raíces)  
- **Matplotlib** → gráficos sin uso de NumPy  

---

## Estructura del proyecto

```
EID-1-Funciones/
├─ src/
│  └─ function_analyzer/
│     ├─ __init__.py
│     ├─ main.py        # GUI con CustomTkinter
│     ├─ analysis.py    # Lógica matemática (dominio, rango, intersecciones, evaluación paso a paso)
│     ├─ plotting.py    # Gráficos de funciones con Matplotlib
│     └─ utils.py       # Funciones auxiliares (formato de conjuntos, potencias, etc.)
├─ assets/
│  └─ screenshots/      # Carpeta donde se guardan las capturas de los gráficos
├─ requirements.txt     # Dependencias del proyecto
└─ README.md            # Documentación
```

---

## Ejemplos de uso (para más ejemplos revisar examples/demo_inputs)

### Ejemplo 1: cuadrática  
**Entrada**:  
- f(x) = `x^2 - 4`  
- x = `3`  

**Resultados esperados**:  
- Dominio: ℝ  
- Rango: `[ -4 , ∞ )`  
- Intersecciones: `x = -2, 2`, `y = -4`  
- Evaluación paso a paso:  
  ```
  Funcion: f(x) = x² - 4
  Sustitucion: x = 3
  f(3) = 9 - 4
  Valor numerico: 5
  ```

---

### Ejemplo 2: raíz cuadrada  
**Entrada**:  
- f(x) = `sqrt(x-1)`  
- x = `5`  

**Resultados esperados**:  
- Dominio: `[1, ∞)`  
- Rango: `[0, ∞)`  
- Intersección X: `(1, 0)`  
- Evaluación paso a paso:  
  ```
  Funcion: f(x) = √(x - 1)
  Sustitucion: x = 5
  f(5) = √4
  Valor numerico: 2
  ```

---