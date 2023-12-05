# Ejemplo genérico de funcionamiento de Orange (tiempo estimado: 30min)

Usaremos los widgets propios de Orange para familiarizarnos con la aplicación.

Vamos a descargar uno de los datasets existentes en Orange para realizar un análisis sencillo. Para ello, seleccionamos el widget "Datasets" de la sección "Data", de la columna izquierda donde se encuentran todos los widgets disponibles.

<img src="images/orange_intro_4.png" alt="orange_intro_4" width="800"/>

Hacemos doble click sobre el widget para que se abra la ventana que nos permitirá seleccionar un dataset de los que tiene cargados Orange para practicar. En este caso elegimos el conjunto de datos "Illegal waste 
dumpsites in Slovenia", haciendo doble click sobre él para que se descargue a nuestra aplicación. Aparecerá un círculo verde junto al nombre del dataset cuando se haya descargado.

Vamos a explorar los datos que hemos obtenido. Para ello usamos el widget *Data Table*, conectándolo con nuestro widget *Datasets*. Vemos que la conexión entre los dos widgets es una línea continua, que indica que los datos se han transmitido correctamente. Haciendo doble click en Data Table vemos los datos que tenemos:

<img src="images/orange_intro_5.png" alt="orange_intro_5" width="800"/>

Vemos que se trata de 13165 líneas (instances). Exploramos las columnas que tenemos para hacernos una idea de los datos. Ya podemos analizarlos.

## ¿Cuántos incidentes se han registrado cada año?
Existe un campo llamado "Entry creation date" que nos da la fecha en que se incorporó el registro. Lo tomaremos como la fecha de la infracción. Queremos ver cuántos registros hay cada año. Conectaremos nuestra tabla con el widget que nos permite visualizar distribuciones, llamado *Distributions* y hacemos doble click sobre él para ver qué opciones nos da:

<img src="images/orange_intro_6.png" alt="orange_intro_6" width="800"/>

Lo primero es seleccionar la variable (la columna) que queremos representar. De la lista de nombres de columnas marcada con el número 1, seleccionamos *Entry creation date*. Veremos una representación de los datos en fechas. El campo con el número 2, llamado *Bin width*. Aquí podremos decidir que rango temporal queremos para nuestra agrupación. Elegiremos *1 year*, para sacar la distribución año a año.

Ahora vemos un gráfico de columnas con el número de registros que tenemos cada año, y llama la atención el número de eventos que tenemos de 2010. Pensemos que queremos descargarnos este primer gráfico. Nos vamos a la parte inferior izquierda de la ventana y veremos un pequeño disquete (identificado con el número 3). Pinchando en él nos podremos descargar la imagen del gráfico.

Pero podemos hacer algo más con nuestro gráfico de distribución. Podemos querer dividir los registros de cada columna por otra variable:

<img src="images/orange_intro_7.png" alt="orange_intro_7" width="800"/>

En este caso tenemos una columna llamada *Was cleaned* que nos indica si el vertido ha sido limpiado o no. Vamos a usarlo para ver cuántos de los registros de cada año se han limpiado. Seleccionamos el nombre de la columna en el campo *Split by*. Nos mostrará dos columnas por cada año, uno para los registros que tiene valor 0 en *Was cleaned* y otra con lo que tienen valor 1. De forma general, se considera que 0 equivale a Falso y 1 a Verdadero. Esta vista de dos columnas por año puede ser un poco confusa para analizar. Si preferimos que ambas aparezcan en columnas apiladas, seleccionaremos *Stack columns*, debajo del desplegable donde hemos elegido la columna. Nos quedará un gráfico muy ilustrativo. 

# Cambiar valores de una columna

Digamos que el hecho de que la columna *Was cleaned* tenga valores 0 y 1 no es muy claro y queremos que en lugar de eso indique False/True, para que nos ayude a interpretar los resultados. Podemos hacerlo usando el widget *Edit Domain*:

<img src="images/orange_intro_8.png" alt="orange_intro_8" width="800"/>

Ahí seleccionamos la columna que queremos tratar, en el apartado marcado con un 1. Vemos los valores que puede tomar la columna *Was cleaned*, que puede ser 0 o 1. Si hacemos doble click sobre 0 podemos darle el valor que queramos que tenga, por ejemplo, "NO" para 0, y "YES" para 1. Después de escribir el valor que queremos que tome, pulsamos Intro para que se haga el cambio. Veremos algo así:

<img src="images/orange_intro_9.png" alt="orange_intro_9" width="800"/>

Ya podemos utilizar esta salida para representar correctamente estos datos.

# Crear una columna a partir de otros datos
Volvamos al dataset original. Hay una columna llamada *Waste area (m2)* muy interesante para nuestro análisis, pero nos gustaría obtener a partir de ella los registros que se corresponden a áreas pequeñas, grandes y muy grandes. 

<img src="images/orange_intro_10.png" alt="orange_intro_10" width="800"/>

Vamos a tratar esa columna numérica. Usamos el widget *Discretize* que se encuentra en la sección *Transform*. Abrimos ese widget, elegimos la columna que queremos convertir y luego la forma de transformación. En este caso elegiremos directamente los rangos que queremos para nuestra columna (opción Custom) y estos serán: 100m2, 1000m2 y 10000m2: 

<img src="images/orange_intro_11.png" alt="orange_intro_11" width="800"/>

¿Cómo queda nuestra tabla después de hacer esto?

<img src="images/orange_intro_12.png" alt="orange_intro_12" width="800"/>

Vemos que ahora tenemos una columna en la que aparece el rango del área de basura, según los parámetros que le dimos: menos de 100m2, entre 100 y 1000m2, entre 1000-10000 y más de 10000. Ya podemos ver el número de registros de cada rango. Sólo tenemos que conectar nuestra nueva tabla con el widget *Distribution*, como hemos hecho antes, para ver el número de registros en cada franja.

<img src="images/orange_intro_13.png" alt="orange_intro_13" width="800"/>

# Representar los registros en un mapa
Vamos a ver una de las opciones más interesantes de representación de datos cuando tenemos localizaciones. Veamos su representación en un mapa. Conectamos nuestra tabla de datos al widget *Geo Map*. Lo que veremos será algo así:

<img src="images/orange_intro_14.png" alt="orange_intro_14" width="800"/>

Modificando los atributos, podremos crear un mapa que comunique información. Podemos elegir el color de los puntos según una columna, como por ejemplo *Was cleaned*, *Waste partially buried?* o cualquiera de tipo categoría. Podemos darle tamaño (size) en función de una columna numérica, como *Waste area [m2]* o *Waste volume [m3]*. Podemos guardar el mapa de la misma forma que guardamos un gráfico, o hacer una selección de una zona para quedarnos con esos registros y poder analizarlos por separado.

El resultado de todo esto es un workflow que podemos guardar, en formato propio de .ows y reproducir en cualquier momento.

<img src="images/orange_intro_15.png" alt="orange_intro_15" width="800"/>