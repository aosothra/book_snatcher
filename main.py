import argparse
import os
from pathlib import Path
from pprint import pprint
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import HTTPError


def download_image(url, images_dir):
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPError(f'Request failed or redirected. Status code: {response.status_code}')

    filename = unquote(urlsplit(url).path.split('/')[-1])
    fullpath = os.path.join(images_dir, filename)

    with open(fullpath, 'wb') as img_file:
        img_file.write(response.content)


def download_book(book_id, books_dir, book_title):
    url = 'https://tululu.org/txt.php'
    params = {
        'id': book_id
    }

    response = requests.get(url, params=params, allow_redirects=False)
    if response.status_code != 200:
        raise HTTPError(f'Request failed or redirected. Status code: {response.status_code}')

    book_text = response.text

    book_title = sanitize_filename(book_title)
    fullpath = os.path.join(books_dir, f'{book_id}_{book_title}.txt')

    with open(fullpath, 'w') as text_file:
        text_file.write(book_text)


def get_book_details(id):
    url = f'https://tululu.org/b{id}/'

    response = requests.get(url, allow_redirects=False)
    if response.status_code != 200:
        raise HTTPError(f'Request failed or redirected. Status code: {response.status_code}')

    page_content = response.text

    soup = BeautifulSoup(page_content, 'lxml').find(id='content')

    book_title, book_author = soup.find('h1').text.split('::')
    book_image_src = soup.find('div', class_='bookimage').find('img')['src']
    book_genre = soup.find('span', class_='d_book').find('a').text
    book_comments = [text_node.find('span').text for text_node
                     in soup.find_all('div', class_='texts')]
                     
    return {
        'title': book_title.strip(),
        'author': book_author.strip(),
        'genre': book_genre,
        'img_url': urljoin(url, book_image_src),
        'comments': book_comments
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_id', default=1, type=int, help='ID of the book to start fetching from')
    parser.add_argument('--end_id', default=10, type=int, help='ID of the book to finish fetching at')
    args = parser.parse_args()

    start_id = args.start_id
    end_id = args.end_id + 1

    books_dir = './books/'
    images_dir = './images'
    Path(books_dir).mkdir(exist_ok=True, parents=True)
    Path(images_dir).mkdir(exist_ok=True, parents=True)

    for id in range(start_id, end_id):
        try:
            details = get_book_details(id)
            pprint(details, sort_dicts=False)
            download_book(id, books_dir, details['title'])
            download_image(details['img_url'], images_dir)
        except HTTPError as err:
            print('Failed to fetch book by id:', id)
            print(err)
        finally:
            print()


if __name__ == "__main__":
    main()
