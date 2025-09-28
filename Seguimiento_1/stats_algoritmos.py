import matplotlib.pyplot as plt

# Nombres de los algoritmos
algorithms = [
    "TimSort", "Pigeonhole Sort", "RadixSort", "Tree Sort", 
    "QuickSort", "HeapSort", "Comb Sort", "Binary Insertion Sort",
    "Bitonic Sort", "Selection Sort", "BucketSort", "Gnome Sort"
]

# Tiempos correspondientes (en segundos) que me diste
times = [
    0.007775, 0.182685, 2.360685, 0.082040,
    0.015041, 1.478462, 0.089920, 0.092856,
    0.360274, 8.256235, 0.225239, 0.032919
]

# Ordenar ascendentemente según el tiempo
sorted_indices = sorted(range(len(times)), key=lambda i: times[i])
sorted_algorithms = [algorithms[i] for i in sorted_indices]
sorted_times = [times[i] for i in sorted_indices]

# Crear el gráfico de barras horizontales
plt.figure(figsize=(12,6))
plt.barh(sorted_algorithms, sorted_times, color='skyblue')
plt.xlabel("Tiempo de ejecución (segundos)")
plt.ylabel("Algoritmo de ordenamiento")
plt.title("Comparación de tiempos de 12 algoritmos de ordenamiento")
plt.grid(axis='x', linestyle='--', alpha=0.7)

# Etiquetas con los valores en cada barra
for i, v in enumerate(sorted_times):
    plt.text(v + 0.01, i, f"{v:.6f}", va='center')

# Mostrar el gráfico
plt.tight_layout()
plt.show()
