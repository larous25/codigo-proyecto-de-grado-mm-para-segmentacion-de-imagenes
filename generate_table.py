import pandas as pd
import sys

# Ruta al archivo de resultados
csv_path = 'logs_watershed/csv/benchmark_results.csv'

# Cargar el DataFrame con índice múltiple y encabezado múltiple
df = pd.read_csv(csv_path, header=[0, 1], index_col=[0, 1])

# Algoritmos a considerar
algorithms = ['skimage', 'opencv', 'higra']
resources = ['time', 'memory']

# Unidad para cada métrica
units = {'time': 's', 'memory': 'MB'}

# Diccionario para almacenar resultados
results = []

# Calcular métricas
for algo in algorithms:
    for res in resources:
        values = df[(algo, res)].dropna()
        mean = values.mean()
        std = values.std()
        
        # Agregar media
        results.append((
            f"Tiempo medio ({algo.capitalize()})" if res == 'time' else f"Memoria media ({algo.capitalize()})",
            f"{mean:.5f} {units[res]}"
        ))
        
        # Agregar desviación estándar
        results.append((
            f"Desviación estándar del tiempo ({algo.capitalize()})" if res == 'time'
            else f"Desviación estándar de la memoria ({algo.capitalize()})",
            f"{std:.5f} {units[res]}"
        ))

# Redirigir la salida estándar a un archivo
original_stdout = sys.stdout  # Guardar la salida estándar original
with open('tabla.tex', 'w', encoding='utf-8') as f:
    sys.stdout = f  # Redirigir la salida estándar al archivo
    
    # Imprimir en formato LaTeX
    print("\\begin{tabular} { m{9cm} | m{2cm}  }")
    print("\\textbf{Métrica} & \\textbf{Valor} \\\\")
    print("\\midrule")
    for metric, value in results:
        print(f"{metric} & {value} \\\\")
    print("\\bottomrule")
    print("\\end{tabular}")
    
    sys.stdout = original_stdout  # Restaurar la salida estándar original

# Opcional: Mostrar un mensaje de confirmación
print("La tabla LaTeX se ha guardado en tabla.tex")