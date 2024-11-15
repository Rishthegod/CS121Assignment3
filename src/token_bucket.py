from nltk.stem import PorterStemmer
import json
from partial_index import PartialIndex
from enum import Enum


BUCKET_ENTRY_LIMIT = 3


class TermType(Enum):
    Normal = 'normal'
    PageTitle = 'page_title'
    Heading = 'heading'
    Anchor = 'anchor'
    Bold = 'bold'


class TokenBucket:
    def __init__(self, name: str) -> None:
        self._size = 0
        self._token_map = {}
        self._stemmer = PorterStemmer()
        self._disk_index = PartialIndex(name)


    def add_frequency(self, doc_entry: dict, freq_type: TermType):
        freq_key = 'frequency_' + freq_type.value
        doc_entry[freq_key] = doc_entry.get(freq_key, 0) + 1
        doc_entry['frequency'] = doc_entry.get('frequency', 0) + 1


    def add_document(self, token: str, document_id: int, term_type: TermType = TermType.Normal, idf = None) -> None:
        document_id = str(document_id)

        # if our current size is too large, we update the disk index
        if len(self) >= BUCKET_ENTRY_LIMIT:
            print(f'\nSurpassed {BUCKET_ENTRY_LIMIT} of entries, updating partial index `{self._disk_index.get_name()}` on disk')
            # self._disk_index.write_to_disk(self._token_map)
            self.merge()

        stemmed = self.stem_token(token)
        token_docs = self._token_map.get(stemmed, {})

        doc_entry = token_docs.get(document_id, { 'document_id': document_id })
        self.add_frequency(doc_entry, term_type)

        # Write-back for if it is a new entry
        token_docs[document_id] = doc_entry
        self._token_map[stemmed] = token_docs


    def merge(self) -> None:
        temp_map = self._disk_index.read_from_disk()
        for tok, pages in self._token_map.items():
            for page_doc_id, page in pages.items():
                posting_to_update = temp_map[tok][page_doc_id]
                for property, value in [p for p in page.items() if p[0].startswith('frequency')]:
                    posting_to_update[property] = posting_to_update.get(property, 0) + value
                    # print(f'need to update {tok} -> {page_doc_id} with {property}:{value}')

        self._disk_index.write_to_disk(temp_map)
        self._token_map = {}


    def print(self, data: dict = None) -> None:
        print(f'TokenBucket<{len(self)}> = ', end='')
        prettified = json.dumps(self._token_map if data is None else data, indent=2)
        print(prettified)


    def print_full(self) -> None:
        self.merge()
        temp_map = self._disk_index.read_from_disk()
        print('Full', end='')
        self.print(temp_map)


    def __len__(self) -> int:
        document_counts = [len(token_doc_map) for token_doc_map in self._token_map.values()]
        return sum(document_counts)


    def stem_token(self, token: str) -> str:
        return self._stemmer.stem(token)



def main():
    test_bucket = TokenBucket('test-token')
    # test_bucket._token_map = test_bucket._disk_index.read_from_disk()

    # THIS SHOULD ADD ON ITS OWN NOW
    test_bucket.add_document('tokenizer', 1)
    test_bucket.add_document('tokenize', 1)
    test_bucket.add_document('tokenize', 1)
    test_bucket.add_document('tokens', 1)  # total should be 4
    test_bucket.add_document('tokens', 2)
    test_bucket.add_document('test', 2)
    test_bucket.add_document('test', 2, TermType.Bold)
    test_bucket.print()
    test_bucket.print_full()

    # test_bucket._disk_index.write_to_disk(test_bucket._token_map)


if __name__ == '__main__':
    main()


'''
Sample Data
TokenBucket<3> = {
  "token": {
    "https://1.1.1.1": { "document_id": "https://1.1.1.1", "frequency_normal": 4, "frequency": 4 },
    "second_id":       { "document_id": "second_id",       "frequency_normal": 1, "frequency": 1 }
  },
  "test": {
    "second_id": { "document_id": "second_id", "frequency_normal": 1, "frequency": 2, "frequency_bold": 1 }
  }
}
'''