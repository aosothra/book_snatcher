# book_snatcher

This script can be used to download books from [tululu.org](https://tululu.org/).

Use it to save text content of books and their cover images.

## Installation guidelines

You must have Python3 installed on your system.
You may use `pip` (or `pip3` to avoid conflict with Python2) to install dependencies.

```
pip install -r requirements.txt
```

It is strongly advised to use [virtualenv/venv](https://docs.python.org/3/library/venv.html) for project isolation.

## Basic usage

Each book on the [tululu.org](https://tululu.org/) website is addressed by unique `id` property.

So in order for the script to do the job, user is expected to specify a range of id's to download respective books. Use arguments `--start_id` and `--end_id` for that purpose. This range is inclusive, so with both argument set to a same value a single book will be downloaded (if avaliable).

Here is an example of how to get books from 1 to 10:

```
python main.py --start_id 1 --end_id 10
```

In your terminal's output you will see details about each single book as well as any error which might occure in the proccess (usually for books which are not avaliable)

## Project goals

This project was created for educational purposes as part of [dvmn.org](https://dvmn.org/) Backend Developer course.