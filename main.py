import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import HTTPError

from tululu_parse_category import get_books_from_page, raise_for_redirects


def download_image(url, images_dir):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    raise_for_redirects(response)

    filename = unquote(urlsplit(url).path.split('/')[-1])
    fullpath = os.path.join(images_dir, filename)

    with open(fullpath, 'wb') as img_file:
        img_file.write(response.content)

    return fullpath


def download_book(book_id, books_dir, book_title):
    url = 'https://tululu.org/txt.php'
    params = {
        'id': book_id
    }

    response = requests.get(url, params=params, allow_redirects=False)
    response.raise_for_status()
    raise_for_redirects(response)

    book_text = response.text

    book_title = sanitize_filename(book_title)
    fullpath = os.path.join(books_dir, f'{book_title}.txt')

    with open(fullpath, 'w') as text_file:
        text_file.write(book_text)

    return fullpath


def get_book_details(url):
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    raise_for_redirects(response)

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
        'comments': book_comments
    }, urljoin(url, book_image_src)


def collect_books(books_urls, books_dir, images_dir):
    book_descriptions = []
    for book_url in books_urls:
        book_id = re.search(r'\d+', book_url).group()
        try:
            description, cover_image_url = get_book_details(book_url)

            description['book_path'] = download_book(book_id, books_dir, description['title'])
            description['img_src'] = download_image(cover_image_url, images_dir)
            book_descriptions.append(description)
        except HTTPError as err:
            print('Failed to fetch book by url:', book_url)
            print(err)

    return book_descriptions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', default=1, type=int, help='Page from where to start parsing')
    parser.add_argument('--end_page', default=10, type=int, help='Page at which to end parsing')
    args = parser.parse_args()

    start_page = args.start_page
    end_page = args.end_page + 1

    books_dir = './books/'
    images_dir = './images/'
    Path(books_dir).mkdir(exist_ok=True, parents=True)
    Path(images_dir).mkdir(exist_ok=True, parents=True)

    book_descriptions = []

    for categoty_page in range(start_page, end_page):
        try:
            books_urls = get_books_from_page(categoty_page)
            book_descriptions += collect_books(books_urls, books_dir, images_dir)
        except HTTPError:
            print('Request redirected, assuming no more books to parse...')
            break

    with open('library.json', 'w', encoding='utf8') as lib_file:
        json.dump(book_descriptions, lib_file, ensure_ascii=False)


if __name__ == "__main__":
    main()
