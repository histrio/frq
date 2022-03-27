import logging
import genanki
import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin

from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BLOCK_HEADERS = ['h3', 'h4']
URL = 'https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Czech_wordlist'
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


def get_all_blocks(node):
    if node is None:
        logger.warning("No czech block")
        return
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


def main():
    forever_cache = FileCache('/tmp/.cache/', forever=True)
    session = CacheControl(requests.Session(), forever_cache)

    resp = session.get(URL)
    soup = BeautifulSoup(resp.text, "lxml")
    base = soup.find('div', {'class': "mw-parser-output"})
    w_list = base.find('ol').find_all('li')

    model_fields = [
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

        'Participle',
        'Pronunciation',
        'Declension',
        'Etymology',
        'Etymology 1',
        'Etymology 2',
        'Etymology 3',
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
    ]

    items = ['''
                {{#%(field)s}}
                <div id="notes" class="items">
                <h2> %(field)s </h2> {{%(field)s}}
                </div>
                {{/%(field)s}}
    ''' % {'field': field} for field in model_fields[2:]]

    my_model = genanki.Model(
        1607392320,
        'Wikislovnik',
        css=STYLE,
        fields=[{"name": name} for name in model_fields],
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

    my_deck = genanki.Deck(2059400111, 'Czech Frequency Word List')

    for idx, w in enumerate(w_list):
        word = w.find('a')
        logger.info(f"{idx:0>4} {word.text}")
        w_url = urljoin(URL, word['href'])

        w_resp = session.get(w_url)
        w_soup = BeautifulSoup(w_resp.text, "lxml")

        fields = [str(idx), word.text]
        cz_begin = w_soup.find('span', id="Czech")
        data = dict(get_all_blocks(cz_begin))
        if data:
            for field in model_fields[2:]:
                fields.append(data.pop(field, ""))

            assert not data.keys(), data.keys()

            my_note = genanki.Note(
                model=my_model,
                fields=fields, sort_field='idx')
            my_deck.add_note(my_note)

    genanki.Package(my_deck).write_to_file('/output/czfrq.apkg')


if __name__ == "__main__":
    main()
