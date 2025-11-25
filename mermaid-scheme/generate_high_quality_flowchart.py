"""
Улучшенный скрипт для генерации блок-схемы максимального качества.
Создает диаграммы в разных форматах с оптимизированными настройками.

Использование:
python generate_high_quality_flowchart.py [format] [quality]

Форматы: png, svg, pdf, ps (по умолчанию: png)
Качество: high, ultra (по умолчанию: high)

Примеры:
python generate_high_quality_flowchart.py png high    # Стандартное высокое качество
python generate_high_quality_flowchart.py svg ultra   # Векторное с максимальным качеством
python generate_high_quality_flowchart.py pdf ultra   # PDF для печати
"""

from graphviz import Digraph
import sys

def create_ultra_quality_flowchart():
    """
    Создает диаграмму с максимальными настройками качества
    """
    dot = Digraph(comment='English Project Ultra Quality Flowchart')

    # Максимальные настройки качества
    dot.attr(
        dpi='600',  # Сверхвысокое разрешение
        rankdir='TB',
        size='24,36!',  # Большой фиксированный размер
        bgcolor='white',
        pad='0.5',  # Отступы
        nodesep='1.0',  # Расстояние между узлами
        ranksep='1.5'   # Расстояние между рядами
    )

    # Оптимизированные шрифты и стили
    dot.attr('node',
             shape='box',
             style='rounded,filled',
             fontname='DejaVu Sans',
             fontsize='14',
             height='1.0',
             width='3.0',
             penwidth='3',
             margin='0.3,0.2'
             )

    dot.attr('edge',
             fontname='DejaVu Sans',
             fontsize='12',
             penwidth='3',
             arrowsize='1.5'
             )

    # Основные этапы с улучшенными цветами
    with dot.subgraph(name='cluster_main') as main:
        main.attr(label='main.py', style='filled', color='lightblue', penwidth='3')
        main.node('start', 'Запуск программы\npython main.py', fillcolor='lightgreen', penwidth='3')
        main.node('first_pass', 'main(rootdir, 1)\nПЕРВЫЙ ПРОХОД\nСбор базы non_science', fillcolor='lightblue', penwidth='3')
        main.node('second_pass', 'main(rootdir, 2)\nВТОРОЙ ПРОХОД\nОбработка науки\nс фильтрацией', fillcolor='lightcoral', penwidth='3')

    # PDF обработка
    with dot.subgraph(name='cluster_pdf') as pdf:
        pdf.attr(label='file_processing.py', style='filled', color='lightcoral', penwidth='3')
        pdf.node('clean_names', 'rename_files_in_directory()\nОчистка имен PDF файлов', fillcolor='pink', penwidth='3')
        pdf.node('pdf_convert', 'pdf_to_txt()\nКонвертация PDF → TXT\npoppler-utils', fillcolor='pink', penwidth='3')

    # Анализ текста
    with dot.subgraph(name='cluster_analysis') as analysis:
        analysis.attr(label='text_analysis.py', style='filled', color='lightgreen', penwidth='3')
        analysis.node('read_txt', 'get_txt_file()\nЧтение TXT файла', fillcolor='palegreen', penwidth='3')
        analysis.node('clean_text', 'removing_anomaly()\nОчистка текста\nот мусора и артефактов', fillcolor='palegreen', penwidth='3')
        analysis.node('lemmatize', 'parallel_lemmatize_mp()\nПараллельная лемматизация\nрусского/английского', fillcolor='palegreen', penwidth='3')
        analysis.node('fix_hyphens', 'fix_hyphenated_words()\nИсправление перенесённых слов', fillcolor='palegreen', penwidth='3')
        analysis.node('extract_words', 'analysand_func_dict()\nИзвлечение слов и частот', fillcolor='palegreen', penwidth='3')

    # Фильтрация и очистка
    with dot.subgraph(name='cluster_filter') as filt:
        filt.attr(label='Фильтрация (main.py)', style='filled', color='lightcyan', penwidth='3')
        filt.node('filter_words', 'Фильтрация слов\nИСКЛЮЧЕНИЕ слов из non_science', fillcolor='powderblue', penwidth='3')
        filt.node('detect_lang', 'detect_main_language()\nОпределение языка книги', fillcolor='powderblue', penwidth='3')
        filt.node('get_common', 'select_from_table()\nЗапрос к БД non_science', fillcolor='powderblue', penwidth='3')
        filt.node('clean_duplicates', 'algo_cleaner() + algo_DSU()\nОчистка дубликатов\nDSU + Levenshtein', fillcolor='powderblue', penwidth='3')

    # Работа с БД
    with dot.subgraph(name='cluster_db') as db:
        db.attr(label='database_operations.py', style='filled', color='lightsteelblue', penwidth='3')
        db.node('save_clean', 'insert_many_into_table()\nСохранение терминов\nв БД категории', fillcolor='lightblue', penwidth='3')
        db.node('save_deleted', 'insert_many_into_table()\nСохранение объединённых слов\nв delete.db', fillcolor='lightblue', penwidth='3')

    # Итоговые таблицы
    with dot.subgraph(name='cluster_final') as final:
        final.attr(label='create_non_science_db.py', style='filled', color='plum', penwidth='3')
        final.node('intersection', 'create_intersection_table()\nОбщие слова всех книг\nкатегории (пересечение)', fillcolor='thistle', penwidth='3')
        final.node('union', 'create_union_table()\nВсе уникальные слова\nкатегории (объединение)', fillcolor='thistle', penwidth='3')

    # Связи с правильной логикой
    dot.edge('start', 'first_pass')
    dot.edge('first_pass', 'clean_names')
    dot.edge('clean_names', 'pdf_convert')
    dot.edge('pdf_convert', 'read_txt')
    dot.edge('read_txt', 'clean_text')
    dot.edge('clean_text', 'lemmatize')
    dot.edge('lemmatize', 'fix_hyphens')
    dot.edge('fix_hyphens', 'extract_words')
    dot.edge('extract_words', 'filter_words', label='ФИЛЬТРАЦИЯ:\nисключение обычных слов')
    dot.edge('filter_words', 'detect_lang')
    dot.edge('detect_lang', 'get_common')
    dot.edge('get_common', 'clean_duplicates')
    dot.edge('clean_duplicates', 'save_clean')
    dot.edge('save_clean', 'save_deleted')
    dot.edge('save_deleted', 'intersection', label='Для последнего\nфайла категории')
    dot.edge('intersection', 'union')

    # Переход ко второму проходу
    dot.edge('union', 'second_pass', style='bold', color='red', label='КОНЕЦ ПЕРВОГО ПРОХОДА\nНАЧАЛО ВТОРОГО ПРОХОДА')
    dot.edge('second_pass', 'clean_names', style='dashed', color='red')

    # Финальный узел
    dot.node('end', 'КОНЕЦ ОБРАБОТКИ\nВывод статистики и времени\nВсе БД готовы к использованию',
             shape='ellipse', fillcolor='lightgreen', penwidth='3', fontsize='16')
    dot.edge('union', 'end')

    return dot

def main():
    # Параметры по умолчанию
    format_type = 'png'
    quality = 'high'

    # Парсинг аргументов
    if len(sys.argv) > 1:
        if sys.argv[1] in ['png', 'svg', 'pdf', 'ps']:
            format_type = sys.argv[1]
    if len(sys.argv) > 2:
        if sys.argv[2] in ['high', 'ultra']:
            quality = sys.argv[2]

    print(f"🎨 Генерация блок-схемы максимального качества...")
    print(f"📁 Формат: {format_type.upper()}")
    print(f"⭐ Качество: {quality}")

    # Создание диаграммы
    if quality == 'ultra':
        flowchart = create_ultra_quality_flowchart()
    else:
        # Импорт из основного скрипта
        from generate_flowchart import create_flowchart
        flowchart = create_flowchart()

    # Настройки качества для разных форматов
    if format_type == 'png':
        if quality == 'ultra':
            flowchart.attr(dpi='600', size='30,45!')
        else:
            flowchart.attr(dpi='300', size='20,30!')
    elif format_type in ['svg', 'pdf']:
        flowchart.attr(size='25,40')

    # Генерация файла
    filename = f'project_flowchart_{quality}_quality_{format_type}'
    output_file = flowchart.render(filename, view=False, cleanup=True)

#     print("✅ УСПЕШНО!"    print(f"📄 Файл сохранён: {output_file}")
#     print("
# 🎯 Характеристики качества:"    if format_type == 'png':
#         print(f"   • Разрешение: {'600' if quality == 'ultra' else '300'} DPI")
#         print("   • Формат: Растровый, идеален для презентаций"    elif format_type == 'svg':
#         print("   • Формат: Векторный, масштабируется без потери качества")
#         print("   • Идеален для веб и редактирования"    elif format_type == 'pdf':
#         print("   • Формат: Векторный, оптимизирован для печати")
#         print("   • Лучший выбор для документов и профессиональной печати"
#     print("
# 💡 Советы:"    print("   • PNG: Открывайте в просмотрщиках изображений"    print("   • SVG/PDF: Открывайте в браузерах или Adobe Reader"    print("   • Для зума используйте векторные редакторы (Inkscape, Illustrator)"
    # Дополнительная информация о размерах
    import os
    if os.path.exists(output_file):
        size_mb = os.path.getsize(output_file) / (1024 * 1024)
        # print(".2f"
if __name__ == '__main__':
    main()
