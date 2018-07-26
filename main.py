import genanki
import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin

BLOCK_HEADERS = ['h3', 'h4']


def remove_edit_href(node):
    edit_span = node.find('span', {'class': 'mw-editsection'})
    if edit_span:
        edit_span.decompose()


def get_all_blocks(node):
    if node is None:
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
    url = 'https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Czech_wordlist'
    css = '''.card {
         font-family: arial;
         font-size: 20px;
         color: black;
         background-color: white;
    }'''
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "lxml")
    base = soup.find('div', {'class': "mw-parser-output"})
    w_list = base.find('ol').find_all('li')

    model_fields = [
        {'name': 'idx'},

        {'name': 'Word'},

        {'name': 'Pronoun'},
        {'name': 'Preposition'},
        {'name': 'Conjunction'},
        {'name': 'Particle'},
        {'name': 'Verb'},
        {'name': 'Verb form'},
        {'name': 'Noun'},
        {'name': 'Noun 1'},
        {'name': 'Noun 2'},
        {'name': 'Adverb'},
        {'name': 'Adverb 1'},
        {'name': 'Interjection'},
        {'name': 'Adjective'},
        {'name': 'Numeral'},

        {'name': 'Pronunciation'},
        {'name': 'Declension'},
        {'name': 'Etymology'},
        {'name': 'Etymology 1'},
        {'name': 'Etymology 2'},
        {'name': 'Etymology 3'},
        {'name': 'Synonyms'},
        {'name': 'Antonyms'},
        {'name': 'Hypernyms'},
        {'name': 'Hyponyms'},
        {'name': 'Meronyms'},
        {'name': 'Anagrams'},
        {'name': 'Contraction'},
        {'name': 'References'},
        {'name': 'Descendants'},
        {'name': 'Related terms'},
        {'name': 'See also'},
        {'name': 'Further reading'},
        {'name': 'Derived terms'},
        {'name': 'Usage notes'},
        {'name': 'Phrases'},
        {'name': 'Phrase'},
        {'name': 'Conjugation'},
        {'name': 'Alternative forms'},
        {'name': 'Coordinate terms'},
        {'name': 'External links'},


    ]

    my_model = genanki.Model(
        1607392320,
        'Wikislovnik',
        css=css,
        fields=model_fields,
        templates=[{
            'name': 'Card 1',
            'qfmt': '{{Word}}',
            'afmt': '''
            {{Word}}
            <hr id="answer">
            {{#Pronunciation}}
                {{Pronunciation}}
            {{/Pronunciation}}
            ''',
        }])

    my_deck = genanki.Deck(2059400111, 'Czech Frequency Word List')

    for idx, w in enumerate(w_list):
        word = w.find('a')
        print(idx, word.text)
        w_url = urljoin(url, word['href'])

        w_resp = requests.get(w_url)
        w_soup = BeautifulSoup(w_resp.text, "lxml")

        fields = [str(idx), word.text]
        cz_begin = w_soup.find('span', id="Czech")
        data = dict(get_all_blocks(cz_begin))


        for field in model_fields[2:]:
            field_name = field['name']
            fields.append(data.pop(field_name, ""))

        # if data.keys():
            # print("!!!!!!!!!!!!!!!", data.keys())
        assert not data.keys(), data.keys()

        my_note = genanki.Note(
            model=my_model,
            fields=fields, sort_field='idx')
        my_deck.add_note(my_note)


    genanki.Package(my_deck).write_to_file('/output/czfrq.apkg')


if __name__ == "__main__":
    main()
