import os
import json
import sys
import re
import nltk
import pickle
from bs4 import BeautifulSoup

from collections import defaultdict
import psutil
class Indexer:

    def __init__(self, data_dir, memory_limit=500*1024*1024):
        self.data_dir = data_dir
        self.inverted_index = defaultdict(list)
        self.doc_count = 0
        self.partial_indexes = []
        # self.stemmer = placeholder
        self.memory_limit = memory_limit  # Memory limit in bytes
        self.partial_index_count = 0
        self.unique_tokens = set()
    def process_document(self, filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    html_content = data.get('content', '')
                    url = data.get('url', '')
                    doc_id = filepath  # Using file path as a document ID
                    self.doc_count += 1
                    tokens = self.extract_tokens(html_content)
                    token_counts = defaultdict(int)
                    for token in tokens:
                        token_counts[token] += 1
                    for token, tf in token_counts.items():
                        self.inverted_index[token].append((doc_id, tf))
                        self.unique_tokens.add(token)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    