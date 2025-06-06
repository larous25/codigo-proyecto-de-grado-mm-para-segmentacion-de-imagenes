import os
import cv2
import numpy as np
import pandas as pd
import time
import higra as hg
import imageio 

# try:
#     from utils import * # imshow, locate_resource, get_sed_model_file
# except: # we are probably running from the cloud, try to fetch utils functions from URL
#     import urllib.request as request; exec(request.urlopen('https://github.com/higra/Higra-Notebooks/raw/master/utils.py').read(), globals())
    
from memory_profiler import memory_usage
from scipy import ndimage as ndi

# Imports específicos para Scikit-image
from skimage.morphology import disk
from skimage.segmentation import watershed
from skimage.filters import rank, sobel
from skimage.util import img_as_ubyte
from skimage.feature import peak_local_max
from skimage import img_as_float


# ====================================================================
# SECCIÓN 1: FUNCIONES DE MEDICIÓN Y DECORADORES
# ====================================================================

def decorator(funk_ws, res_type):
    """
    Decorador que mide el tiempo de ejecución o el uso de memoria de una función.
    
    Args:
        funk_ws (function): La función a medir (ej. _opencv_ws).
        res_type (str): 'time' para medir tiempo, 'memory' para medir memoria.

    Returns:
        function: La función 'wrapper' que ejecuta la medición.
    """
    def return_funk(*args, **kwargs):
        if res_type == 'time':
            start_t = time.perf_counter()
            labels = funk_ws(*args, **kwargs)
            process_time = (time.perf_counter() - start_t) 
            return (labels, process_time)
        
        elif res_type == 'memory':
            # memory_usage necesita la función y sus argumentos por separado
            # El resultado de la función se pierde, por eso devolvemos las etiquetas por separado
            labels = None 
            mem_usage = memory_usage((funk_ws, args, kwargs), interval=0.01, max_usage=True)
            # El resultado de la función se captura para no perderlo
            labels = funk_ws(*args, **kwargs)
            return (labels, mem_usage)
        
        else:
            # Si el tipo no es válido, solo ejecuta la función
            labels = funk_ws(*args, **kwargs)
            return (labels, 0.0)
            
    return return_funk


# ====================================================================
# SECCIÓN 2: CLASE PRINCIPAL DEL PROCESAMIENTO DE IMÁGENES
# ====================================================================

class Image_2D:
    """
    Clase para encapsular una imagen 2D y sus operaciones de segmentación.
    """
    def __init__(self, folder, filename, init_size=0):
        self.folder, self.filename = folder, filename
        self.init_size = init_size
        
        # --- Lógica de parsing de nombre de archivo (más robusta) ---
        try:
            name_part = filename.split('.', 1)[0]
            parts = name_part.rsplit('_', 1)
            self.cluster, size_str = parts
            self.size = int(size_str)
            self.mul_size = self.size / init_size if init_size > 0 else 1.0
        except (IndexError, ValueError):
            self.cluster = filename.split('.')[0]
            self.size = 0
            self.mul_size = 1.0

        # --- Carga y preprocesamiento de la imagen ---
        image_path = os.path.join(folder, filename)
        self.img = cv2.imread(image_path)
        # self.img2 = imageio.imread(image_path)
        if self.img is None:
            raise FileNotFoundError(f"No se pudo cargar la imagen: {os.path.join(folder, filename)}")
        self.img_gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.labels = np.zeros(self.img_gray.shape, dtype=np.int32)
        self.result = {'time': 0.0, 'memory': 0.0}

    def process_ws(self, ALGO, res_type='time'):
        """
        Método principal que elige y ejecuta el algoritmo de Watershed.
        """
        if ALGO == 'skimage':
            self.result[res_type] = self.skimage_ws(res_type)
        elif ALGO == 'opencv':
            self.result[res_type] = self.opencv_ws(res_type)
        elif ALGO == 'higra':
            self.result[res_type] = self.higra_ws(res_type)

    # --- Implementación de Scikit-image ---
    def _skimage_ws(self):
        image = self.img_gray
        denoised = rank.median(image, disk(2))
        markers = rank.gradient(denoised, disk(5)) < 10
        markers = ndi.label(markers)[0]
        gradient = rank.gradient(denoised, disk(2))
        return watershed(gradient, markers, watershed_line=True)

    def skimage_ws(self, res_type):
        labels, res = decorator(Image_2D._skimage_ws, res_type)(self)
        if labels is not None: self.labels = labels
        return res

    # --- Implementación de OpenCV ---
    def _opencv_ws(self):
        img_gray = self.img_gray
        ret, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        unknown = cv2.subtract(sure_bg, sure_fg)
        ret, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1
        markers[unknown == 255] = 0
        return cv2.watershed(self.img, markers)

    def opencv_ws(self, res_type):
        labels, res = decorator(Image_2D._opencv_ws, res_type)(self)
        if labels is not None: self.labels = labels
        return res
    
    def _higra_ws(self):
        """Watershed jerárquico usando Higra."""
        
        image = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
       
        if image.ndim == 3:
            image = np.mean(image, axis=2) 
        
        size = image.shape[:2]
        # Detección de bordes estructurados (requiere OpenCV contrib)
        # detector = cv2.ximgproc.createStructuredEdgeDetection(get_sed_model_file())
        # gradient_image = detector.detectEdges(image)
        gradient_image = sobel(image)

        # Construcción del grafo y jerarquía
        graph = hg.get_4_adjacency_graph(size)
        edge_weights = hg.weight_graph(graph, gradient_image, hg.WeightFunction.mean)
        tree, altitudes = hg.watershed_hierarchy_by_area(graph, edge_weights)

        # Obtener segmentación (saliencia)
        labels = hg.labelisation_horizontal_cut_from_threshold(tree, altitudes, threshold=0.5)
        return labels.reshape(size)


    def higra_ws(self, res_type):
        labels, res = decorator(Image_2D._higra_ws, res_type)(self)
        if labels is not None: self.labels = labels
        return res

# ====================================================================
# SECCIÓN 3: FUNCIONES DE LOGGING Y MANEJO DE DATOS
# ====================================================================

def get_spaced_colors(n):
    """Genera una paleta de colores distinguibles para visualización."""
    if n < 10: n = 10
    max_value = 16777215  # 256**3 - 1
    interval = int(max_value / n)
    hex_colors = [hex(i)[2:].zfill(6) for i in range(0, max_value, interval)]
    palette = np.array([(int(c[:2], 16), int(c[2:4], 16), int(c[4:], 16)) for c in hex_colors], dtype=np.uint8)
    np.random.shuffle(palette)
    # Aseguramos que el color para la etiqueta 0 (fondo/líneas) sea negro.
    palette[0] = [0, 0, 0]
    return palette[:n]

def log_labels_2d(logfoldername, logname, i2d):
    """Guarda una imagen de etiquetas 2D como una imagen a color para visualización."""
    os.makedirs(logfoldername, exist_ok=True)
    fname = os.path.join(logfoldername, logname + ".png")
    nlabels = np.max(i2d) + 1
    palette = get_spaced_colors(nlabels)
    # OpenCV espera BGR, no RGB, así que invertimos los canales.
    rgb_slice = palette[i2d.astype(np.int_)]
    bgr_slice = rgb_slice[..., ::-1]
    cv2.imwrite(fname, bgr_slice)

def create_data_frame(image_files, algorithms, resources):
    """
    Crea un DataFrame de pandas para almacenar los resultados del benchmark.
    Versión refactorizada y más legible.
    """
    # Extraer información de los nombres de archivo
    img_info = []
    for f in image_files:
        try:
            name_part = f.split('.', 1)[0]
            cluster, size_str = name_part.rsplit('_', 1)
            img_info.append({'img_name': cluster, 'size': int(size_str)})
        except (ValueError, IndexError):
            print(f"Omitiendo archivo con formato de nombre no esperado: {f}")

    # Crear el DataFrame base
    df = pd.DataFrame(img_info)
    df = df.drop_duplicates().set_index(['img_name', 'size'])

    # Crear MultiIndex para las columnas (ALGO, resource)
    header = pd.MultiIndex.from_product([algorithms, resources], names=['algorithm', 'resource'])
    
    # Crear un DataFrame de resultados con el MultiIndex y rellenarlo con NaN
    results_df = pd.DataFrame(columns=header, index=df.index)
    
    return results_df.sort_index()


def update_dataframe(df, img, algo, resource):
    """Actualiza una celda específica en el DataFrame de resultados."""
    value = img.result[resource]
    df.loc[(img.cluster, img.size), (algo, resource)] = value


# ====================================================================
# SECCIÓN 4: FUNCIONES UTILITARIAS Y OBSOLETAS
# ====================================================================

# Esta función es una alternativa para generar marcadores, no usada por los flujos principales.
def label_2d_cv_2(img, min_dist, need_invert=False):
    """Genera marcadores usando picos locales en la transformada de distancia."""
    thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    if need_invert:
        thresh = 255 - thresh
    D = ndi.distance_transform_edt(thresh)
    
    localMax = peak_local_max(
        D, 
        min_distance=min_dist,
        footprint=np.ones((3, 3)),
        labels=thresh
    )
    
    markers = ndi.label(localMax, structure=np.ones((3, 3)))[0]
    return (thresh, D, markers)

# --- Funciones comentadas ---
# Estas funciones parecen ser de una librería diferente (no OpenCV) y no son compatibles.
# def getArrayFromImage(imIn, size): ...
# def fillImageWithArray(array, imOut): ...


# ====================================================================
# SECCIÓN 5: BLOQUE PRINCIPAL DE EJECUCIÓN
# ====================================================================

if __name__ == '__main__':
    # --- Configuración con rutas relativas (misma carpeta que el script) ---
    INPUT_FOLDER = 'dest_imgs2'          # Carpeta con imágenes a procesar
    LOGS_FOLDER = 'logs_watershed'      # Carpeta para resultados (se creará automáticamente)
    SOURCE_FOLDER = 'source_imgs'       # Carpeta fuente (si se usa)
    SIZES_FILE = 'sizes.txt'            # Archivo con tamaños (si se usa)

    ALGORITHMS = ['skimage', 'opencv', 'higra']  # Algoritmos a comparar
    RESOURCES_TO_MEASURE = ['time', 'memory']

    # --- Comprobación de la carpeta de entrada ---
    if not os.path.isdir(INPUT_FOLDER) or INPUT_FOLDER == "ruta/a/tus/imagenes":
        print(f"Error: La carpeta de entrada '{INPUT_FOLDER}' no existe o no se ha configurado.")
        print("Por favor, edita el script y cambia la variable INPUT_FOLDER.")
    else:
        # --- Recopilar imágenes y crear el DataFrame ---
        image_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(('.png', '.jpg', '.tif'))]
        
        if not image_files:
            print(f"No se encontraron imágenes en '{INPUT_FOLDER}'.")
        else:
            print(f"Encontradas {len(image_files)} imágenes. Creando DataFrame...")
            results_df = create_data_frame(image_files, ALGORITHMS, RESOURCES_TO_MEASURE)
            print("DataFrame creado. Iniciando procesamiento...")

            # --- Bucle principal de procesamiento ---
            for filename in image_files:
                print(f"\n--- Procesando: {filename} ---")
                try:
                    img_instance = Image_2D(folder=INPUT_FOLDER, filename=filename)
                    
                    for algo in ALGORITHMS:
                        for resource in RESOURCES_TO_MEASURE:
                            print(f"Ejecutando '{algo}' midiendo '{resource}'...")
                            img_instance.process_ws(ALGO=algo, res_type=resource)
                            update_dataframe(results_df, img_instance, algo, resource)
                    
                    # Guardar una imagen de ejemplo del último resultado
                    log_labels_2d(LOGS_FOLDER, f"result_{img_instance.cluster}_{img_instance.size}", img_instance.labels)

                except (FileNotFoundError, Exception) as e:
                    print(f"Error procesando {filename}: {e}")

            # --- Mostrar y guardar resultados ---
            print("\n\n--- Resultados Finales ---")
            print(results_df)
            
            # Guardar el DataFrame en un archivo CSV
            results_csv_path = os.path.join(LOGS_FOLDER, "benchmark_results.csv")
            results_df.to_csv(results_csv_path)
            print(f"\nResultados guardados en: {results_csv_path}")
