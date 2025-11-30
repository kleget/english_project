```mermaid
%% Auto-generated Mermaid call graph.
%% View in VS Code (Markdown preview with Mermaid support) or mermaid.live.
flowchart TB
  subgraph "config"
    direction TB
    config["config()"]
  end
  subgraph "database_aggregation"
    direction TB
    create_intersection_table["create_intersection_table(db_name, result_table)"]
    create_union_table["create_union_table(db_name, result_table)"]
  end
  subgraph "database_operations"
    direction TB
    create_table["create_table(db_name, table_name)<br/>creating table"]
    insert_many_into_table["insert_many_into_table(db_name, table_name, data)"]
    select_from_table["select_from_table(db_name, request)"]
    create_intersection_table_query["create_intersection_table_query(tables, db_path, result_table)"]
    create_translations_table["create_translations_table(cursor, table_name)<br/>create translations table"]
    create_union_table_query["create_union_table_query(tables, db_path, result_table, translation_threshold)<br/>build union table with translations"]
    get_cached_translations["get_cached_translations(words, use_global_cache)"]
    save_to_global_translations_cache["save_to_global_translations_cache(translations)"]
    get_word_with_translation["get_word_with_translation(cursor, word, union_table)"]
    create_processed_books_table["create_processed_books_table(db_name)"]
    is_book_processed["is_book_processed(db_name, book_path)"]
    mark_book_as_processed["mark_book_as_processed(db_name, book_path, word_count)"]
  end
  subgraph "detect_lang"
    direction TB
    detect_main_language["detect_main_language(file_path, num_samples, sample_size, model_path)"]
  end
  subgraph "file_processing"
    direction TB
    pdf_to_txt["pdf_to_txt(root, name_file)"]
    rename_files_in_directory["rename_files_in_directory(directory)"]
    get_directory_structure["get_directory_structure(rootdir)"]
    get_all_folders["get_all_folders(structure, current_path)"]
  end
  subgraph "lemmatize"
    direction TB
    init_spacy["init_spacy()"]
    get_lemma["get_lemma(word)"]
    lemmatize_ru_paragraph["lemmatize_ru_paragraph(paragraph)"]
    lemmatize_en_paragraph["lemmatize_en_paragraph(paragraph)"]
    split_into_paragraphs["split_into_paragraphs(text)"]
    parallel_lemmatize_mp["parallel_lemmatize_mp(text, lang, max_workers)"]
  end
  subgraph "main"
    direction TB
    initialize_all_databases["initialize_all_databases()"]
    print_all_files_from_rootdir["print_all_files_from_rootdir()"]
    reqursion["reqursion(all_files_from_rootdir, start_num)"]
    algo_cleaner["algo_cleaner(sorted_analysand)"]
    algo_DSU["algo_DSU(sorted_analysand, length_groups)"]
    main_fn["main(rootdir, start_num)"]
  end
  subgraph "text_analysis"
    direction TB
    fix_hyphenated_words["fix_hyphenated_words(text)"]
    removing_anomaly["removing_anomaly(text_from_book, lang)"]
    get_txt_file["get_txt_file(name_file)"]
    analysand_func_dict["analysand_func_dict(name_file)"]
    analysand_func_list["analysand_func_list(name_file)"]
  end
  subgraph "translation_utils"
    direction TB
    detect_language["detect_language(word)"]
    translate_batch["translate_batch(words, batch_size)"]
  end

  initialize_all_databases --> create_processed_books_table
  initialize_all_databases --> is_book_processed
  initialize_all_databases --> mark_book_as_processed
  print_all_files_from_rootdir --> get_directory_structure
  print_all_files_from_rootdir --> get_all_folders
  reqursion --> is_book_processed
  reqursion --> get_common
  reqursion --> algo_cleaner
  reqursion --> insert_many_into_table
  reqursion --> create_intersection_table
  reqursion --> create_union_table
  algo_cleaner --> algo_DSU
  main_fn --> rename_files_in_directory
  main_fn --> pdf_to_txt
  main_fn --> reqursion
  fix_hyphenated_words --> removing_anomaly
  removing_anomaly --> parallel_lemmatize_mp
  removing_anomaly --> detect_language
  get_txt_file --> fix_hyphenated_words
  get_txt_file --> removing_anomaly
  analysand_func_dict --> get_txt_file
  analysand_func_list --> get_txt_file
  translate_batch --> detect_language
  create_intersection_table_query --> create_table
  create_union_table_query --> create_translations_table
  create_union_table_query --> get_cached_translations
  create_union_table_query --> save_to_global_translations_cache
  save_to_global_translations_cache --> init_spacy
  get_cached_translations --> init_spacy
  get_word_with_translation --> init_spacy
  parallel_lemmatize_mp --> split_into_paragraphs
  lemmatize_ru_paragraph --> get_lemma
  lemmatize_en_paragraph --> init_spacy
  pdf_to_txt --> rename_files_in_directory
  reqursion --> detect_main_language

  %% Legend
  note1["function(args)<br/>first doc line"]:::legend
  classDef legend fill:#fef3c7,stroke:#facc15,color:#1f2937;
```
