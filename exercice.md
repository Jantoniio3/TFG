# Ejercicio Generado

## Enunciado
Ejercicio: Búsqueda secuencial: Encontrar un elemento en una lista utilizando búsqueda lineal. 

Descripción: En este ejercicio, aprenderás a implementar la búsqueda secuencial para encontrar un número en una lista dada. El programa generará una lista de 100 números enteros aleatorios y el objetivo es escribir un programa que encuentre un número específico utilizando la búsqueda lineal.

Instrucciones:
1. Genera una lista llamada `numeros` que contenga 100 números enteros aleatorios entre 1 y 200.
2. Asigna un número objetivo a buscar en la lista, por ejemplo, `numero_objetivo = 56`. 
3. Escribe una función llamada `encontrar_numero` que tome como parámetro la lista `numeros` y el valor del `numero_objetivo`. Esta función debe implementar la búsqueda secuencial para encontrar el número objetivo en la lista.
4. Utiliza un bucle for para recorrer cada elemento de la lista `numeros`. En cada iteración, verifica si el valor actual del elemento es igual al `numero_objetivo`.
5. Si se encuentra el número objetivo, la función debe devolver True. De lo contrario, debe devolver False.
6. Llama a la función `encontrar_numero` pasando los argumentos necesarios y almacena el resultado en una variable llamada `resultado`. 
7. Verifica si el valor de `resultado` es True o False e imprime un mensaje apropiado.

## Solución y Explicación
Primero, generamos la lista de números aleatorios utilizando la función `random.sample()`. Luego, definimos una función `encontrar_numero()` que recibe la lista y el número objetivo como parámetros. Dentro de esta función, usamos un bucle for para iterar sobre cada elemento de la lista. En cada iteración, comparamos el valor actual del elemento con el número objetivo. Si son iguales, devolvemos True ya que hemos encontrado el número. Si no lo encontramos después de recorrer toda la lista, devolvemos False.
