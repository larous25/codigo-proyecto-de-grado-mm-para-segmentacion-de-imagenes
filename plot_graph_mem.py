import pandas as pd
import matplotlib.pyplot as plt
import seaborn
from matplotlib import rc
from collections import OrderedDict
import argparse
import os

# Configuración de estilos y tipografía
plt.style.use('seaborn-v0_8')
plt.rcParams['font.size'] = 14
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "text.latex.preamble": r"""
        \usepackage[utf8]{inputenc}
        \usepackage[english]{babel}
    """
})

# Diccionario de títulos para las bibliotecas
titles = {'opencv': 'OpenCV', 'skimage': 'Scikit-image', 'higra': 'Higra'}

# Configuración de argumentos de línea de comandos
parser = argparse.ArgumentParser(description='Generar gráficos de consumo de memoria.')
parser.add_argument("-lg", "--logarithmic", help="Escala logarítmica.", action='store_true')
parser.add_argument("-wl", "--watershed_lines", help="Incluir líneas de watershed.", action='store_true')
parser.add_argument("-d", "--dimensions", help="Número de dimensiones de la imagen.", type=int, default=2)
args = parser.parse_args()

LOGARITHMIC = args.logarithmic
WITH_WL = args.watershed_lines
D = args.dimensions

if WITH_WL:
    str_wl = ' (con líneas de watershed)'
else: 
    str_wl = ' (sin líneas de watershed)'

# Tamaños necesarios para imágenes 2D
if D == 2:
    needed_sizes = [512, 1861, 2581]

if __name__ == "__main__":
    # Asegurar que existen las carpetas necesarias
    os.makedirs('plots', exist_ok=True)
    
    # Cargar los datos del benchmark
    input_file = "logs_watershed/benchmark_results.csv"
    try:
        df = pd.read_csv(input_file, header=[0,1], index_col=[0,1])
        print(f"Datos cargados correctamente desde: {input_file}")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {input_file}")
        print("Ejecuta primero el script watershed_benchmark.py para generar los datos")
        exit(1)

    # Para level0 (nombres de bibliotecas)
    level0 = [item[0] for item in df.columns.values if item[0] in titles]
    level0 = list(OrderedDict.fromkeys(level0))  # Eliminar duplicados manteniendo orden

    # Para level1 (tipos de métricas)
    level1 = list({item[1] for item in df.columns.values})
    
    # Filtrar bibliotecas según parámetros
    if not WITH_WL:
        level0 = [lib for lib in level0 if lib != 'opencv']
    
    level1 = list({item[1] for item in df.columns.get_values()})
    
    # Reordenar si es necesario
    if WITH_WL and D == 2:
        if 'higra' in level0 and level0.index('higra') == 3:
            level0.append(level0.pop(3))
    
    titles_l0 = [titles[lib] for lib in level0]
    
    # Obtener clusters únicos
    clusters = list(OrderedDict.fromkeys(df.index.get_level_values(0)))
    print("Clusters encontrados:", clusters)
    print("Bibliotecas:", level0)
    print("Métricas:", level1)

    # Generar gráficos para cada cluster
    for cluster in clusters:
        plt.figure(figsize=(10, 6))
        ax = plt.gca()
        
        for lib in level0:
            # Seleccionar datos para este cluster y biblioteca
            table = df.loc[(cluster, slice(None)), (lib, slice(None))].droplevel(0, axis=0)
            table.columns = table.columns.droplevel(0)
            
            # Preprocesamiento para gráficos 2D
            if D == 2:
                sizes = table.index.values
                ticks = tuple(zip(*[(sz*sz, f"{sz}x{sz}") for sz in sizes if sz in needed_sizes]))
                table['size'] = table.index ** 2
                table.plot(x='size', y='memory', style='--', marker='.', grid=True, 
                          ax=ax, logy=LOGARITHMIC, label=titles[lib])
        
        # Configuración del gráfico
        ax.legend(titles_l0)
        
        if D == 2:
            ax.set_xlabel('Tamaño de imagen (píxeles)')
            if 'ticks' in locals():
                plt.xticks(ticks[0], ticks[1])
        
        memory_unit = 'MiB (escala logarítmica)' if LOGARITHMIC else 'MiB'
        ax.set_ylabel(f'Memoria máxima usada ({memory_unit})')
        
        # Ajustar título
        display_name = 'cells' if cluster == 'circles' else cluster
        title_plot = display_name.capitalize() + str_wl
        ax.set_title(title_plot)
        
        # Guardar el gráfico
        output_suffix = '_WL' if WITH_WL else ''
        output_file = f"plots/{cluster}_memory{output_suffix}.pdf"
        plt.savefig(output_file, bbox_inches='tight')
        print(f"Gráfico guardado en: {output_file}")
        plt.close()