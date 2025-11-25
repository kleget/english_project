"""
Скрипт для генерации визуальной блок-схемы проекта English Project.
Требует установки: pip install graphviz

Запуск: python generate_flowchart.py
Результат: project_flowchart.png
"""

from graphviz import Digraph

def create_flowchart():
    # Создаем направленный граф с высоким качеством
    dot = Digraph(comment='English Project Flowchart', format='png')

    # Высокое качество для PNG
    dot.attr(dpi='300')  # Высокое разрешение (300 DPI)
    dot.attr(rankdir='TB', size='16,24')  # Увеличенный размер
    dot.attr(bgcolor='white')  # Белый фон

    # Улучшенные шрифты и размеры
    dot.attr('node', shape='box', style='rounded,filled',
             fontname='DejaVu Sans', fontsize='12',
             height='0.8', width='2.5')  # Увеличенные размеры узлов
    dot.attr('edge', fontname='DejaVu Sans', fontsize='10',
             penwidth='2')  # Толще линии

    # Основные этапы
    with dot.subgraph(name='cluster_main') as main:
        main.attr(label='main.py', style='filled', color='lightblue')
        main.node('start', 'Запуск программы\nmain(rootdir, 1) и main(rootdir, 2)', fillcolor='lightgreen')
        main.node('rename', 'rename_files_in_directory()\nОчистка имен PDF файлов', fillcolor='lightyellow')
        main.node('walk', 'os.walk()\nПоиск всех PDF файлов', fillcolor='lightyellow')
        main.node('reqursion', 'reqursion()\nРекурсивная обработка TXT файлов', fillcolor='orange')

    # Конвертация PDF
    with dot.subgraph(name='cluster_pdf') as pdf:
        pdf.attr(label='file_processing.py', style='filled', color='lightcoral')
        pdf.node('pdf_to_txt', 'pdf_to_txt()\nКонвертация PDF → TXT\nс помощью poppler-utils', fillcolor='pink')

    # Анализ текста
    with dot.subgraph(name='cluster_analysis') as analysis:
        analysis.attr(label='text_analysis.py', style='filled', color='lightgreen')
        analysis.node('get_txt', 'get_txt_file()\nЧтение и предварительная обработка', fillcolor='palegreen')
        analysis.node('anomaly', 'removing_anomaly()\nОчистка текста от мусора', fillcolor='palegreen')
        analysis.node('fix_hyphen', 'fix_hyphenated_words()\nИсправление переносов слов', fillcolor='palegreen')
        analysis.node('analysand', 'analysand_func_dict()\nИзвлечение слов из книги', fillcolor='palegreen')

    # Лемматизация
    with dot.subgraph(name='cluster_lemmatize') as lem:
        lem.attr(label='lemmatize.py', style='filled', color='lightsalmon')
        lem.node('lemmatize', 'parallel_lemmatize_mp()\nПараллельная лемматизация\nрусского/английского', fillcolor='peachpuff')

    # Детали лемматизации
    with dot.subgraph(name='cluster_lemmatize_detail') as lem_det:
        lem_det.attr(label='Детали лемматизации', style='filled', color='mistyrose')
        lem_det.node('split_para', 'split_into_paragraphs()\nРазделение на абзацы', fillcolor='lavenderblush')
        lem_det.node('lem_ru', 'lemmatize_ru_paragraph()\nЛемматизация русского', fillcolor='lavenderblush')
        lem_det.node('lem_en', 'lemmatize_en_paragraph()\nЛемматизация английского', fillcolor='lavenderblush')
        lem_det.node('get_lemma', 'get_lemma()\nКэшированная лемматизация\nс pymorphy3/spaCy', fillcolor='lavenderblush')

    # Фильтрация и очистка
    with dot.subgraph(name='cluster_filter') as filt:
        filt.attr(label='Фильтрация слов (main.py)', style='filled', color='lightcyan')
        filt.node('filter', 'Фильтрация обычных слов\nиз базы non_science', fillcolor='powderblue')
        filt.node('select_db', 'select_from_table()\nПолучение обычных слов из БД', fillcolor='powderblue')

    # Алгоритм очистки
    with dot.subgraph(name='cluster_cleaner') as cleaner:
        cleaner.attr(label='Очистка дубликатов (main.py)', style='filled', color='lightgoldenrod')
        cleaner.node('algo_cleaner', 'algo_cleaner()\nОчистка от дубликатов', fillcolor='palegoldenrod')
        cleaner.node('dsu', 'algo_DSU()\nАлгоритм DSU + Levenshtein\nдля объединения похожих слов', fillcolor='palegoldenrod')

    # Детали DSU
    with dot.subgraph(name='cluster_dsu_detail') as dsu_det:
        dsu_det.attr(label='Детали DSU алгоритма', style='filled', color='wheat')
        dsu_det.node('group_len', 'Группировка слов по длине', fillcolor='moccasin')
        dsu_det.node('find_similar', 'Поиск похожих слов\n(расстояние Левенштейна)', fillcolor='moccasin')
        dsu_det.node('union_groups', 'Объединение групп слов', fillcolor='moccasin')
        dsu_det.node('sum_freq', 'Суммирование частот', fillcolor='moccasin')

    # Работа с БД
    with dot.subgraph(name='cluster_db') as db:
        db.attr(label='database_operations.py', style='filled', color='lightsteelblue')
        db.node('save_clean', 'insert_many_into_table()\nСохранение очищенных слов', fillcolor='lightblue')
        db.node('save_deleted', 'insert_many_into_table()\nСохранение удалённых слов\n(таблица delete)', fillcolor='lightblue')

    # Итоговые таблицы
    with dot.subgraph(name='cluster_final') as final:
        final.attr(label='create_non_science_db.py', style='filled', color='plum')
        final.node('intersection', 'create_intersection_table()\nСлова, встречающиеся\nво всех книгах категории', fillcolor='thistle')
        final.node('union', 'create_union_table()\nВсе уникальные слова\nкатегории с частотами', fillcolor='thistle')

    # Определение языка
    dot.node('detect_lang', 'detect_main_language()\ndetect_lang.py\nОпределение языка книги\n(русский/английский)', shape='ellipse', fillcolor='lightgray')

    # Связи основных этапов
    dot.edge('start', 'rename')
    dot.edge('rename', 'walk')
    dot.edge('walk', 'pdf_to_txt')
    dot.edge('pdf_to_txt', 'reqursion')
    dot.edge('reqursion', 'analysand')
    dot.edge('analysand', 'get_txt')
    dot.edge('get_txt', 'anomaly')
    dot.edge('anomaly', 'lemmatize')
    dot.edge('lemmatize', 'fix_hyphen')
    dot.edge('fix_hyphen', 'filter')
    dot.edge('filter', 'select_db')
    dot.edge('select_db', 'algo_cleaner')
    dot.edge('algo_cleaner', 'save_clean')
    dot.edge('save_clean', 'save_deleted')
    dot.edge('save_deleted', 'intersection', label='Только для\nпоследнего файла\nкатегории')
    dot.edge('intersection', 'union')

    # Детальные связи внутри подграфов
    dot.edge('lemmatize', 'split_para')
    dot.edge('split_para', 'lem_ru', label='Если русский')
    dot.edge('split_para', 'lem_en', label='Если английский')
    dot.edge('lem_ru', 'get_lemma')
    dot.edge('lem_en', 'get_lemma')

    dot.edge('algo_cleaner', 'group_len')
    dot.edge('group_len', 'find_similar')
    dot.edge('find_similar', 'union_groups')
    dot.edge('union_groups', 'sum_freq')

    # Детали очистки текста
    dot.edge('anomaly', 'anomaly_detail', label='Детали очистки', style='dashed')
    dot.node('anomaly_detail', 'Удаление цифр/коротких слов\nВставка пробелов вокруг символов\nОчистка от переносов (\\xad)', shape='note', fillcolor='lightcyan')

    # Детали исправления переносов
    dot.edge('fix_hyphen', 'hyphen_detail', label='Детали исправления', style='dashed')
    dot.node('hyphen_detail', 'Удаление Unicode символов\nОбработка переносов с дефисом\nОбработка переносов без дефиса\nФинальная очистка переносов строк', shape='note', fillcolor='lightcyan')

    # Конечный узел
    dot.node('end', 'Конец обработки\nВывод статистики и времени', shape='ellipse', fillcolor='lightgreen')
    dot.edge('union', 'end')

    # Дополнительные связи
    dot.edge('reqursion', 'detect_lang', label='Определение языка\nдля выбора базы', style='dotted')

    return dot

if __name__ == '__main__':
    import sys

    # Параметры качества по умолчанию
    format_type = 'png'  # Можно изменить на 'svg', 'pdf', 'ps'
    high_quality = True

    # Парсинг аргументов командной строки
    if len(sys.argv) > 1:
        if sys.argv[1] in ['svg', 'pdf', 'ps', 'png']:
            format_type = sys.argv[1]
        if len(sys.argv) > 2 and sys.argv[2] == 'low':
            high_quality = False

    print(f"Генерация блок-схемы проекта English Project в формате {format_type.upper()}...")

    # Создание диаграммы
    flowchart = create_flowchart()

    # Настройки высокого качества для PNG
    if format_type == 'png' and high_quality:
        flowchart.attr(dpi='300')  # 300 DPI для высокого качества
        flowchart.attr(size='20,30!')  # Фиксированный размер с высоким разрешением
    elif format_type in ['svg', 'pdf']:
        # Векторные форматы всегда высокого качества
        flowchart.attr(size='20,30')

    # Генерация файла
    filename = f'project_flowchart_high_quality.{format_type}'
    output_file = flowchart.render(filename, view=False, cleanup=True)

    print(f"✅ Блок-схема высокого качества сохранена в: {output_file}")
    print("💡 Советы по качеству:")
    print("   - PNG: Используйте для презентаций и веб (300 DPI)")
    print("   - SVG: Векторный формат, масштабируется без потери качества")
    print("   - PDF: Лучше всего для печати и документов")
    print(f"   - Для ещё большего качества запустите: python generate_flowchart.py {format_type}")

    # Дополнительная информация
    if format_type == 'png':
        print("   - PNG файл можно открыть в любом просмотрщике изображений")
        print("   - Для зума используйте графические редакторы (Photoshop, GIMP)")
    elif format_type == 'svg':
        print("   - SVG файл можно открыть в браузерах и векторных редакторах")
        print("   - Масштабируется без потери качества")
    elif format_type == 'pdf':
        print("   - PDF файл можно открыть в Acrobat Reader или браузерах")
        print("   - Идеален для печати и профессиональных документов")
