/// @file prim.cpp
/// @brief Реализация алгоритма Прима.

#include "prim.h"

#include <fstream>
#include <queue>
#include <sstream>
#include <vector>

namespace {

/// @brief Приводит число к короткому строковому виду для подписей в DOT.
///
/// Целые значения выводятся без дробной части, дробные — с ограниченной
/// точностью и без лишних нулей.
std::string formatWeight(double value) {
    std::ostringstream stream;
    if (value == static_cast<double>(static_cast<long long>(value))) {
        stream << static_cast<long long>(value);
    } else {
        stream.setf(std::ios::fixed);
        stream.precision(4);
        stream << value;
        std::string result = stream.str();
        while (!result.empty() && result.back() == '0') {
            result.pop_back();
        }
        if (!result.empty() && result.back() == '.') {
            result.pop_back();
        }
        return result;
    }
    return stream.str();
}

/// @brief Компаратор очереди с приоритетом: меньшее значение веса выше.
struct MinWeight {
    bool operator()(const std::pair<double, Edge>& first,
                    const std::pair<double, Edge>& second) const {
        return first.first > second.first;
    }
};

} // namespace

void Prim::run(const Graph& graph) {
    vertex_count_ = graph.vertexCount();
    tree_edges_.clear();
    total_weight_ = 0.0;

    if (vertex_count_ == 0) {
        return;
    }

    std::vector<bool> in_tree(vertex_count_, false);

    using QueueEntry = std::pair<double, Edge>;
    std::priority_queue<QueueEntry, std::vector<QueueEntry>, MinWeight> frontier;

    // Начало построения дерева с вершины 0.
    in_tree[0] = true;
    for (const Edge& edge : graph.adjacency(0)) {
        frontier.push({edge.weight, edge});
    }

    int attached = 1; // Количество вершин, уже включённых в дерево.
    while (!frontier.empty() && attached < vertex_count_) {
        const QueueEntry entry = frontier.top();
        frontier.pop();

        const Edge& edge = entry.second;
        if (in_tree[edge.to]) {
            continue; // Ребро ведёт в уже включённую вершину (устаревшее).
        }

        in_tree[edge.to] = true;
        tree_edges_.push_back(edge);
        total_weight_ += edge.weight;
        ++attached;

        for (const Edge& next : graph.adjacency(edge.to)) {
            if (!in_tree[next.to]) {
                frontier.push({next.weight, next});
            }
        }
    }
}

const std::vector<Edge>& Prim::treeEdges() const {
    return tree_edges_;
}

double Prim::totalWeight() const {
    return total_weight_;
}

bool Prim::isSpanning() const {
    return vertex_count_ == 0 ||
           static_cast<int>(tree_edges_.size()) == vertex_count_ - 1;
}

bool Prim::saveDot(const std::string& filename) const {
    std::ofstream output(filename);
    if (!output.is_open()) {
        return false;
    }

    output << "graph MST {\n";
    output << "    label = \"Minimum spanning tree (Prim's algorithm), "
           << "total weight = " << formatWeight(total_weight_) << "\";\n";
    output << "    node [shape = circle];\n";

    for (int vertex = 0; vertex < vertex_count_; ++vertex) {
        output << "    " << vertex << ";\n";
    }

    for (const Edge& edge : tree_edges_) {
        output << "    " << edge.from << " -- " << edge.to
               << " [label = \"" << formatWeight(edge.weight) << "\"];\n";
    }

    output << "}\n";
    return true;
}
