from partial_index import documents
from token_bucket import TokenBucket
from pathlib import Path
import text_extractor as te
import json
import re
from nltk.stem import PorterStemmer
import time

_bucket_keys = [
    *[chr(c) for c in range(ord('a'), ord('z') + 1)],
    *[chr(c) for c in range(ord('0'), ord('9') + 1)],
    '*'
]

_bucket_pairs = [[first + second for second in _bucket_keys] for first in _bucket_keys]

all_buckets = {key: TokenBucket('full2/' + key) for l in _bucket_pairs for key in l}

# all_buckets = [
#     TokenBucket("A-F"),
#     TokenBucket("G-L"),
#     TokenBucket("M-Q"),
#     TokenBucket("R-V"),
#     TokenBucket("W-Z"),
#     TokenBucket("numbers"),
#     TokenBucket("symbols")
# ]

def get_bucket_name(stem: str) -> str:
    first, second = [re.sub('[^a-z0-9]|^$', '*', s) for s in (stem[0:1], stem[1:2])]
    return first + second

def find_bucket(stem: str) -> TokenBucket:
    bucket_name = get_bucket_name(stem)
    return all_buckets[bucket_name]


# def find_bucket(letter: str) -> int:
#     if 'a' <= letter <= 'f':
#         return 0
#     elif 'g' <= letter <= 'l':
#         return 1
#     elif 'm' <= letter <= 'q':
#         return 2
#     elif 'r' <= letter <= 'v':
#         return 3
#     elif 'w' <= letter <= 'z':
#         return 4
#     elif '0' <= letter <= '9':
#         return 5
#     else:
#         return 6

def all_jsons_in_folder(folder: str):
    folder_path = Path(folder)
    path_list = []
    if folder_path.exists() and folder_path.is_dir():
        path_list = [path for path in folder_path.rglob('*.json')]

    return path_list

def build_index_helper(source: Path) -> dict:
    """source: dict of URL w/ its body"""
    with open(source, 'r') as file:
        data = json.loads(file.read())


    start = time.perf_counter()

    url = data["url"]
    html_content = data["content"]
    doc_id = documents.add_url(url)

    start, diff = time.perf_counter(), time.perf_counter() - start
    print(f',  add_url={round(diff * 1000, 3)}ms', end=', ')

    mapped_tokens = te.map_tokens(te.extract_tokens(html_content))

    start, diff = time.perf_counter(), time.perf_counter() - start
    print(f' map_tokens={round(diff * 1000, 3)}ms', end=', ')

    stemmer = PorterStemmer()

    for token, term_type in mapped_tokens:
        stem = stemmer.stem(token.lower())
        bucket = find_bucket(stem)
        bucket.add_document(stem, doc_id, term_type)

    start, diff = time.perf_counter(), time.perf_counter() - start
    print(f' add_doc={round(diff * 1000, 3)}ms')


def build_index(path_lists: list[Path]):
    # print(path_lists)
    for i, p in enumerate(path_lists):
        print(f'[START] INDEX={i}, PAGE="{p}"', end='')
        # print(f'-----\n-----\n{p}\n-----\n-----')
        build_index_helper(p)


def main():
    all_jsons = all_jsons_in_folder(input('Enter file path: '))
    build_index(all_jsons)
    for b in all_buckets.values():
        b.print_full()


if __name__ == "__main__":
    '''To clear the current files, `rm index_files/output/*.index.gz`   '''
    main()
