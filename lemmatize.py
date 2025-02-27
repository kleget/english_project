import spacy
import pymorphy3
import re

nlp = spacy.load("en_core_web_sm")
nlp.max_length = 40000000 # or higher
def get_infinitiv(word):
    return word

#
# def tokenize(text):
#     return re.findall(r'\w+', text)

def lemmatize_text_ru(text):
    words = re.findall(r'\w+', text) # tokenize(text)
    morph = pymorphy3.MorphAnalyzer()
    lemmatized_words = [morph.parse(word)[0].normal_form for word in words]
    return " ".join(lemmatized_words)

def lemmatize_text_en(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc])

# text = 'The boys were playing with a big beautiful ball'
# print(lemmatize_text(text))
