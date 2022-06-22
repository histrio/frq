import os
import logging
import hashlib
from urllib.parse import urljoin

import genanki
from bs4 import BeautifulSoup, NavigableString
from requests_cache import CachedSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOURCES = {}
CACHE = os.path.expanduser('~/.cache/wikifrq/')

BLOCK_HEADERS = ['h3', 'h4']

FIELDS = [
    'idx',
    'Word',

    'Pronoun',
    'Preposition',
    'Conjunction',
    'Verb',
    'Verb form',
    'Noun',
    'Noun 1',
    'Noun 2',
    'Adverb',
    'Adverb 1',
    'Adverb 2',
    'Interjection',
    'Adjective',
    'Numeral',
    'Particle',
    'Letter',
    'Postposition',

    'Participle',
    'Pronunciation',
    'Pronunciation 1',
    'Pronunciation 2',
    'Declension',
    'Etymology',
    'Etymology 1',
    'Etymology 2',
    'Etymology 3',
    'Etymology 4',
    'Etymology 5',
    'Etymology 6',
    'Etymology 7',
    'Etymology 8',
    'Etymology 9',
    'Etymology 10',
    'Proper noun',
    'Synonyms',
    'Antonyms',
    'Hypernyms',
    'Hyponyms',
    'Meronyms',
    'Anagrams',
    'Contraction',
    'References',
    'Descendants',
    'Related terms',
    'See also',
    'Further reading',
    'Derived terms',
    'Usage notes',
    'Phrases',
    'Phrase',
    'Conjugation',
    'Alternative forms',
    'Coordinate terms',
    'External links',
    'Usage Note',
    'Quotations',
    'Determiner',
    'Translations',
    'Number',
    'Article',
    'Symbol',
    'Punctuation mark',
    'Gallery',
    'Holonyms',
    'Prepositional phrase',
    'Statistics',
    'Troponyms',
    'Infix',
    'Notes',
    'Abbreviations',
    'Prefix',
    'Proverbs',
    'Reference',
]
STYLE = '''
    .card {
        font-family: helvetica, arial, sans-serif;
        font-size: 14px;
        text-align: left;
        color:#1d2129;
        background-color:#e9ebee;
    }


    .bar{
        border-radius: 3px;
        border-bottom: 1px solid #29487d;
        color: #fff;
        padding: 5px;
        text-decoration:none;
        font-size: 12px;
        color: #fff;
        font-weight: bold;
    }

    .head{
        padding-left:25px;
        background: #365899 url(_clipboard.png) no-repeat
    }

    .foot{
        padding-right:25px;
        text-align:right;
        background: #365899 url(_cloud.png) no-repeat right
    }

    .section {
        border: 1px solid;
        border-color: #e5e6e9 #dfe0e4 #d0d1d5;
        border-radius: 3px;
        background-color: #fff;
        position: relative;
        margin: 5px 0;
    }

    .expression{
        font-size: 45px;
        margin: 0 12px;
        padding: 10px 0 8px 0;
        border-bottom: 1px solid #e5e5e5;
    }

    .items{
        border-top: 1px solid #e5e5e5;
        font-size: 16px;
        margin: 0 12px;
        padding: 10px 0 8px 0;
    }

    #url a{
    text-decoration:none;
    font-size: 12px;
    color: #fff;
    font-weight: bold;
    }
'''


def remove_edit_href(node):
    edit_span = node.find('span', {'class': 'mw-editsection'})
    if edit_span:
        edit_span.decompose()


def regsource(code, name):
    def wrapper(clbl):
        SOURCES[code] = (name, clbl)
        def _wrapper(*args, **kwargs):
            return clbl(*args, **kwargs)
        return _wrapper
    return wrapper


@regsource('se', 'Serbo-Croatian')
def iterate_srb_words(session):
    url = 'https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Serbian_wordlist'
    resp = session.get(url)
    soup = BeautifulSoup(resp.content, "lxml")
    base = soup.find('table')
    for item in base.find_all('tr'):
        yield item.find('th').text.strip()

@regsource('en', 'English')
def iterate_eng_words(session):
    url = 'https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/TV/2006/'
    for part in ['1-1000', '1001-2000']:
        resp = session.get(url + part)
        soup = BeautifulSoup(resp.text, "lxml")
        base = soup.find('table')
        for item in base.find_all('tr'):
            #import pdb; pdb.set_trace()
            href = item.find('a')
            if href:
                yield href.text.strip()
           # yield item.find('th').text.strip()

@regsource('cz', 'Czech')
def iterate_cz_words(session):
    url = 'https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Czech_wordlist'
    resp = session.get(url)
    soup = BeautifulSoup(resp.content, "lxml")
    base = soup.find('div', {'class': "mw-parser-output"})
    for item in base.find('ol').find_all('li'):
        yield item.find('a').content.strip()


def get_all_blocks(node):
    node = node.find_next(BLOCK_HEADERS)
    remove_edit_href(node)
    head, body = node.text, ""
    while node.nextSibling and node.nextSibling.name != 'hr':
        node = node.nextSibling
        if isinstance(node, NavigableString):
            continue
        if node.name in BLOCK_HEADERS:
            yield head, body
            remove_edit_href(node)
            head, body = node.text, ""
        else:
            body += str(node)
    yield head, body


def generate(args):
    session = CachedSession('http_cache', backend='filesystem', use_cache_dir=True)
    items = ['''
                {{#%(field)s}}
                <div id="notes" class="items">
                <h2> %(field)s </h2> {{%(field)s}}
                </div>
                {{/%(field)s}}
    ''' % {'field': field} for field in FIELDS[2:]]

    model_name = f'model-frq-{args.lang}'
    model_id = int(hashlib.sha256(model_name.encode('utf-8')).hexdigest(), 16) % 10**8
    my_model = genanki.Model(
        model_id,
        'Wikislovnik',
        css=STYLE,
        fields=[{"name": name} for name in FIELDS],
        templates=[{
            'name': 'Card 1',
            'qfmt': '''
                <div class="bar head">Deck : {{Deck}}
                </div>
                <div class="section">
                <div class="expression">{{Word}}</div>
                </div>
            ''',
            'afmt': '''
                {{FrontSide}}
                <div class="section">
                    %s
                </div>
                <div class="bar foot">
                  <div id="url"><a href=https://en.wiktionary.org/wiki/{{ Word }}#Czech>Wikislovnik</a></div>
                </div>
            ''' % '\n'.join(items),
        }])


    name, w_list = SOURCES[args.lang]
    deck_name = f'deck-frq-{args.lang}'
    deck_id = int(hashlib.sha256(deck_name.encode('utf-8')).hexdigest(), 16) % 10**8
    my_deck = genanki.Deck(deck_id, f'{name} Frequency Word List')
    for idx, word in enumerate(w_list(session)):
        w_url = urljoin('https://en.wiktionary.org/wiki/', word)
        logger.info(f"{idx:0>4} {word}")

        w_resp = session.get(w_url, stream=False)
        w_soup = BeautifulSoup(w_resp.content, "lxml")

        fields = [str(idx), word]
        _begin = w_soup.find('span', id=name)
        if _begin is None:
            logger.warning(f"No block `{name}`")
            continue
        data = dict(get_all_blocks(_begin))
        if data:
            for field in FIELDS[2:]:
                fields.append(data.pop(field, ""))

            assert not data.keys(), data.keys()
            my_note = genanki.Note(
                model=my_model,
                fields=fields, sort_field='idx')
            my_deck.add_note(my_note)

    output_filename = os.path.join(os.getcwd(), f'frq-{args.lang}.apkg')
    genanki.Package(my_deck).write_to_file(output_filename)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('lang', choices=SOURCES.keys())
    generate(parser.parse_args())

if __name__ == "__main__":
    main()
