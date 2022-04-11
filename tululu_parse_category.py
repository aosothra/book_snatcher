from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
from requests.models import Response


def raise_for_redirects(response: Response):
    '''Raise HTTPError in case of redirect'''

    if response.status_code in [301, 302]:
        redirect_url = urljoin(response.url, response.headers['Location'])
        raise HTTPError(f'Request shamelessly redirected to: {redirect_url}')


def get_books_from_page(num_page: int):
    '''Collect all book urls from a single category page'''

    url = f'https://tululu.org/l55/{num_page}'

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    raise_for_redirects(response)

    content_soup = BeautifulSoup(response.text, 'lxml').select_one('#content')
    nodes = content_soup.select('div.bookimage a')

    books_on_page = [
        urljoin(url, node.get('href')) for node in nodes
        ]

    return books_on_page


def get_last_page_in_category():
    '''Find last page in the category of books'''

    url = 'https://tululu.org/l55/'

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    raise_for_redirects(response)

    content_soup = BeautifulSoup(response.text, 'lxml').select_one('#content')
    last_page = int(content_soup.select_one('a.npage:last-child').text)

    return last_page


def main():
    '''Print books on pages from 1 to 20'''

    for num_page in range(1, 20):
        try:
            books_urls = get_books_from_page(num_page)
            print(books_urls)
        except HTTPError:
            print('Request redirected, assuming no more books to parse...')
            break


if __name__ == "__main__":
    main()
