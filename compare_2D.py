import os
import cv2
import higra
import argparse
from tools import create_data_frame, Image_2D, update_dataframe


# Argumentos de línea de comandos
parser = argparse.ArgumentParser(description='Comparar tiempo y memoria de segmentación Watershed en imágenes 2D.')
parser.add_argument("--save", help="Guardar los resultados de segmentación.", action='store_true')
parser.add_argument("-d", "--dir", help="Directorio con imágenes.")
parser.add_argument("--resource", help="Recurso a evaluar: 'time' o 'memory'.", required=True)
parser.add_argument("--logs_dir", help="Directorio para guardar resultados.")

args = parser.parse_args()

resource = args.resource
NEED_SAVE = args.save
LOGS_FOLDER = args.logs_dir if args.logs_dir else 'logs_watershed'
IMGS_FOLDER = args.dir if args.dir else 'dest_imgs'

INIT_SIZE = 512
INIT_MIN_DIST = 0

# Cargar lista de imágenes
imgs = os.listdir(IMGS_FOLDER)
imgs = [f for f in imgs if f.endswith('.png')]
imgs.sort(key=lambda x: int(x.split('.', 1)[0].rsplit('_', 1)[1]))

# Distancias mínimas por tipo de imagen
image_init_min_dist = {
    'board': 20,
    'circles': 6,
    'coins': 35,
    'maze': 13,
    'fruits': 15
}
image_need_invert = ['circles', 'coins']

# Algoritmos y recursos
ALGORITHMS = ['skimage', 'opencv', 'higra']

resources = ['time', 'memory']
df = create_data_frame(imgs, ALGORITHMS, resources)

# Procesamiento principal
if __name__ == '__main__':
    # --- Argumentos de línea de comandos ---

    image_files = [f for f in os.listdir(IMGS_FOLDER) if f.endswith('.png')]
    image_files.sort(key=lambda x: int(x.split('.', 1)[0].rsplit('_', 1)[1]))

    if not image_files:
        print(f"No se encontraron imágenes en '{IMGS_FOLDER}'.")
        exit(1)

    # Crear DataFrame de resultados
    results_df = create_data_frame(image_files, ALGORITHMS, ['time', 'memory'])

    # Procesamiento principal
    for filename in image_files:
        print(f"\nProcesando: {filename}")
        try:
            img_instance = Image_2D(folder=IMGS_FOLDER, filename=filename, init_size=INIT_SIZE)

            for algo in ALGORITHMS:
                try:
                    print(f"   Ejecutando {algo} ({resource})...")
                    img_instance.process_ws(ALGO=algo, res_type=resource)
                    print(f"   {algo}: {resource} = {img_instance.result[resource]}")
                    update_dataframe(results_df, img_instance, algo, resource)

                    if NEED_SAVE:
                        log_labels_2d(LOGS_FOLDER, f"{algo}_{img_instance.cluster}_{img_instance.size}", img_instance.labels)

                except Exception as e:
                    print(f"   Error con {algo}: {e}")

        except Exception as e:
            print(f"Error procesando {filename}: {e}")

    # Guardar CSV de resultados
    os.makedirs(os.path.join(LOGS_FOLDER, "csv"), exist_ok=True)
    suffix = "proc_time.csv" if resource == "time" else "proc_mem.csv"
    csv_path = os.path.join(LOGS_FOLDER, "csv", suffix)
    results_df.to_csv(csv_path)
    print(f"\nResultados guardados en: {csv_path}")

