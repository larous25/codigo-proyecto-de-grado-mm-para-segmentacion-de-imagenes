# Comparación de implementaciones de algoritmos computacionales de morfología matemática (Watershed)

Este proyecto es una modificación del repositorio original [Computational resources comparison of watershed algorithm implementations](https://github.com/ant-Korn/Comparing_watersheds/tree/master/2018), desarrollado como apoyo al artículo:

> Kornilov AS, Safonov IV. *An Overview of Watershed Algorithm Implementations in Open Source Libraries*. Journal of Imaging. 2018; 4(10):123.  
> https://doi.org/10.3390/jimaging4100123

El presente trabajo consiste en un conjunto de scripts que permite comparar el tiempo de ejecución y el uso máximo de memoria de algunas implementaciones del algoritmo *watershed*, disponibles en las siguientes bibliotecas:

- [OpenCV](https://github.com/opencv/opencv "Open Source Computer Vision Library")
- [Scikit-image](https://github.com/scikit-image/scikit-image "scikit-image")
- [Higra](https://github.com/higra/Higra "Hierarchical Graph Analysis")

---

## Requisitos previos

Para ejecutar los scripts, es necesario instalar [ImageMagick](https://github.com/ImageMagick/ImageMagick), que permite escalar las imágenes iniciales durante la generación de las series de prueba.

También se requiere tener Python (versión ≥ 3.6) y las bibliotecas mencionadas anteriormente. Para instalar todas las dependencias necesarias, puedes utilizar:

```bash
pip install -r requirements.txt
````

---

## Compatibilidad con Windows

Dado que la mayoría de los scripts están diseñados para ejecutarse en entornos Windows, se ha incluido un archivo `.bat` que permite lanzar los experimentos sin necesidad de utilizar un entorno tipo UNIX ni herramientas como `make`.

Esta adaptación facilita la ejecución de las pruebas en sistemas operativos Windows, respetando la lógica del proyecto original.

---

## Uso con Makefile (opcional)

El archivo [`Makefile`](./Makefile) ofrece una serie de comandos predefinidos para facilitar el uso del proyecto:

```make
make init               # Crear la estructura de directorios y las imágenes de prueba
make compare_2D     # Comparar tiempo de ejecución y memoria máxima para el caso 2D

make gen_imgs           # Generar una serie de imágenes 2D de prueba a partir de las imágenes en $(SOURCE_FOLDER)

make plot_all           # Generar gráficos basados en todas las comparaciones
make plots_time         # Generar gráficos de comparación de tiempo
make plots_mem          # Generar gráficos de comparación de memoria

make clean              # Limpiar todos los archivos generados
make clean_2D           # Eliminar las imágenes generadas para el caso 2D
```


