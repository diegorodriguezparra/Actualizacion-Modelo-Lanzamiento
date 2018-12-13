Proyecto REOS
===============
Repositorio GitHub para la organización de código.

En este repositorio se incluirán los archivos de código que se emplean en el proyecto,
tanto para trayectoria de lanzamiento como para el sistema orbital.

En el caso de que el propietario de este directorio abandone el NIDO, será necesario que
otro integrante del REOS se encarge de descargarse las ramas pertinentes y crear otro
directorio siendo él mismo el propietario del proyecto, después contactar con el antiguo
propietario para que elimine el directorio que dejará de tener validez.

Modo de Uso
-------------
Aquí se incluye una breve introducción a GitHub.

GitHub se basa en la ramificación de un proyecto, para así poder trabajar a la vez en
diferentes versiones o partes de éste. 

Inicialmente existe un único respositorio, el cual vamos a considerar el tronco del proyecto
o repositorio principal. Éste tiene el nombre de **'master'**.

Cuando ramificas el repositorio princial, creas una **branch**, en 'master' se crea una copia
de la rama en ese instante. Si alguien modifica la rama 'master' mientras uno está trabajando
en su propia rama, es posible actualizar tu rama con los datos modificados, pero github no lo
hará a no ser que se lo indiques.
Para ramificar una rama lo primero es ir a la página principal del repositorio, abrir el menu
de 'branches', elegir un nombre para la nueva rama y pulsar 'Enter'.
Para borrar una rama hay que ir al repositorio principal, sleccionar 'Number branches' y eliminar.

Es importante que no haya varias personas y ramas trabajando sobre la misma cosa,
debido a que lo que uno cambie no le aparecerá al otro y no se podrá unir de nuevo
a la rama 'master'. Es decir, si uno decide trabajar sobre archivos existentes, ha de
tener cuidado pues puede que esté trabajando sobre archivos obsoletos, y si otro quiere
trabajar sobre lo mismo ha de haber comunicación.

Un **'pull request'** permite dar a conocer a los demas contribuyentes los cambios que quieres
realizar. Una vez se abre esa 'pull request' cualquiera puede discutir y reaccionar a esos
cambios, para después decidir si unirlos a la rama principal.
Para crear una petición o **'request'**, lo primero que hay que hacer es crear una nueva
rama y una vez hechos los cambios crear la solicitud, la cual deberá ser aceptada mediante
un **'pull request'**.
Crear una 'pull request' equivale a crear una rama con ciertos cambios. Por defecto, las
peticiones están basadas en el repositorio principal, si se quiere hacer una petición a
otra rama tendrá que elegirse en la lista de ramas: la 'base branch' es donde se quieren
realizar los cambios y 'head branch' contiene lo que se quiere cambiar.
Una vez creada una petición, se pueden introducir cambios a ésta y aparecerán en orden 
cronológico en la ventana "Files Changed". Se pueden ver también los cambios en la rama
de trabajo en la ventana "Conversation".

Una vez se ha terminado de realizar cambios en la rama, se puede unir la petición al repositorio
o rama principal. Estos cambios se aplicarán de la 'head branch' a la 'base branch'. Para poder
unir las ramas se incluye un filtro, este filtro consiste en que otra persona del proyecto revise
el código para que no haya ningún fallo de transcripción al unir la rama. Es decir, una 
revisión de la petición por una segunda persona.

A la hora de hacer un **'pull request merge'** hay varias maneras. 
La primera es la que se realiza por defecto cuando se selecciona la opción 'merge pull request'
en una petición, todos los cambios ('commits') de la rama de trabajo se añaden a la 'base branch'
en una unión individualmente.

<img src="images/merge_commit.PNG" width="50%">

La segunda opción es hacer un **'squash and merge'**, la cual se va a recomendar. Ésta opción 
consiste en unir la rama de trabajo a la principal como un todo, es decir combinando todos los
cambios en una única petición.

<img src="images/squash_merge.PNG" width="50%">

Para unir una petición hay que pinchar en "Pull requests" y elegir la petición que queremos unir.
A continuación hay que incluir un mensaje indicando los cambios que se han llevado a cabo y
confirmar la unión.

Otra manera de trabajar es haciendo un **'fork'**, esto consiste en clonar el trabajo creando
una copia del repositorio, incluyendo todas las ramas que existen en ese momento, para así poder
experimentar libremente cambiando cosas sin afectar al código original. Una vez trabajado con el
'fork', se puede crear una solicitud al propietario del proyecto.

Dentro de un 'fork' es posible crear ramas, de la misma manera que en el proyecto principal. Pero 
no se recomienda trabajar con 'fork' pues realmente sería como trabajar sobre otro proyecto.

Resumen
-------
 - El **repositorio principal** corresponde al trabajo colaborativo del equipo, el cual puede tener
una o varias ramas. Todos los contribuyentes tienen su propia copia del mismo.
 - Cada **'fork'** del repositorio principal corresponde al trabajo de un contribuyente. Realmente un 
'fork' es una construcción GitHub para almacenar un clon del repositorio en tu cuenta de usuario.
Como clon, contendrá todas las ramas del repositorio clonado en el momento que se hace el 'fork'.
 - Cada **'branch'/rama** en un 'fork' o en el repositorio principal puede corresponder a diferentes
cosas, en función de como se quiera trabajar. Cada rama puede referirse a una versión del proyecto
pero también puede corresponder a diferentes caminos de desarrollo como puede ser trabajo experimental.
 - Un **'pull request'** corresponde a una tarea. Cada vez que uno quiera contribuir a la rama principal
con una tarea finalizada, hay que crear una 'pull request' que contenga los 'commits' o cambios
realizados. Estos cambios se aplicarán desde un 'fork' o 'branch' al repositorio principal una vez
se acepte la petición.
 - Un **'commit'** es una serie de cambios realizados en el código.
 
 A la hora de trabajar se recomienda trabajar ÚNICAMENTE CON BRANCHES pues es un lío tener 'forks'
 o clones del proyecto. Antes de comenzar con una nueva rama hay que unir o eliminar las que
 tengamos activas, para que no haya demasiadas ramas a la vez.
 
 Desde la ventana "Insights" y "Networks" se puede ver como se han ido creando y uniendo las ramas
 teniendo una visión general del proyecto.
