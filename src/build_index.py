from partial_index import PartialIndex, documents
from token_bucket import TokenBucket, TermType
from pathlib import Path
import text_extractor as te
import json
import sys


all_buckets = [
    TokenBucket("A-F"),
    TokenBucket("G-L"),
    TokenBucket("M-Q"),
    TokenBucket("R-V"),
    TokenBucket("W-Z"),
    TokenBucket("numbers"),
    TokenBucket("symbols")
]

def find_bucket(letter: str) -> int:
    if 'a' <= letter <= 'f':
        return 0
    elif 'g' <= letter <= 'l':
        return 1
    elif 'm' <= letter <= 'q':
        return 2
    elif 'r' <= letter <= 'v':
        return 3
    elif 'w' <= letter <= 'z':
        return 4
    elif '0' <= letter <= '9':
        return 5
    else:
        return 6

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

    url = data["url"]
    html_content = data["content"]
    doc_id = documents.add_url(url)

    mapped_tokens = te.map_tokens(te.extract_tokens(html_content))
    for token, term_type in mapped_tokens:
        bucket = all_buckets[find_bucket(token[0])]
        bucket.add_document(token, doc_id, term_type)


def build_index(path_lists: list[Path]):
    print(path_lists)
    for i, p in enumerate(path_lists):
        print(f'[START] INDEX={i}, PAGE="{p}"')
        # print(f'-----\n-----\n{p}\n-----\n-----')
        build_index_helper(p)


def main():
    all_jsons = all_jsons_in_folder(input('Enter file path: '))
    build_index(all_jsons)
    for b in all_buckets:
        b.print_full()

if __name__ == "__main__":
    '''To clear the current files, `rm index_files/{A-F,G-L,M-Q,numbers,R-V,W-Z,symbols}.index.gz`   '''
    main()