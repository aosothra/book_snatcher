import argparse
import json
import os
import re
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from requests.exceptions import HTTPError

from tululu_parse_category import get_books_from_page, raise_for_redirects


def download_image(url: str, images_dir: str):
    '''Fetch image from URL and save in filesystem'''

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    raise_for_redirects(response)

    # Filename is extracted from provided URL
    filename = unquote(urlsplit(url).path.split('/')[-1])
    fullpath = os.path.join(images_dir, filename)

    with open(fullpath, 'wb') as img_file:
        img_file.write(response.content)

    return fullpath


def download_book(book_id: int, books_dir: str, book_title: str):
    '''Fetch book text content and save in filesystem'''

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


def get_book_details(url: str):
    '''Collect individual book details and cover image URL'''

    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    raise_for_redirects(response)

    page_content = response.text

    soup = BeautifulSoup(page_content, 'lxml').select_one('#content')

    book_title, book_author = soup.select_one('h1').text.split('::')
    book_image_src = soup.select_one('div.bookimage img').get('src')

    book_genre = soup.select_one('span.d_book a').text
    book_comments = [text_node.text for text_node
                     in soup.select('div.texts span')]

    return {
        'title': book_title.strip(),
        'author': book_author.strip(),
        'genre': book_genre,
        'comments': book_comments
    }, urljoin(url, book_image_src)


def collect_books(books_urls: Iterable[str], books_dir: str, images_dir: str):
    '''Fetch all book datas from a given list of URLs'''

    book_descriptions = []
    for book_url in books_urls:
        book_id = re.search(r'\d+', book_url).group()
        try:
            description, cover_image_url = get_book_details(book_url)
            if books_dir:
                description['book_path'] = download_book(book_id, books_dir, description['title'])
            if images_dir:
                description['img_src'] = download_image(cover_image_url, images_dir)
            book_descriptions.append(description)
        except HTTPError as err:
            print('Failed to fetch book by url:', book_url)
            print(err)

    return book_descriptions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--start_page', default=1, type=int, help='Page from where to start parsing')
    parser.add_argument('--end_page', default=4, type=int, help='Page at which to end parsing')
    parser.add_argument(
        '--dest_folder',
        default='',
        type=str,
        help='Path to directory where downloaded content should be saved'
        )
    parser.add_argument(
        '--json_path',
        default='library.json',
        type=str,
        help='Path to JSON file to save complete book registry'
        )
    parser.add_argument('--skip_imgs', action='store_true', help='Skip images during download')
    parser.add_argument('--skip_txt', action='store_true', help='Skip book texts during download')

    args = parser.parse_args()

    books_dir = '' if args.skip_txt else os.path.join(args.dest_folder, 'books')
    images_dir = '' if args.skip_imgs else os.path.join(args.dest_folder, 'images')
    json_dir = os.path.split(args.json_path)[0]

    Path(books_dir).mkdir(exist_ok=True, parents=True)
    Path(images_dir).mkdir(exist_ok=True, parents=True)
    Path(json_dir).mkdir(exist_ok=True, parents=True)

    book_descriptions = []

    for categoty_page in range(args.start_page, args.end_page + 1):
        try:
            books_urls = get_books_from_page(categoty_page)
            book_descriptions += collect_books(books_urls, books_dir, images_dir)
        except HTTPError:
            print('Request redirected, assuming no more books to parse...')
            break

    with open(args.json_path, 'w', encoding='utf8') as lib_file:
        json.dump(book_descriptions, lib_file, ensure_ascii=False)


if __name__ == "__main__":
    main()
