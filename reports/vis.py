import matplotlib.pyplot as plt
import seaborn as sns
import json
import numpy as np
import pandas as pd
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parent


def do_plot(title, data, small: bool = False):
    data = json.loads(data)

    # Подготовка данных для heatmap
    # Извлекаем данные для heatmap для avg и max ключей
    ratios_avg = data['avg']
    ratios_max = data['max']

    if small:
        k_values = list(range(2, 12))
        n_values = [list(range(k, 12)) for k in k_values]
    else:
        k_values = list(range(3, 13))
        n_values = [list(range(50, 400, 50)) for k in k_values]

    # Определяем значения для меток осей x и y
    k_values_labels = k_values
    n_values_labels = [n for sublist in n_values for n in sublist]
    n_values_labels = sorted(list(set(n_values_labels)))  # Уникальные и отсортированные значения n

    # Создаем DataFrame для heatmap
    # Для каждой комбинации k и n, найдем соответствующее значение из ratios
    heatmap_data_avg = pd.DataFrame(index=k_values_labels, columns=n_values_labels, dtype=float)
    heatmap_data_max = pd.DataFrame(index=k_values_labels, columns=n_values_labels, dtype=float)

    for i, k in enumerate(k_values):
        for j, n in enumerate(n_values[i]):
            if j < len(ratios_avg[i]):
                heatmap_data_avg.loc[k, n] = ratios_avg[i][j]
            if j < len(ratios_max[i]):
                heatmap_data_max.loc[k, n] = ratios_max[i][j]

    # Визуализация heatmap для "avg"
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data_avg, annot=True, cmap="viridis", fmt=".2f", linewidths=.5)
    plt.title('Средняя ошибка - ' + title)
    plt.xlabel('n')
    plt.ylabel('k')
    plt.show()

    # Визуализация heatmap для "max"
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data_max, annot=True, cmap="viridis", fmt=".2f", linewidths=.5)
    plt.title('Максимальная ошибка - ' + title)
    plt.xlabel('n')
    plt.ylabel('k')
    plt.show()


def read_file(path):
    with open(path) as file:
        return file.read()


do_plot('Эрдёш-Реньи жадное/аппроксимационное, p = 0.2', read_file('erdos_renyi_big-0.2.json'))
do_plot('Эрдёш-Реньи жадное/аппроксимационное, p = 0.5', read_file('erdos_renyi_big-0.5.json'))
do_plot('Эрдёш-Реньи жадное/аппроксимационное, p = 0.9', read_file('erdos_renyi_big-0.9.json'))
do_plot('Эрдёш-Реньи аппроксимационное/наивное, p = 0.2', read_file('erdos_renyi_small-0.2-500.json'), True)
do_plot('Эрдёш-Реньи аппроксимационное/наивное, p = 0.5', read_file('erdos_renyi_small-0.5-500.json'), True)
do_plot('Эрдёш-Реньи аппроксимационное/наивное, p = 0.9', read_file('erdos_renyi_small-0.9-500.json'), True)
