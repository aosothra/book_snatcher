from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError


def raise_for_redirects(response):
    if response.status_code in [301, 302]:
        redirect_url = urljoin(response.url, response.headers['Location'])
        raise HTTPError(f'Request shamelessly redirected to: {redirect_url}')


def get_books_from_page(num_page):
    url = f'https://tululu.org/l55/{num_page}'

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    raise_for_redirects(response)

    content_soup = BeautifulSoup(response.text, 'lxml').find(id='content')
    nodes = content_soup.find_all('div', class_='bookimage')

    books_on_page = [
        urljoin(url, node.find('a').get('href'))
        for node in nodes
        ]

    return books_on_page


def main():
    for num_page in range(1, 20):
        try:
            books_urls = get_books_from_page(num_page)
            print(books_urls)
        except HTTPError:
            print('Request redirected, assuming no more books to parse...')
            break


if __name__ == "__main__":
    main()
