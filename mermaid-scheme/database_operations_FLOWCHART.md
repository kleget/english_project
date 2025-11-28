# Блок-схема работы database_operations.py

## 🎯 Основной поток создания global_union с переводами

```mermaid
flowchart TD
    Start([Начало: create_union_table_query]) --> CheckDB{БД существует?}
    CheckDB -->|Нет| Error1[❌ Ошибка: БД не найдена]
    CheckDB -->|Да| DropTable[Удалить старую global_union]
    
    DropTable --> CreateUnion[Создать таблицу global_union<br/>word, count]
    CreateUnion --> CreateTrans[Создать таблицу translations<br/>word, count, translation]
    
    CreateTrans --> CollectWords[Собрать все слова из всех таблиц<br/>UNION ALL + GROUP BY + SUM]
    CollectWords --> SortWords[Сортировать по count DESC]
    SortWords --> InsertAll[Вставить все слова в global_union]
    
    InsertAll --> SelectTop[Выбрать топ N% слов<br/>по умолчанию 25%]
    SelectTop --> CheckCache[🔍 Проверить глобальный кэш<br/>translations_cache.db]
    
    CheckCache --> SplitWords{Разделить слова}
    SplitWords -->|В кэше| CachedWords[Слова из кэша]
    SplitWords -->|Не в кэше| NewWords[Слова для перевода]
    
    CachedWords --> MergeResults[Объединить результаты]
    NewWords --> Translate[🔁 Перевести через API]
    Translate --> SaveGlobalCache[💾 Сохранить в глобальный кэш]
    SaveGlobalCache --> MergeResults
    
    MergeResults --> UpdateLocal[Обновить локальную таблицу<br/>translations в научной БД]
    UpdateLocal --> Commit[Сохранить изменения]
    Commit --> End([✅ Готово])
    
    Error1 --> End
    
    style Start fill:#90EE90
    style End fill:#90EE90
    style CheckCache fill:#87CEEB
    style Translate fill:#FFD700
    style SaveGlobalCache fill:#FFD700
    style Error1 fill:#FF6B6B
```

---

## 🔄 Детальная схема работы с кэшем

```mermaid
flowchart LR
    A[Список слов для перевода] --> B{Проверить<br/>глобальный кэш}
    
    B -->|Слово найдено| C[Использовать из кэша]
    B -->|Слова нет| D[Добавить в список<br/>для перевода]
    
    C --> E[Объединить результаты]
    D --> F[Перевести через API]
    F --> G[Сохранить в<br/>глобальный кэш]
    G --> E
    
    E --> H[Сохранить в<br/>локальную таблицу]
    
    style B fill:#87CEEB
    style F fill:#FFD700
    style G fill:#FFD700
    style C fill:#90EE90
```

---

## 📊 Схема создания таблицы пересечения

```mermaid
flowchart TD
    Start([create_intersection_table_query]) --> CheckDB{БД существует?}
    CheckDB -->|Нет| Error[❌ Ошибка]
    CheckDB -->|Да| DropOld[Удалить старую<br/>word_intersection]
    
    DropOld --> UnionAll[Объединить все таблицы<br/>с пометкой источника]
    UnionAll --> GroupBy[Группировать по слову<br/>COUNT источников]
    
    GroupBy --> Filter{Слово есть<br/>во всех таблицах?}
    Filter -->|Да| SumCounts[Суммировать count<br/>для этих слов]
    Filter -->|Нет| Skip[Пропустить]
    
    SumCounts --> CreateTable[Создать таблицу<br/>word_intersection]
    CreateTable --> Commit[Сохранить]
    Commit --> End([✅ Готово])
    
    Error --> End
    Skip --> End
    
    style Start fill:#90EE90
    style End fill:#90EE90
    style Filter fill:#87CEEB
    style Error fill:#FF6B6B
```

---

## 💾 Схема работы с глобальным кэшем

```mermaid
flowchart TD
    Start([Запрос переводов]) --> Init{Кэш существует?}
    Init -->|Нет| CreateCache[Создать translations_cache.db<br/>и таблицу]
    Init -->|Да| QueryCache
    CreateCache --> QueryCache[Запрос: SELECT word, translation<br/>WHERE word IN ...]
    
    QueryCache --> Return[Вернуть словарь<br/>{word: translation}]
    Return --> End([✅ Готово])
    
    SaveStart([Сохранение переводов]) --> Init2{Кэш существует?}
    Init2 -->|Нет| CreateCache2[Создать кэш]
    Init2 -->|Да| Insert
    CreateCache2 --> Insert[INSERT OR IGNORE<br/>в translations_cache]
    Insert --> End2([✅ Готово])
    
    style Start fill:#90EE90
    style End fill:#90EE90
    style SaveStart fill:#90EE90
    style End2 fill:#90EE90
    style QueryCache fill:#87CEEB
    style Insert fill:#FFD700
```

---

## 🔀 Схема работы между разными научными БД

```mermaid
flowchart LR
    subgraph "Первая обработка"
        A1[biology.db] --> B1[1000 слов]
        B1 --> C1[Перевести 250]
        C1 --> D1[Сохранить в<br/>глобальный кэш]
    end
    
    subgraph "Вторая обработка"
        A2[physics.db] --> B2[1000 слов]
        B2 --> C2[Проверить кэш]
        C2 --> D2{200 в кэше<br/>50 новых}
        D2 --> E2[Перевести только 50]
        E2 --> F2[Сохранить 50<br/>в глобальный кэш]
    end
    
    subgraph "Глобальный кэш"
        GC[translations_cache.db<br/>250 переводов]
    end
    
    D1 --> GC
    C2 --> GC
    F2 --> GC
    
    style GC fill:#FFD700
    style D1 fill:#90EE90
    style E2 fill:#90EE90
```

---

## 📝 Упрощённая схема основных функций

```mermaid
graph TB
    subgraph "Базовые операции"
        A[create_table<br/>Создать таблицу]
        B[insert_many_into_table<br/>Вставить данные]
        C[select_from_table<br/>Выполнить запрос]
    end
    
    subgraph "Аналитические таблицы"
        D[create_intersection_table_query<br/>Слова во всех книгах]
        E[create_union_table_query<br/>Все слова + переводы]
    end
    
    subgraph "Работа с переводами"
        F[get_cached_translations<br/>Проверить кэш]
        G[save_to_global_translations_cache<br/>Сохранить в кэш]
        H[get_word_with_translation<br/>Получить слово + перевод]
    end
    
    E --> F
    E --> G
    E --> H
    
    style E fill:#FFD700
    style F fill:#87CEEB
    style G fill:#87CEEB
```

---

## 🎓 Легенда блок-схем

- 🟢 **Зелёный** — начало/конец, успешное завершение
- 🔵 **Голубой** — проверки, условия
- 🟡 **Жёлтый** — операции с переводами, API
- 🔴 **Красный** — ошибки

---

## 📌 Ключевые моменты

1. **Глобальный кэш** используется всеми научными БД
2. **Локальная таблица** содержит переводы только для этой науки
3. **Переводятся только топ N%** слов (экономия токенов)
4. **Кэш сохраняется** между запусками программы

