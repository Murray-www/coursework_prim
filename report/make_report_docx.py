# -*- coding: utf-8 -*-
"""Сборка отчёта report.docx без внешних библиотек (чистый OOXML)."""
import os
import struct
import zipfile

BODY_FONT = "Times New Roman"
MONO_FONT = "Consolas"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_R_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def esc(text):
    return (text.replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;'))


def png_size(path):
    with open(path, 'rb') as f:
        data = f.read(24)
    return struct.unpack('>II', data[16:24])


# ---------- поля и закладки ----------
_bookmark_id = [0]


def next_bid():
    _bookmark_id[0] += 1
    return _bookmark_id[0]


def field_runs(instr, placeholder):
    return ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> %s </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r><w:t>%s</w:t></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
            % (instr, esc(placeholder)))


def seq_figure_runs(bookmark, placeholder):
    bid = next_bid()
    return ('<w:bookmarkStart w:id="%d" w:name="%s"/>'
            '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> SEQ Figure \\* ARABIC '
            '</w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r><w:t>%s</w:t></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
            '<w:bookmarkEnd w:id="%d"/>'
            % (bid, bookmark, esc(placeholder), bid))


def ref_runs(bookmark, placeholder):
    return field_runs('REF %s \\h' % bookmark, placeholder)


# ---------- построение абзацев ----------
def run(text, bold=False, mono=False, sz=28):
    font = MONO_FONT if mono else BODY_FONT
    b = '<w:b/>' if bold else ''
    return ('<w:r><w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/>%s'
            '<w:sz w:val="%d"/><w:szCs w:val="%d"/></w:rPr>'
            '<w:t xml:space="preserve">%s</w:t></w:r>'
            % (font, font, font, b, sz, sz, esc(text)))


def plain_run(text):
    return '<w:r><w:t xml:space="preserve">%s</w:t></w:r>' % esc(text)


def para(runs_xml, style=None, align=None, first=False, line=None,
         before=0, after=0):
    ppr = []
    if style:
        ppr.append('<w:pStyle w:val="%s"/>' % style)
    if first:
        ppr.append('<w:ind w:firstLine="709"/>')
    if align:
        ppr.append('<w:jc w:val="%s"/>' % align)
    ppr.append('<w:spacing w:before="%d" w:after="%d"' % (before, after))
    if line is not None:
        ppr.append(' w:line="%d" w:lineRule="auto"' % line)
    ppr.append('/>')
    return '<w:p><w:pPr>%s</w:pPr>%s</w:p>' % ('\n'.join(ppr), runs_xml)


def body(text):
    return para(run(text), align='both', first=True, line=360)


def bullet(text):
    return para(run('—  ' + text), align='both', line=360)


def h1(text):
    return para(plain_run(text), style='Heading1')


def h2(text):
    return para(plain_run(text), style='Heading2')


def code(text):
    lines = text.rstrip('\n').split('\n')
    return '\n'.join(para(plain_run(line), style='Code') for line in lines)


def centered(text, bold=False, sz=28, before=0, after=0):
    return para(run(text, bold=bold, sz=sz), align='center',
                before=before, after=after)


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def toc_field():
    return ('<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> TOC \\o &quot;1-2&quot; '
            '\\h \\z \\u </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            '<w:r><w:t>Обновите поле оглавления (F9) в Word.</w:t></w:r>'
            '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>')


_img_counter = [0]


def image_para(rid, path, name, max_w=5500000):
    w, h = png_size(path)
    emu_w = max_w
    emu_h = int(max_w * h / w)
    _img_counter[0] += 1
    did = _img_counter[0]
    return ('<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            '<wp:inline distT="0" distB="0" distL="0" distR="0">'
            '<wp:extent cx="%d" cy="%d"/>'
            '<wp:docPr id="%d" name="%s"/>'
            '<a:graphic><a:graphicData '
            'uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic><pic:nvPicPr><pic:cNvPr id="0" name="%s"/>'
            '<pic:cNvPicPr/></pic:nvPicPr>'
            '<pic:blipFill><a:blip r:embed="%s"/>'
            '<a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/>'
            '<a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            '</pic:pic></a:graphicData></a:graphic></wp:inline>'
            '</w:drawing></w:r></w:p>'
            % (emu_w, emu_h, did, name, name, rid, emu_w, emu_h))


def figure(rid, path, name, bookmark, number, title):
    return (image_para(rid, path, name)
            + para(run('Рисунок ') + seq_figure_runs(bookmark, str(number))
                   + run(' — ' + title),
                   align='center', before=120, after=240))


def body_with_ref(prefix, bookmark, placeholder, suffix):
    return para(run(prefix) + ref_runs(bookmark, placeholder) + run(suffix),
                align='both', first=True, line=360)


SOURCE_FILES = [
    ('src/main.cpp', '../src/main.cpp'),
    ('inc/graph.h', '../inc/graph.h'),
    ('src/graph.cpp', '../src/graph.cpp'),
    ('inc/prim.h', '../inc/prim.h'),
    ('src/prim.cpp', '../src/prim.cpp'),
]


def build_body():
    out = []

    # ---------- Титульный лист ----------
    out.append(centered('МИНИСТЕРСТВО НАУКИ И ВЫСШЕГО ОБРАЗОВАНИЯ '
                        'РОССИЙСКОЙ ФЕДЕРАЦИИ', sz=20, after=60))
    out.append(centered('ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ АВТОНОМНОЕ '
                        'ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ ВЫСШЕГО ОБРАЗОВАНИЯ',
                        sz=20, after=60))
    out.append(centered('«САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ '
                        'АЭРОКОСМИЧЕСКОГО ПРИБОРОСТРОЕНИЯ»', sz=20, after=200))
    out.append(centered('КУРСОВАЯ РАБОТА', bold=True, sz=28, before=200, after=80))
    out.append(centered('по дисциплине «Программирование»', sz=28, after=120))
    out.append(centered('Тема: «Алгоритм Прима: построение минимального '
                        'остовного дерева»', bold=True, sz=28, after=200))
    out.append(para(run('Выполнил: студент группы {ГРУППА}', sz=24),
                    align='right', before=120))
    out.append(para(run('{ФАМИЛИЯ И. О.}', sz=24), align='right'))
    out.append(para(run('Проверил: {ФАМИЛИЯ И. О. ПРЕПОДАВАТЕЛЯ}', sz=24),
                    align='right', before=120))
    out.append(centered('Санкт-Петербург', sz=24, before=240))
    out.append(centered('{ГОД}', sz=24))
    out.append(page_break())

    # ---------- Оглавление ----------
    out.append(h1('Оглавление'))
    out.append(toc_field())
    out.append(page_break())

    # ---------- 1. Постановка задачи ----------
    out.append(h1('1. Постановка задачи'))
    out.append(body('Задачей данной курсовой работы является разработка '
                    'программы, которая по заданному взвешенному '
                    'неориентированному связному графу строит его минимальное '
                    'остовное дерево с помощью алгоритма Прима и сохраняет '
                    'результат в текстовый файл в формате graphviz (DOT).'))
    out.append(body('Пусть задан связный неориентированный граф G = (V, E), '
                    'каждому ребру e ∈ E которого приписан неотрицательный '
                    'вес w(e). Остовным деревом (каркасом) графа называется '
                    'такой его подграф T = (V, E′), который содержит все '
                    'вершины исходного графа и при этом является деревом, то '
                    'есть связным графом без циклов. Минимальным остовным '
                    'деревом называется остовное дерево, сумма весов рёбер '
                    'которого минимальна среди всех остовных деревьев данного '
                    'графа. Если в графе имеются рёбра одинакового веса, '
                    'минимальное остовное дерево может быть не единственным; '
                    'в этом случае программа выводит одно из возможных.'))
    out.append(body('Задача имеет практический смысл: минимальное остовное '
                    'дерево описывает, например, наиболее дешёвый способ '
                    'соединения нескольких объектов сетью (дорогами, линиями '
                    'связи, трубопроводами) без образования циклов. Связность '
                    'дерева гарантирует достижимость любого объекта, а '
                    'отсутствие циклов — отсутствие избыточных соединений.'))
    out.append(body_with_ref('Осмысленность задачи можно показать на примере. '
                             'Для графа, изображённого на рисунке ',
                             'Fig1', '1',
                             ', существуют остовные деревья различной '
                             'стоимости. Так, дерево из рёбер (0,1), (1,2), '
                             '(1,3), (3,4) и (4,5) имеет суммарный вес '
                             '4+1+5+2+3 = 15, тогда как дерево из рёбер (0,2), '
                             '(1,2), (1,3), (3,4) и (4,5) имеет вес '
                             '2+1+5+2+3 = 13. Таким образом, выбор дерева '
                             'минимальной стоимости не является тривиальным. '
                             'Подробное описание задачи и алгоритма её решения '
                             'приведено в книге [1].'))
    out.append(figure('rIdImg1', 'fig/fig_graph.png', 'fig_graph.png',
                      'Fig1', 1, 'Исходный взвешенный неориентированный граф'))

    # ---------- 2. Алгоритм ----------
    out.append(h1('2. Алгоритм'))
    out.append(h2('2.1. Идея алгоритма'))
    out.append(body('Алгоритм Прима относится к классу жадных алгоритмов. Он '
                    'строит минимальное остовное дерево постепенно: на каждом '
                    'шаге к уже построенной части дерева присоединяется ребро '
                    'минимального веса, один конец которого лежит в дереве, а '
                    'другой — вне его. Построение начинается с произвольной '
                    'вершины (в данной реализации — с вершины с номером 0). '
                    'Процесс продолжается до тех пор, пока в дерево не будут '
                    'включены все вершины графа.'))
    out.append(h2('2.2. Структуры данных'))
    out.append(body('В программе используются следующие структуры данных:'))
    out.append(bullet('граф хранится в виде списков смежности — контейнера '
                      'std::vector<std::vector<Edge>>, где Edge — структура, '
                      'содержащая номера вершин и вес ребра;'))
    out.append(bullet('множество вершин, уже включённых в дерево, '
                      'представляется булевым вектором std::vector<bool>;'))
    out.append(bullet('для выбора ребра минимального веса, пересекающего '
                      'разрез (множество рёбер, соединяющих вершины дерева с '
                      'остальными вершинами), используется очередь с '
                      'приоритетом std::priority_queue, основанная на двоичной '
                      'куче.'))
    out.append(h2('2.3. Пошаговое выполнение на примере'))
    out.append(body('Рассмотрим работу алгоритма на графе, изображённом на '
                    'рисунке 1. Построение начинается с вершины 0.'))
    out.append(body('1. Дерево состоит из вершины {0}. Рёбра, пересекающие '
                    'разрез: (0,1) с весом 4 и (0,2) с весом 2. Выбирается '
                    'ребро минимального веса (0,2); вершина 2 включается в '
                    'дерево.'))
    out.append(body('2. Дерево: {0,2}. Рёбра, пересекающие разрез: (0,1), '
                    '(1,2), (2,3), (2,4). Минимальное — (1,2) с весом 1; '
                    'вершина 1 включается в дерево.'))
    out.append(body('3. Дерево: {0,1,2}. Из рёбер (2,3), (2,4), (1,3) '
                    'выбирается (1,3) с весом 5; вершина 3 включается в '
                    'дерево.'))
    out.append(body('4. Дерево: {0,1,2,3}. Из рёбер (2,4), (3,4), (3,5) '
                    'выбирается (3,4) с весом 2; вершина 4 включается в '
                    'дерево.'))
    out.append(body('5. Дерево: {0,1,2,3,4}. Из рёбер (3,5), (4,5) выбирается '
                    '(4,5) с весом 3; вершина 5 включается в дерево.'))
    out.append(body_with_ref('Все вершины включены в дерево; построение '
                             'завершено. Суммарный вес минимального остовного '
                             'дерева равен 2+1+5+2+3 = 13. Результат приведён '
                             'на рисунке ', 'Fig2', '2', '.'))
    out.append(figure('rIdImg2', 'fig/fig_mst.png', 'fig_mst.png',
                      'Fig2', 2,
                      'Минимальное остовное дерево — результат работы '
                      'программы, отрисованный программой graphviz'))
    out.append(h2('2.4. Псевдокод'))
    out.append(code(
        'АЛГОРИТМ Прима(G, start = 0):\n'
        '    in_tree[v] <- false для всех v из V\n'
        '    tree_edges <- пустой список рёбер\n'
        '    total_weight <- 0\n'
        '\n'
        '    in_tree[start] <- true\n'
        '    frontier <- пустая очередь с приоритетом (минимум по весу)\n'
        '    для каждого ребра e = (start, u, w) из G.adjacency(start):\n'
        '        frontier.push((w, e))\n'
        '\n'
        '    пока frontier не пуста:\n'
        '        (w, e) <- frontier.top(); frontier.pop()\n'
        '        если in_tree[e.to] == true:\n'
        '            continue    // ребро ведёт в уже включённую вершину\n'
        '        in_tree[e.to] <- true\n'
        '        tree_edges.push_back(e)\n'
        '        total_weight <- total_weight + w\n'
        '        для каждого ребра next = (e.to, x, w2) из G.adjacency(e.to):\n'
        '            если in_tree[x] == false:\n'
        '                frontier.push((w2, next))\n'
        '\n'
        '    вернуть (tree_edges, total_weight)'))
    out.append(h2('2.5. Анализ сложности'))
    out.append(body('Каждая вершина включается в дерево ровно один раз, '
                    'поэтому цикл построения дерева выполняется не более |V| '
                    'раз. Каждое ребро графа попадает в очередь с приоритетом '
                    'не более двух раз (по одному разу для каждого из своих '
                    'концов), поэтому общее количество операций с кучей не '
                    'превосходит 2·|E|. Операции вставки и извлечения минимума '
                    'из двоичной кучи выполняются за O(log n), где n — '
                    'количество элементов в куче, не превосходящее |E|. '
                    'Таким образом, временная сложность алгоритма составляет '
                    'O((V + E)·log E). Поскольку в простом графе '
                    '|E| ≤ |V|·(|V|−1)/2, справедливо log E = O(log V), '
                    'поэтому сложность можно записать как O((V + E)·log V). '
                    'Затраты памяти составляют O(V + E).'))

    # ---------- 3. Инструкция пользователя ----------
    out.append(h1('3. Инструкция пользователя'))
    out.append(h2('3.1. Запуск программы'))
    out.append(body('Программа запускается из командной строки и принимает '
                    'два аргумента — имена входного и выходного файлов:'))
    out.append(code('prim.exe input.txt output.dot'))
    out.append(h2('3.2. Формат входного файла'))
    out.append(body('Входной файл содержит матрицу смежности весов графа. В '
                    'первой строке задано количество вершин N, далее следуют N '
                    'строк по N чисел. Число 0 означает отсутствие ребра, '
                    'положительное число — вес ребра. Граф неориентированный, '
                    'поэтому матрица должна быть симметричной.'))
    out.append(h2('3.3. Формат выходного файла'))
    out.append(body('Выходной файл содержит граф в формате DOT, '
                    'поддерживаемом программой graphviz. В файл записываются '
                    'все вершины графа и рёбра построенного минимального '
                    'остовного дерева с указанием весов; суммарный вес дерева '
                    'указывается в подписи графа. Такой файл можно '
                    'преобразовать в изображение командой:'))
    out.append(code('dot -Tpng output.dot -o graph.png'))

    # ---------- 4. Тестовые примеры ----------
    out.append(h1('4. Тестовые примеры'))
    out.append(body('Ниже приведены три тестовых примера. Для каждого указаны '
                    'входной файл, полученный выходной файл и суммарный вес '
                    'минимального остовного дерева.'))
    out.append(h2('4.1. Тест 1. Четыре вершины'))
    out.append(body('Входной файл:'))
    out.append(code('4\n0 1 2 3\n1 0 4 5\n2 4 0 6\n3 5 6 0'))
    out.append(body('Выходной файл:'))
    out.append(code('graph MST {\n'
                    '    label = "Minimum spanning tree (Prim\'s algorithm), '
                    'total weight = 6";\n'
                    '    node [shape = circle];\n'
                    '    0; 1; 2; 3;\n'
                    '    0 -- 1 [label = "1"];\n'
                    '    0 -- 2 [label = "2"];\n'
                    '    0 -- 3 [label = "3"];\n'
                    '}'))
    out.append(body('Суммарный вес: 6.'))
    out.append(h2('4.2. Тест 2. Пять вершин'))
    out.append(body('Входной файл:'))
    out.append(code('5\n0 2 0 6 0\n2 0 3 8 5\n0 3 0 0 7\n6 8 0 0 9\n0 5 7 9 0'))
    out.append(body('Выходной файл:'))
    out.append(code('graph MST {\n'
                    '    label = "Minimum spanning tree (Prim\'s algorithm), '
                    'total weight = 16";\n'
                    '    node [shape = circle];\n'
                    '    0; 1; 2; 3; 4;\n'
                    '    0 -- 1 [label = "2"];\n'
                    '    1 -- 2 [label = "3"];\n'
                    '    1 -- 4 [label = "5"];\n'
                    '    0 -- 3 [label = "6"];\n'
                    '}'))
    out.append(body('Суммарный вес: 16.'))
    out.append(h2('4.3. Тест 3. Шесть вершин'))
    out.append(body('Входной файл:'))
    out.append(code('6\n0 4 2 0 0 0\n4 0 1 5 0 0\n2 1 0 8 10 0\n'
                    '0 5 8 0 2 6\n0 0 10 2 0 3\n0 0 0 6 3 0'))
    out.append(body('Выходной файл:'))
    out.append(code('graph MST {\n'
                    '    label = "Minimum spanning tree (Prim\'s algorithm), '
                    'total weight = 13";\n'
                    '    node [shape = circle];\n'
                    '    0; 1; 2; 3; 4; 5;\n'
                    '    0 -- 2 [label = "2"];\n'
                    '    2 -- 1 [label = "1"];\n'
                    '    1 -- 3 [label = "5"];\n'
                    '    3 -- 4 [label = "2"];\n'
                    '    4 -- 5 [label = "3"];\n'
                    '}'))
    out.append(body('Суммарный вес: 13.'))

    # ---------- Список литературы ----------
    out.append(h1('Список литературы'))
    out.append(body('[1] Ахо А., Хопкрофт Дж., Ульман Дж. Построение и анализ '
                    'вычислительных алгоритмов. — М.: Мир, 1979.'))
    out.append(body('[2] Кормен Т., Лейзерсон Ч., Ривест Р., Штайн К. '
                    'Алгоритмы: построение и анализ. — 3-е изд. — М.: Вильямс, '
                    '2013.'))
    out.append(body('[3] Graphviz — Graph Visualization Software '
                    '[Электронный ресурс]. — URL: https://graphviz.org/ '
                    '(дата обращения: 2026).'))

    # ---------- Приложение. Листинг исходного кода ----------
    out.append(page_break())
    out.append(h1('Приложение. Листинг исходного кода'))
    out.append(body('Ниже приведён полный исходный код программы.'))
    for i, (label, relpath) in enumerate(SOURCE_FILES, 1):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            relpath)
        with open(path, encoding='utf-8') as f:
            content = f.read().rstrip('\n')
        out.append(para(run('Листинг %d — Файл %s' % (i, label), bold=True),
                        before=120, after=60))
        out.append(code(content))

    return '\n'.join(out)


def build_document_xml(body_xml):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document xmlns:w="%s" xmlns:r="%s" '
            'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/'
            'wordprocessingDrawing" '
            'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
            'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/'
            'picture">\n'
            '<w:body>\n%s\n'
            '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1134" w:right="850" w:bottom="1134" w:left="1701" '
            'w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>\n'
            '</w:body>\n</w:document>' % (W_NS, R_NS, body_xml))


def build_styles_xml():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:styles xmlns:w="%s">\n'
            '<w:docDefaults><w:rPrDefault><w:rPr>'
            '<w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/>'
            '<w:sz w:val="28"/><w:szCs w:val="28"/>'
            '<w:lang w:val="ru-RU"/></w:rPr></w:rPrDefault>'
            '<w:pPrDefault><w:pPr><w:spacing w:after="0" w:line="360" '
            'w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>\n'
            '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
            '<w:name w:val="Normal"/><w:qFormat/></w:style>\n'
            '<w:style w:type="paragraph" w:styleId="Heading1">'
            '<w:name w:val="heading 1"/><w:basedOn w:val="Normal"/>'
            '<w:next w:val="Normal"/><w:qFormat/>'
            '<w:pPr><w:outlineLvl w:val="0"/><w:spacing w:before="240" '
            'w:after="120"/><w:keepNext/></w:pPr>'
            '<w:rPr><w:b/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>'
            '</w:style>\n'
            '<w:style w:type="paragraph" w:styleId="Heading2">'
            '<w:name w:val="heading 2"/><w:basedOn w:val="Normal"/>'
            '<w:next w:val="Normal"/><w:qFormat/>'
            '<w:pPr><w:outlineLvl w:val="1"/><w:spacing w:before="240" '
            'w:after="120"/><w:keepNext/></w:pPr>'
            '<w:rPr><w:b/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr>'
            '</w:style>\n'
            '<w:style w:type="paragraph" w:styleId="Code">'
            '<w:name w:val="Code"/><w:basedOn w:val="Normal"/>'
            '<w:pPr><w:spacing w:line="240" w:lineRule="auto" w:after="0"/>'
            '<w:ind w:left="284"/></w:pPr>'
            '<w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s" w:cs="%s"/>'
            '<w:sz w:val="20"/><w:szCs w:val="20"/></w:rPr>'
            '</w:style>\n'
            '</w:styles>'
            % (W_NS, BODY_FONT, BODY_FONT, BODY_FONT,
               MONO_FONT, MONO_FONT, MONO_FONT))


def build_content_types():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Types xmlns="%s">'
            '<Default Extension="rels" ContentType="application/vnd.'
            'openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="png" ContentType="image/png"/>'
            '<Override PartName="/word/document.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.wordprocessingml.document.'
            'main+xml"/>'
            '<Override PartName="/word/styles.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
            '<Override PartName="/word/settings.xml" ContentType="application/'
            'vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
            '</Types>' % CT_NS)


def build_root_rels():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="%s">'
            '<Relationship Id="rId1" Type="%s/officeDocument" '
            'Target="word/document.xml"/>'
            '</Relationships>' % (PKG_R_NS, R_NS))


def build_doc_rels():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="%s">'
            '<Relationship Id="rId1" Type="%s/styles" Target="styles.xml"/>'
            '<Relationship Id="rId2" Type="%s/settings" Target="settings.xml"/>'
            '<Relationship Id="rIdImg1" Type="%s/image" '
            'Target="media/fig_graph.png"/>'
            '<Relationship Id="rIdImg2" Type="%s/image" '
            'Target="media/fig_mst.png"/>'
            '</Relationships>' % (PKG_R_NS, R_NS, R_NS, R_NS, R_NS))


def build_settings_xml():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:settings xmlns:w="%s"><w:updateFields w:val="true"/>'
            '</w:settings>' % W_NS)


def main():
    out_path = 'report.docx'
    z = zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED)
    z.writestr('[Content_Types].xml', build_content_types())
    z.writestr('_rels/.rels', build_root_rels())
    z.writestr('word/document.xml', build_document_xml(build_body()))
    z.writestr('word/styles.xml', build_styles_xml())
    z.writestr('word/settings.xml', build_settings_xml())
    z.writestr('word/_rels/document.xml.rels', build_doc_rels())
    z.write('fig/fig_graph.png', 'word/media/fig_graph.png')
    z.write('fig/fig_mst.png', 'word/media/fig_mst.png')
    z.close()
    print('wrote', out_path, os.path.getsize(out_path), 'bytes')


if __name__ == '__main__':
    main()
