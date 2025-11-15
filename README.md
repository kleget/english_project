This is my python project to learn English. I am doing this to gain data science skills.

pip install pdfminer

pip install pdfminer.six

pip install spacy

pip install pymorphy3

pip install python-Levenshtein

pip install termcolor

pip install pdfreader

pip install poppler-utils

для виндовс скачиваем файлик:
https://github.com/facebookresearch/fastText/issues/1277#issuecomment-1955988614

устанавливаем файлик

pip install other/fasttext-0.9.2-cp311-cp311-win_amd64.whl

для linux:

pip install fasttext


python -m spacy download en_core_web_sm

sudo apt-get install poppler-utils 

в проекте должна быть пустая папка database
книги хранятся в папке book, в которой должны быть папки pdf и txt а уже в них папки по наукам, а в них сами книги

wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin

в файле config.py укажи правильный rootdir до папки /book

если винда, то заходи на сайт 
https://github.com/oschwartz10612/poppler-windows/releases/
скачивай последнюю версию, распаковывый куданибудь в статическое место
и добавляй \poppler\Library\bin в Path