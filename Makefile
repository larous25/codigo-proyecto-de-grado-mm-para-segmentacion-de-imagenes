IMG_FOLDER = dest_imgs2
SOURCE_FOLDER = source_imgs
SIZES_FILE = sizes.txt
LOGS_FOLDER = logs_watershed
PLOTS_FOLDER = plots

# Inicialización: borra todo, crea carpetas y genera imágenes
init: clean $(IMG_FOLDER) $(LOGS_FOLDER) $(PLOTS_FOLDER) gen_imgs

# Comparación 
compare_2D: compare_2D_time compare_2D_mem

# Crear carpetas si no existen
$(IMG_FOLDER):
	if not exist $(IMG_FOLDER) mkdir $(IMG_FOLDER)

$(PLOTS_FOLDER):
	if not exist $(PLOTS_FOLDER) mkdir $(PLOTS_FOLDER)

$(LOGS_FOLDER):
	if not exist $(LOGS_FOLDER) mkdir $(LOGS_FOLDER)
	if not exist $(LOGS_FOLDER)\csv mkdir $(LOGS_FOLDER)\csv

# Generar imágenes
gen_imgs: clean_2D $(SIZES_FILE) resize_src_imgs.sh $(SOURCE_FOLDER) $(IMG_FOLDER)
	resize_src_imgs.bat -sd $(SOURCE_FOLDER) -dd $(IMG_FOLDER) -f $(SIZES_FILE)

$(SIZES_FILE): generate_size.py
	python generate_size.py -N 40 -st 40000 -init 512 > $(SIZES_FILE)

# Comparaciones
compare_2D_time: $(IMG_FOLDER) compare_2D.py
	python compare_2D.py -d $(IMG_FOLDER) --resource time --logs_dir $(LOGS_FOLDER)

compare_2D_mem: $(IMG_FOLDER) compare_2D.py
	python compare_2D.py -d $(IMG_FOLDER) --resource memory --logs_dir $(LOGS_FOLDER)

# Graficar todo sin WL
plot_all: plots_time plots_mem

plots_time: plot_graph_time.py
	python plot_graph_time.py -d 2 -lg
	python plot_graph_time.py -d 3 -lg

plots_mem: plot_graph_mem.py
	python plot_graph_mem.py -d 2
	python plot_graph_mem.py -d 3

# Limpieza
clean: clean_2D

clean_2D:
	if exist $(IMG_FOLDER)\* del /Q $(IMG_FOLDER)\*
	if exist $(SIZES_FILE) del /Q $(SIZES_FILE)
