import pandas as pd
import matplotlib.pyplot as plt
from collections import OrderedDict
import argparse
import os

# Estilo y fuentes
plt.style.use('seaborn-v0_8')
plt.rcParams.update({
    "font.size": 14,
    "legend.fontsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "text.usetex": False,
    "font.family": "serif"
})

# Títulos para bibliotecas
titles = {'opencv': 'OpenCV', 'skimage': 'Scikit-image', 'higra': 'Higra'}

# Argumentos
parser = argparse.ArgumentParser(description='Graficar uso de memoria de algoritmos de Watershed.')
parser.add_argument("-lg", "--logarithmic", help="Escala logarítmica en eje Y.", action='store_true')
args = parser.parse_args()

LOGARITHMIC = args.logarithmic

# Tamaños esperados
needed_sizes = [512, 1861, 2581]

def main():
    os.makedirs('plots', exist_ok=True)

    input_file = "logs_watershed/benchmark_results.csv"
    try:
        df = pd.read_csv(input_file, header=[0, 1], index_col=[0, 1])
        print(f"Datos cargados desde: {input_file}")
    except FileNotFoundError:
        print(f"ERROR: No se encontró {input_file}. Ejecuta el script principal primero.")
        return

    level0 = [item[0] for item in df.columns.values if item[0] in titles]
    level0 = list(OrderedDict.fromkeys(level0))
    titles_l0 = [titles[lib] for lib in level0]

    clusters = list(OrderedDict.fromkeys(df.index.get_level_values(0)))
    print("Clusters encontrados:", clusters)
    print("Bibliotecas:", level0)

    for cluster in clusters:
        plt.figure(figsize=(10, 6))
        ax = plt.gca()

        for lib in level0:
            try:
                table = df.loc[(cluster, slice(None)), (lib, slice(None))].droplevel(0, axis=0)
                table.columns = table.columns.droplevel(0)
                sizes = table.index.values
                ticks = tuple(zip(*[(sz * sz, f"{sz}x{sz}") for sz in sizes if sz in needed_sizes]))
                table['size'] = table.index ** 2
                table.plot(x='size', y='memory', style='--', marker='o', grid=True,
                           ax=ax, logy=LOGARITHMIC, label=titles[lib])
            except Exception as e:
                print(f"Error al graficar {lib} en {cluster}: {e}")

        ax.set_xlabel('Tamaño de imagen (px²)')
        memory_unit = 'MiB (escala log)' if LOGARITHMIC else 'MiB'
        ax.set_ylabel(f'Memoria máxima usada ({memory_unit})')

        if ticks:
            plt.xticks(ticks[0], ticks[1])

        ax.set_title(f"{cluster.capitalize()}")
        ax.legend()

        output_file = f"plots/{cluster}_memory.pdf"
        plt.savefig(output_file, bbox_inches='tight')
        print(f"Gráfico guardado en: {output_file}")
        plt.close()

if __name__ == "__main__":
    main()
