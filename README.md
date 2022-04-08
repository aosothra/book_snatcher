# book_snatcher

This script can be used to collect fantasy books from [tululu.org](https://tululu.org/).

Use it to save text content of books and their cover images. After collection proccess is completed, the script creates a JSON register, that lists each book data in following schema:
```JavaScript
{
      "title": "Book Title",
      "author": "Author Name",
      "genre": "Book genre",
      "comments":[                      //Might be empty if no comments are found
         "User comment text 1",
         "User comment text 2",
         "User comment text 3",
      ],
      "book_path":"path/to/book.txt",   //field omitted if --skip_txt is set
      "img_src":"path/to/image.jpeg"    //field omitted if --skip_imgs is set
   }
```

## Installation guidelines

You must have Python3 installed on your system.
You may use `pip` (or `pip3` to avoid conflict with Python2) to install dependencies.

```
pip install -r requirements.txt
```

It is strongly advised to use [virtualenv/venv](https://docs.python.org/3/library/venv.html) for project isolation.

## Basic usage

To download the collection, use following command:
```
python main.py
```

This script can be ran with following parameters:

`--start_page` - used to specify the number of page from where to start collecting books. Default value is `1`.

`--end_page` - used to specify the number of page where to stop collecting books. Default value is `4`

Obviously, the starting index should be less than / equal to the ending index. Be aware, that `--end_page` will be included in the collection, so to collect books from a single page - lets say, page 10, - you must pass parameters as follows:

```
python main.py --start_page 10 --end_page 10
```

`--dest_folder` - used to specify folder, where downloaded content will be saved. Root folder is used by default.

Images and texts are saved in separate directories, `images` and `books` respectively, so if some `./custom/path/` is specified by `--dest_folder` it will be prepended to the original path: `./custom/path/images/` and `./custom/path/books/`.

`--json_path` - used to specify full path to save resulting collection register in JSON. Default value is `library.json`. If `--json_path` contains directories - the script will attempt to create them on start. 

`--skip_imgs` - used to flag wether images must be ignored during collection proccess. If set - no image will be saved. 

`--skip_txt` - used to flag wether book texts must be ignored during collection proccess. If set - no book text will be saved.

## Project goals

This project was created for educational purposes as part of [dvmn.org](https://dvmn.org/) Backend Developer course.