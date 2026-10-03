/// @file graph.cpp
/// @brief Реализация класса Graph.

#include "graph.h"

#include <fstream>

bool Graph::loadFromMatrixFile(const std::string& filename) {
    std::ifstream input(filename);
    if (!input.is_open()) {
        return false;
    }

    int n = 0;
    if (!(input >> n) || n <= 0) {
        return false;
    }

    vertex_count_ = n;
    adjacency_list_.assign(n, std::vector<Edge>());

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            double weight = 0.0;
            if (!(input >> weight)) {
                return false;
            }
            if (weight == 0.0) {
                continue; // Ребра нет.
            }
            if (i < j) {
                // Неориентированное ребро добавляется в оба списка смежности.
                adjacency_list_[i].push_back(Edge{i, j, weight});
                adjacency_list_[j].push_back(Edge{j, i, weight});
            }
        }
    }
    return true;
}

int Graph::vertexCount() const {
    return vertex_count_;
}

const std::vector<Edge>& Graph::adjacency(int vertex) const {
    return adjacency_list_[vertex];
}
