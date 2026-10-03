/// @file prim.h
/// @brief Построение минимального остовного дерева алгоритмом Прима.

#ifndef PRIM_H
#define PRIM_H

#include <string>
#include <vector>

#include "graph.h"

/// @brief Построение минимального остовного дерева алгоритмом Прима.
class Prim {
public:
    /// @brief Выполняет алгоритм Прима на заданном графе.
    ///
    /// Алгоритм строит минимальное остовное дерево, начиная с вершины 0.
    /// Для хранения рёбер, пересекающих разрез, используется очередь
    /// с приоритетом (двоичная куча из STL).
    ///
    /// @param graph Исходный взвешенный неориентированный граф.
    void run(const Graph& graph);

    /// @brief Возвращает рёбра построенного минимального остовного дерева.
    const std::vector<Edge>& treeEdges() const;

    /// @brief Возвращает суммарный вес минимального остовного дерева.
    double totalWeight() const;

    /// @brief Проверяет, охватывает ли результат все вершины графа
    ///        (то есть является ли он действительно остовным деревом).
    ///
    /// @return true, если результат является остовным деревом.
    bool isSpanning() const;

    /// @brief Сохраняет дерево в файл в формате graphviz (DOT).
    ///
    /// @param filename Имя выходного файла.
    /// @return true, если файл успешно записан.
    bool saveDot(const std::string& filename) const;

private:
    std::vector<Edge> tree_edges_; ///< Рёбра минимального остовного дерева.
    double total_weight_ = 0.0;    ///< Суммарный вес дерева.
    int vertex_count_ = 0;         ///< Количество вершин исходного графа.
};

#endif // PRIM_H
