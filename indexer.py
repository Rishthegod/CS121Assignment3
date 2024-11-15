# import os
import json
# import sys

# import nltk
# import pickle
# from bs4 import BeautifulSoup
# from collections import defaultdict
import re


from src.text_extractor import get_token_map
from src.token_bucket import TokenBucket, TermType
from src.partial_index import documents


class Indexer:

    def __init__(self, data_dir, memory_limit=500*1024*1024):
        # self.data_dir = data_dir
        # self.inverted_index = defaultdict(list)
        self.doc_count = 0
        # self.partial_indexes = []
        # self.stemmer = placeholder
        # self.memory_limit = memory_limit  # Memory limit in bytes 500 mb

        # self.partial_index_count = 0
        # self.unique_tokens = set()

        self._ranges = ['a-e', 'f-j', 'k-o', 'p-t', 'u-z', '0-9', '^a-z0-9']
        self._expressions = [f'^[{r}]' for r in self._ranges]

        self._buckets = {r: TokenBucket('bucket_' + r) for r in self._ranges}
    

    def get_bucket(self, token: str):
        target_range = [r for r in self._ranges if re.search(r, token)][0]
        print(target_range)


    def process_document(self, filepath):
        # 1. Read the file
        # 2. Extract the text tokens from the file (call helper)
        # 3. Convert the textNode -> element map into a token -> element map
        # 4. For each token...
        #      a. Determine which bucket it goes into (start letter)
        #      b. Determine which TermType that token should have
        # 5. Insert into the TokenBucket (this will deal with file system writing on its own)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                html_content = data.get('content', '')
                url = data.get('url', '')

                if not url:
                    print(f'Missing URL for {filepath}')
                    return

                # doc_id = filepath  # Using file path as a document ID
                self.doc_count += 1
                documents.add_url(url)

                tokens = get_token_map(html_content)
                [self.get_bucket(token) for token in tokens]

                #####   Commented out because we should be able to get token counts from partial indexes   #####
                # token_counts = defaultdict(int)
                # for token in tokens:
                #     token_counts[token] += 1
                # for token, tf in token_counts.items():
                #     self.inverted_index[token].append((doc_id, tf))
                #     self.unique_tokens.add(token)

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
    


def main():
    indexer = Indexer()
    indexer.process_document('data_dump/aiclub_ics_uci_edu/8ef6d99d9f9264fc84514cdd2e680d35843785310331e1db4bbd06dd2b8eda9b.json')


if __name__ == '__main__':
    main()

