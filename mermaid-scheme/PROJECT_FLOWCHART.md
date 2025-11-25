# Подробная блок-схема проекта English Project

Эта диаграмма показывает полный жизненный цикл проекта с правильной логикой двух запусков и деталями каждого этапа.

```mermaid
flowchart TD
    START[ЗАПУСК ПРОГРАММЫ python main.py]

    %% Первый проход - сбор базы non_science
    START --> FIRST_PASS[main rootdir, 1 - ПЕРВЫЙ ПРОХОД - Сбор слов из художественной литературы]
    FIRST_PASS --> CLEAN_NAMES_1[rename_files_in_directory - Очистка имен PDF файлов]
    CLEAN_NAMES_1 --> CONVERT_PDF_1[Цикл os.walk + pdf_to_txt - Конвертация PDF → TXT для non_science книг]
    CONVERT_PDF_1 --> PROCESS_NON_SCIENCE[recursion - Обработка TXT файлов non_science]

    PROCESS_NON_SCIENCE --> EXTRACT_WORDS_NS[analysand_func_dict - Извлечение слов из книги]
    EXTRACT_WORDS_NS --> READ_FILE_NS[get_txt_file - Чтение и предобработка TXT]
    READ_FILE_NS --> CLEAN_TEXT_NS[removing_anomaly - Удаление цифр, коротких слов, вставка пробелов вокруг символов]
    CLEAN_TEXT_NS --> LEMMATIZE_NS[parallel_lemmatize_mp - Параллельная лемматизация русского/английского текста]
    LEMMATIZE_NS --> FIX_HYPHENS_NS[fix_hyphenated_words - Исправление перенесённых слов с дефисами и без]
    FIX_HYPHENS_NS --> FILTER_COMMON_NS[Фильтрация слов - Исключение ОБЫЧНЫХ слов из базы non_science]
    FILTER_COMMON_NS --> GET_COMMON_WORDS_NS[select_from_table - Получение обычных слов из runonscience/ennonscience.db]
    GET_COMMON_WORDS_NS --> CLEAN_DUPLICATES_NS[algo_cleaner - Очистка от дубликатов через DSU + Levenshtein]
    CLEAN_DUPLICATES_NS --> SAVE_CLEAN_WORDS_NS[insert_many_into_table - Сохранение очищенных слов в базу non_science]
    SAVE_CLEAN_WORDS_NS --> SAVE_DELETED_WORDS_NS[insert_many_into_table - Сохранение удалённых слов в delete.db]
    SAVE_DELETED_WORDS_NS --> CREATE_NS_TABLES[create_intersection_table + create_union_table - Создание итоговых таблиц для non_science]

    %% Второй проход - обработка научных текстов
    CREATE_NS_TABLES --> SECOND_PASS[main rootdir, 2 - ВТОРОЙ ПРОХОД - Обработка научных текстов с исключением слов из non_science]
    SECOND_PASS --> CLEAN_NAMES_2[rename_files_in_directory - Очистка имен PDF файлов]
    CLEAN_NAMES_2 --> CONVERT_PDF_2[Цикл os.walk + pdf_to_txt - Конвертация PDF → TXT для научных книг]
    CONVERT_PDF_2 --> PROCESS_SCIENCE[recursion - Обработка TXT файлов науки]

    PROCESS_SCIENCE --> EXTRACT_WORDS_SC[analysand_func_dict - Извлечение слов из научной книги]
    EXTRACT_WORDS_SC --> READ_FILE_SC[get_txt_file - Чтение и предобработка TXT]
    READ_FILE_SC --> CLEAN_TEXT_SC[removing_anomaly - Очистка текста от мусора]
    CLEAN_TEXT_SC --> LEMMATIZE_SC[parallel_lemmatize_mp - Лемматизация научного текста]
    LEMMATIZE_SC --> FIX_HYPHENS_SC[fix_hyphenated_words - Исправление переносов в научном тексте]
    FIX_HYPHENS_SC --> FILTER_COMMON_SC[ВАЖНЫЙ ЭТАП ФИЛЬТРАЦИИ - Исключение слов, которые УЖЕ ЕСТЬ в non_science чтобы остались только СПЕЦИФИЧЕСКИЕ научные термины]
    FILTER_COMMON_SC --> GET_COMMON_WORDS_SC[select_from_table - Запрос к runonscience.db или ennonscience.db в зависимости от языка книги]
    GET_COMMON_WORDS_SC --> DETECT_LANGUAGE[detect_main_language - Определение языка книги для выбора правильной БД]
    DETECT_LANGUAGE --> CLEAN_DUPLICATES_SC[algo_cleaner - Очистка от дубликатов в научных терминах]
    CLEAN_DUPLICATES_SC --> SAVE_CLEAN_WORDS_SC[insert_many_into_table - Сохранение научных терминов в базу соответствующей науки math.db, physics.db, etc.]
    SAVE_CLEAN_WORDS_SC --> SAVE_DELETED_WORDS_SC[insert_many_into_table - Сохранение объединённых слов в delete.db]
    SAVE_DELETED_WORDS_SC --> CREATE_SCIENCE_TABLES[create_intersection_table + create_union_table - Создание итоговых таблиц для научной категории]

    %% Детали ключевых функций
    subgraph ALGO_CLEANER_DETAILS[ПОДРОБНОСТИ algo_cleaner]
        DSU1[Группировка слов по длине]
        DSU2[algo_DSU: Поиск похожих слов - Расстояние Левенштейна - Объединение в группы]
        DSU3[Суммирование частот объединённых слов]
        DSU4[Сохранение информации об удалённых словах]
        DSU1 --> DSU2 --> DSU3 --> DSU4
    end

    subgraph FIX_HYPHENATED_DETAILS[ПОДРОБНОСТИ fix_hyphenated_words]
        HYPH1[Удаление Unicode символов переноса xad, u200b, etc.]
        HYPH2[Обработка переносов С дефисом: од- нако → однако]
        HYPH3[Обработка переносов БЕЗ дефиса: за границей → заграницей для коротких слов]
        HYPH4[Финальная очистка одиночных переносов строк]
        HYPH1 --> HYPH2 --> HYPH3 --> HYPH4
    end

    subgraph LEMMATIZE_DETAILS[ПОДРОБНОСТИ parallel_lemmatize_mp]
        LEM1[split_into_paragraphs - Разделение текста на абзацы]
        LEM2[Параллельная обработка: lemmatize_ru_paragraph или lemmatize_en_paragraph]
        LEM3[get_lemma с lru_cache - Кэшированная лемматизация через pymorphy3/spaCy]
        LEM4[Объединение результатов всех абзацев]
        LEM1 --> LEM2 --> LEM3 --> LEM4
    end

    subgraph REMOVING_ANOMALY_DETAILS[ПОДРОБНОСТИ removing_anomaly]
        CLEAN1[Удаление слов с цифрами и чистых чисел]
        CLEAN2[Фильтрация по длине: убрать слова меньше 3 символов и больше 17 символов]
        CLEAN3[Вставка пробелов вокруг специальных символов в словах]
        CLEAN4[Очистка от мягких переносов и других артефактов PDF]
        CLEAN1 --> CLEAN2 --> CLEAN3 --> CLEAN4
    end

    subgraph INTERSECTION_DETAILS[ПОДРОБНОСТИ create_intersection_table]
        INTER1[Получение списка всех таблиц в научной БД]
        INTER2[SQL UNION ALL всех таблиц с подсчётом частот слов]
        INTER3[HAVING COUNT больше или равно кол-во таблиц - оставить только общие слова]
        INTER4[Создание таблицы word_intersection с суммированными частотами]
        INTER1 --> INTER2 --> INTER3 --> INTER4
    end

    subgraph UNION_DETAILS[ПОДРОБНОСТИ create_union_table]
        UNION1[Получение списка таблиц исключая word_intersection]
        UNION2[SQL UNION ALL всех таблиц с группировкой по словам]
        UNION3[Суммирование частот всех уникальных слов]
        UNION4[Создание таблицы global_union отсортированной по частоте]
        UNION1 --> UNION2 --> UNION3 --> UNION4
    end

    %% Связи с подграфами
    CLEAN_DUPLICATES_NS -.-> ALGO_CLEANER_DETAILS
    CLEAN_DUPLICATES_SC -.-> ALGO_CLEANER_DETAILS

    FIX_HYPHENS_NS -.-> FIX_HYPHENATED_DETAILS
    FIX_HYPHENS_SC -.-> FIX_HYPHENATED_DETAILS

    LEMMATIZE_NS -.-> LEMMATIZE_DETAILS
    LEMMATIZE_SC -.-> LEMMATIZE_DETAILS

    CLEAN_TEXT_NS -.-> REMOVING_ANOMALY_DETAILS
    CLEAN_TEXT_SC -.-> REMOVING_ANOMALY_DETAILS

    CREATE_NS_TABLES -.-> INTERSECTION_DETAILS
    CREATE_SCIENCE_TABLES -.-> INTERSECTION_DETAILS

    CREATE_NS_TABLES -.-> UNION_DETAILS
    CREATE_SCIENCE_TABLES -.-> UNION_DETAILS

    %% Финальные этапы
    CREATE_SCIENCE_TABLES --> END_PROGRAM[КОНЕЦ ПРОГРАММЫ - Вывод общего времени выполнения]
    END_PROGRAM --> STATS[Статистика обработки: количество книг, время выполнения, размеры БД]

    %% Стилизация
    classDef firstPass fill:#e1f5fe,stroke:#01579b
    classDef secondPass fill:#f3e5f5,stroke:#4a148c
    classDef processing fill:#e8f5e8,stroke:#1b5e20
    classDef details fill:#fff3e0,stroke:#e65100

    class FIRST_PASS,PROCESS_NON_SCIENCE,EXTRACT_WORDS_NS,READ_FILE_NS,CLEAN_TEXT_NS,LEMMATIZE_NS,FIX_HYPHENS_NS,FILTER_COMMON_NS,GET_COMMON_WORDS_NS,CLEAN_DUPLICATES_NS,SAVE_CLEAN_WORDS_NS,SAVE_DELETED_WORDS_NS,CREATE_NS_TABLES firstPass
    class SECOND_PASS,PROCESS_SCIENCE,EXTRACT_WORDS_SC,READ_FILE_SC,CLEAN_TEXT_SC,LEMMATIZE_SC,FIX_HYPHENS_SC,FILTER_COMMON_SC,GET_COMMON_WORDS_SC,DETECT_LANGUAGE,CLEAN_DUPLICATES_SC,SAVE_CLEAN_WORDS_SC,SAVE_DELETED_WORDS_SC,CREATE_SCIENCE_TABLES secondPass
    class CLEAN_NAMES_1,CONVERT_PDF_1,CLEAN_NAMES_2,CONVERT_PDF_2 processing
    class DSU1,DSU2,DSU3,DSU4,HYPH1,HYPH2,HYPH3,HYPH4,LEM1,LEM2,LEM3,LEM4,CLEAN1,CLEAN2,CLEAN3,CLEAN4,INTER1,INTER2,INTER3,INTER4,UNION1,UNION2,UNION3,UNION4 details
```

## Описание блок-схемы

### Основной поток выполнения:

1. **main.py** → Запуск программы с двумя проходами
2. **rename_files_in_directory** (file_processing.py) → Очистка имен PDF файлов
3. **Цикл os.walk** → Поиск всех PDF файлов
4. **pdf_to_txt** (file_processing.py) → Конвертация PDF в TXT с помощью poppler-utils
5. **reqursion** (main.py) → Рекурсивная обработка всех TXT файлов
6. **analysand_func_dict** (text_analysis.py) → Извлечение слов из книги
7. **get_txt_file** (text_analysis.py) → Чтение и предварительная обработка
8. **removing_anomaly** (text_analysis.py) → Детальная очистка текста
9. **parallel_lemmatize_mp** (lemmatize.py) → Параллельная лемматизация
10. **fix_hyphenated_words** (text_analysis.py) → Исправление перенесённых слов
11. **Фильтрация слов** → Исключение обычных слов через БД
12. **algo_cleaner** (main.py) → Очистка от дубликатов через DSU
13. **insert_many_into_table** (database_operations.py) → Сохранение результатов
14. **create_intersection_table** и **create_union_table** (create_non_science_db.py) → Итоговые таблицы

### Ключевые файлы и их роли:

- **main.py**: Оркестратор всего процесса
- **file_processing.py**: Работа с файлами (PDF→TXT, переименование)
- **text_analysis.py**: Анализ и очистка текста
- **lemmatize.py**: Лемматизация (русский/английский)
- **detect_lang.py**: Определение языка текста
- **database_operations.py**: Операции с SQLite БД
- **create_non_science_db.py**: Создание итоговых таблиц

### Важные замечания:

- Проект запускается дважды: первый проход создаёт базу обычных слов, второй — обрабатывает научные тексты
- Все PDF конвертируются в TXT один раз перед анализом
- Лемматизация происходит параллельно для ускорения
- Очистка от дубликатов использует алгоритм DSU с расстоянием Левенштейна
- Финальные таблицы (пересечение и объединение) создаются только для каждой категории

### Как использовать диаграмму:

1. Скопируйте код Mermaid в любой онлайн-редактор (например, https://mermaid.live/)
2. Или вставьте в Markdown-файл для отображения в поддерживаемых редакторах
3. Диаграмма показывает полный жизненный цикл обработки одной книги

Эта блок-схема даёт полное понимание архитектуры и потока данных в вашем проекте!
