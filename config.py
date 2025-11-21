rootdir = 'E:/Code/english_project/book'
# rootdir = '/home/kleget/Code/english_project/book' # корневая директория для анализа папки книжек
chars = r"""!"#$%&'()*+-,./:;<=>?@[\]^_`{|}~×–…“”«»—"""  # все символы, которе не могут быть отдельным символом так:" x "
PREFIX_LENGTH = 2     # Длина префикса для группировки
MAX_GROUP_SIZE = 5000  # Макс. элементов для сравнения в группе
MIN_WORD_LENGTH = 4   # Минимальная длина слова для обработки
MIN_COMMON_RATIO = 0.6
LEN_LEVENSHTEIN = 3
