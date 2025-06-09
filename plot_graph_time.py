import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from collections import OrderedDict

# Estilos
plt.style.use('seaborn-v0_8')
plt.rcParams.update({
    "font.size": 14,
    "legend.fontsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "text.usetex": False,
    "font.family": "serif"
})

# Títulos para gráficas
titles = {'opencv': 'OpenCV', 'skimage': 'Scikit-image', 'higra': 'Higra'}

# Argumentos de línea de comandos
parser = argparse.ArgumentParser(description='Generar gráficos de benchmark Watershed.')
parser.add_argument("-lg", "--logarifmic", help="Escala logarítmica en eje Y.", action='store_true')
parser.add_argument("-d", "--dimensions", help="Número de dimensiones (2D por defecto).", type=int, default=2)
args = parser.parse_args()

LOGARIFMIC = args.logarifmic
D = args.dimensions

# Tamaños usados en imágenes (ajusta si necesitas otros)
needed_sizes = [512, 1861, 2581]

def main():
    os.makedirs('plots', exist_ok=True)
    input_file = "logs_watershed/benchmark_results.csv"

    try:
        df = pd.read_csv(input_file, header=[0, 1], index_col=[0, 1])
        print(f"Datos cargados correctamente desde: {input_file}")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {input_file}")
        print("Ejecuta primero el script de benchmark para generarlo.")
        return

    # Bibliotecas presentes en el archivo
    level0 = [item[0] for item in df.columns.values if item[0] in titles]
    level0 = list(OrderedDict.fromkeys(level0))
    level1 = list({item[1] for item in df.columns.values})
    titles_l0 = [titles[lib] for lib in level0]

    # Clusters disponibles
    clusters = list(OrderedDict.fromkeys(df.index.get_level_values(0)))
    print("Clusters encontrados:", clusters)
    print("Bibliotecas:", level0)
    print("Métricas:", level1)

    for cluster in clusters:
        plt.figure(figsize=(10, 6))
        ax = plt.gca()

        for lib in level0:
            try:
                table = df.loc[(cluster, slice(None)), (lib, slice(None))].droplevel(0, axis=0)
                table.columns = table.columns.droplevel(0)
                sizes = table.index.values
                table['size'] = table.index ** 2
                table.plot(x='size', y='time', style='--', marker='.', grid=True,
                           ax=ax, logy=LOGARIFMIC, label=titles[lib])
            except Exception as e:
                print(f"Error al graficar {lib} en {cluster}: {e}")

        ticks = tuple(zip(*[(sz * sz, f"{sz}x{sz}") for sz in sizes if sz in needed_sizes]))
        if ticks:
            plt.xticks(ticks[0], ticks[1])

        ax.set_xlabel('Tamaño de imagen (px²)')
        time_unit = ', s (escala log)' if LOGARIFMIC else ', s'
        ax.set_ylabel(f'Tiempo de procesamiento{time_unit}')
        ax.set_title(cluster.capitalize())
        ax.legend()

        output_file = f"plots/{cluster}.pdf"
        plt.savefig(output_file, bbox_inches='tight')
        print(f"Gráfico guardado en: {output_file}")
        plt.close()

if __name__ == "__main__":
    main()
