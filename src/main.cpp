/// @file main.cpp
/// @brief Точка входа программы построения минимального остовного дерева.

#include <iostream>
#include <string>

#include "graph.h"
#include "prim.h"

/// @brief Точка входа программы.
///
/// Программа принимает два аргумента командной строки: имя входного файла
/// (матрица смежности весов) и имя выходного файла (graphviz DOT).
///
/// @param argc Количество аргументов командной строки.
/// @param argv Массив аргументов командной строки.
/// @return 0 при успешном завершении, ненулевое значение при ошибке.
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <input-file> <output-file>\n";
        return 1;
    }

    const std::string input_filename = argv[1];
    const std::string output_filename = argv[2];

    // Загрузка исходных данных.
    Graph graph;
    if (!graph.loadFromMatrixFile(input_filename)) {
        std::cerr << "Error: failed to load graph from file \""
                  << input_filename << "\".\n";
        return 1;
    }

    // Выполнение алгоритма.
    Prim prim;
    prim.run(graph);

    if (!prim.isSpanning()) {
        std::cerr << "Warning: the graph is disconnected, "
                  << "so there is no spanning tree.\n";
    }

    // Сохранение результата.
    if (!prim.saveDot(output_filename)) {
        std::cerr << "Error: failed to write result to file \""
                  << output_filename << "\".\n";
        return 1;
    }

    std::cout << "Minimum spanning tree (total weight = " << prim.totalWeight()
              << ") saved to \"" << output_filename << "\".\n";
    return 0;
}
