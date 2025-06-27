# Descripción

A Pacha le gusta mucho caminar por las montañas. Esta vez se le ocurrió ir *al punto más alto* de las montañas que rodean su ciudad para tomar una foto de recuerdo. Es bien sabido que no hay ningún otro punto en la montaña con una altura igual o superior, por lo que tiene la mejor vista.

Él siempre junta un grupo para estas actividades y esta vez, decidiste unirte. Llegó el día de la excursión; ya habías preparado todo, pero, por desgracia, te quedaste dormido... No podrás acompañar al grupo todo el camino, pero sí puedes encontrarlos en *el punto más alto*. Le pides el mapa a Pacha para alcanzarlos y él te lo envía en forma de acertijo.

Las montañas se representan como una cadena que consiste de los caracteres '$+$' y '$-$', cada uno indicando si ese punto de la montaña es más alto o más bajo que el anterior de izquierda a derecha, y teniendo siempre una diferencia de alturas de 1 metro. Te dice también, que asumas que el punto anterior al inicio de la montaña se encuentra a altura 0.

Por ejemplo, la cadena $+++--+--$ es un mapa de montañas con alturas $[1, 2, 3, 2, 1, 2, 1, 0]$.

Dado el mapa, debes calcular la posición de la montaña (de izquierda a derecha) que corresponda al punto más alto para encontrarte con el grupo.

## Entrada

La primera y única línea contiene una cadena $s$ formada por los caracteres '$+$' y '$-$' (sin comillas). El tamaño de la cadena no será superior a $10^5$ y contendrá al menos un caracter.

Se garantiza que todos los puntos de las montañas estarán a una altura no negativa y que *solamente habrá un punto más alto*.

## Salida

Un número entero, indicando la posición de la montaña que corresponde al punto más alto.

## Ejemplos

\sample-case 0-01.in 0-01.out
\sample-case 0-02.in 0-02.out

En el primer caso, los puntos de las montañas tienen las alturas $[1, 0, 1, 0, 1, 2, 3, 2, 1, 2, 1, 0]$. El punto en la posición $7$ es el más alto.
