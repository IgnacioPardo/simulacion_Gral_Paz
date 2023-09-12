# Trabajo Práctico - Simulación General Paz

## Apliaciones Computacionales en Negocios

## Integrantes

- [Zoe Borrone - Legajo: 21G245]()
- [Luca Mazzarello - Legajo: 21L720]()
- [Ignacio Pardo - Legajo: 21R1160]()

## Estructura del repositorio

```{bash}
./src
│
├── Evaluation of Drivers Reaction Time Measured in Driving Simulator.ipynb # Notebook de la evaluación de los tiempos de reacción
│
├── assets
│   └── car.png # Imagen del auto
│
├─── car.py # Clase del auto
├─── highway.py # Clase de la autopista
├── simulation.py # Clase de la simulación
│
├── animation_%Y-%m-%d_%H-%M-%S.mp4 # Video resultante de la simulación
│
├── logs # Logs de la simulación
│
├── notebook.ipynb # Ideas preeliminares (no se usa), el contenido se pasó a simulation.py + highway.py + car.py
│
├── observations.ipynb # Notebook de las observaciones
│
├── plots # Gráficos de la simulación generados por observaciones.ipynb
│
└── utils.py # Funciones auxiliares para la animación (no se usa)
```

## Instrucciones de uso

### Requerimientos

- Python 3.8 y pip

Instalar las dependencias:

```{bash}
pip install -r requirements.txt
```

### Ejecutar la simulación

```{bash}
python simulation.py

python simulation.py --precision 100 --frames 12000 --interval 0 --fps 30 --length 14000 --max_v 100 --plot False --live False --short_scale False --log True --seed 42
```

### Parametros de la simulación

- `frames`: Cantidad de frames de la simulación: cada frame es un instante de tiempo en la simulación. Corresponde a 1 segundo de la vida real. Por defecto: 12000.
- `precision`: Por cada frame, los autos se actualizan `precision` veces. Por defecto: 100. Es decir, cada _subframe_ corresponde a 1/100 segundos de la vida real.
- `interval`: Cantidad de frames entre cada medición de velocidad. Por defecto: 0. Es decir, se mide la velocidad en cada frame.
- `fps`: Cantidad de frames por segundo del video resultante. Por defecto: 30.
- `length`: Longitud de la autopista. Por defecto: 14000mts (14kms)
- `max_v`: Velocidad máxima de los autos en kilometros por hora. Por defecto: 100(km/h)
- `plot`: Si se desea graficar la simulación. Por defecto: True.
- `live`: Si se desea ver la simulación en vivo. Por defecto: True.
- `short_scale`: Si se desea usar la escala corta para los ejes de los gráficos. Por defecto: True.
- `log`: Si se desea guardar los logs de la simulación. Por defecto: True.
- `seed`: Semilla para la generación de números aleatorios. Por defecto: 42.
- `smart_car_probability`: Probabilidad de que un auto sea inteligente. Por defecto: 0.2.

## Observaciones

Para ver las observaciones, ejecutar el notebook `observations.ipynb`.
Se tienen que haber ejecutado previamente las simulaciones con el parámetro `log` en `True`. Como resultante dentro de la carpeta `logs` se generan los archivos `.csv` con los logs de cada simulación.
El notebook genera los gráficos y los guarda en la carpeta `plots`.
Además imprime algunas estadísticas de las simulaciones.

## Evaluación de los tiempos de reacción

La evaluación de los tiempos de reacción se encuentra en el notebook `Evaluation of Drivers Reaction Time Measured in Driving Simulator.ipynb`.
Los datos se obtuvieron de la siguiente publicación:
[Evaluation of Driver’s Reaction Time Measured in Driving Simulator](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9099898/)

Los resultados obtenidos se encuentran en el notebook.

## Referencias

- [Evaluation of Driver’s Reaction Time Measured in Driving Simulator](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9099898/)
- [Intelligent Driver Model](https://en.wikipedia.org/wiki/Intelligent_driver_model)
- [Traffic Shockwaves](https://www.youtube.com/watch?v=6ZC9h8jgSj4&pp=ygUSZ2VvcmdpYSBzaG9ja3dhdmVz)
