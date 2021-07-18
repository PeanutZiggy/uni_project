import spacy
import itertools
from spacy.tokenizer import Tokenizer
from collections import Counter
from langdetect import detect
from googlesearch import search
import requests
from bs4 import BeautifulSoup

# loads the trained model
nlp = spacy.load('en_core_web_lg')

stopwords = spacy.lang.en.stop_words.STOP_WORDS

# function to extract text from a provided weblink


def info_extractor(weblink):

    resp = requests.get(weblink)

    soup = BeautifulSoup(resp.text, 'html.parser')

    info = []
    article = soup.find('article')

    # checks if there is an HTML article tag to extract text from its children p tags
    # or extracts directly from the p tags
    # also checks if the text extracted from each tag is not very short (not below 200 characters)
    if article:
        ps = article.findChildren('p')
        for p in ps:
            if len(p.get_text()) > 200:
                info.append(p.get_text())
                continue
            else:
                continue
    else:
        for x in soup.find_all('p'):
            if len(x.get_text()) > 200:
                info.append(x.get_text())
                continue
            else:
                continue
    print(list(set(info))[0])
    return list(set(info))

# function to process provided text


def process_text(text):
    doc = nlp(text)

    lemmatized = []
    # removes stopwords, punctioation and pronouns by checking each word
    for token in doc:
        if token.text in stopwords:
            continue
        if token.is_punct:
            continue
        if token.lemma_ == '-PRON-':
            continue
        # adds the lemma of the word
        lemmatized.append(token.lemma_)

    # provides the lemmatized text as a whole string instead of a list
    whole_text = " ".join(lemmatized)

    return whole_text

# calculates the similarity between 2 lemmatized texts


def calculate_similarity(text1, text2):
    t1 = nlp(process_text(text1))
    t2 = nlp(process_text(text2))

    return t1.similarity(t2)

# finds weblinks based on search word provided by the user


def get_links(search_word):
    social_links = ['facebook.com/', 'twitter.com/',
                    'youtube.com/', 'instagram.com/']

    links = [url for url in search(search_word, num_results=10)]

    # removes any links that are part of the social websites
    for s in social_links:
        for l in links:
            if s in l:
                links.remove(l)
                print('Link removed: ', l)
    print("\nFinal list of links: ", links)
    return links


def main(word):
    result = []

    links = get_links(word)

    result.append(links)

    # extracts the text from the websites
    info = {}
    i = 0
    for link in links:
        try:
            info[i] = info_extractor(link)
            i += 1
        except:
            continue

    # uses a copy of the dictionary with text so it can avoid runtime errors
    # checks if there is an empty text value and if all of them are in Enlgish
    for k in info.copy():
        if not info[k]:
            #print('empty value')
            info.pop(k)
        elif detect(str(info.get(k))) != 'en':
            #print('content not in english')
            info.pop(k)
        else:
            continue

    # removes nested lists from extracted text
    info2 = {}
    for key, val in info.items():
        info2[key] = ' '.join(val)

    # checks the similarity between all text elements in the dictionary
    # uses the itertools.combinations library to create all combinations without duplicates
    # if the similarity score is above 97%, removes one of the elements
    keys = []
    for k1, k2 in itertools.combinations(info2, 2):
        similarity = calculate_similarity(info2.get(k1), info2.get(k2))
        # print(similarity)
        if similarity >= 0.97:
            keys.append(k2)

    for k in keys:
        try:
            info.pop(k)
        except:
            # print('key not found')
            continue

    # creates a list with only the values
    # and then uses it to create a string with new line character between each value
    text1 = list(itertools.chain.from_iterable(info.values()))
    text = '\n'.join(str(txt) for txt in text1)

    result.append(text)

    # common words
    word_freq = Counter(text.split())
    common_words = word_freq.most_common(100)

    # named entity recognition
    ner = [(ent.text, ent.label_) for ent in nlp(text).ents]

    result.append(common_words)
    result.append(ner)
    return result


#print("--- %s seconds ---" % (time.time() - start_time))
