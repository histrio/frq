import genanki
import requests
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin


def remove_edit_href(node):
    edit_span = node.find('span', {'class': 'mw-editsection'})
    if edit_span:
        edit_span.decompose()


def get_all_blocks(node):
    pass


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

    my_model = genanki.Model(
        1607392320,
        'Wikislovnik',
        css=css,
        fields=[
            {'name': 'idx'},
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[{
            'name': 'Card 1',
            'qfmt': '{{Question}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
        }])

    my_deck = genanki.Deck(2059400111, 'Czech Frequency Word List')

    for idx, w in enumerate(w_list):
        word = w.find('a')
        print(idx, word.text)
        w_url = urljoin(url, word['href'])

        w_resp = requests.get(w_url)
        w_soup = BeautifulSoup(w_resp.text, "lxml")

        tr = ""
        cz_begin = w_soup.find('span', id="Czech")
        for block in get_all_blocks(cz_begin):
            print(block)

        # if cz_negin:
            # rr = rr.parent
            # while rr.nextSibling and rr.nextSibling.name != 'hr':
                # rr = rr.nextSibling
                # if isinstance(rr, NavigableString):
                    # continue
                # remove_edit_href(rr)
                # tr += str(rr)
        my_note = genanki.Note(
            model=my_model,
            fields=[word.text, tr, str(idx)], sort_field='idx')
        my_deck.add_note(my_note)
        if idx>10:
            break

    genanki.Package(my_deck).write_to_file('/output/czfrq.apkg')


if __name__ == "__main__":
    main()
