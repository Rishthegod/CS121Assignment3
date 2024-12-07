import json
from partial_index import PartialIndex
from enum import Enum


BUCKET_ENTRY_LIMIT = 50000


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
        self._disk_index = PartialIndex(name)


    def add_frequency(self, doc_entry: dict, freq_type: TermType, doc_length: int):
        freq_key = 'frequency_' + freq_type.value
        doc_entry[freq_key] = doc_entry.get(freq_key, 0) + 1
        doc_entry['frequency'] = doc_entry.get('frequency', 0) + 1 / doc_length


    def add_document(self, normalized_token: str, document_id: int, term_type: TermType = TermType.Normal, *, doc_length: int) -> None:
        if type(document_id) != int:
            raise TypeError('Invalid Document ID. Must be a number from documents.add_url() return value')
        document_id = str(document_id)

        # if our current size is too large, we update the disk index
        if len(self) >= BUCKET_ENTRY_LIMIT:
            print(f'\nSurpassed {BUCKET_ENTRY_LIMIT} of entries, updating partial index `{self._disk_index.get_name()}` on disk')
            # self._disk_index.write_to_disk(self._token_map)
            self.merge()

        token_docs = self._token_map.get(normalized_token, {})

        doc_entry = token_docs.get(document_id, { 'document_id': document_id })
        if document_id not in token_docs:
            self._size += 1

        self.add_frequency(doc_entry, term_type, doc_length)

        # Write-back for if it is a new entry
        token_docs[document_id] = doc_entry
        self._token_map[normalized_token] = token_docs


    def merge(self) -> None:
        temp_map = self._disk_index.read_from_disk()
        for tok, pages in self._token_map.items():
            for page_doc_id, page in pages.items():
                temp_token_map = temp_map.get(tok, {})
                temp_map[tok] = temp_token_map
                posting_to_update = temp_token_map.get(page_doc_id, { 'document_id': page_doc_id })
                temp_token_map[page_doc_id] = posting_to_update
                for property, value in [p for p in page.items() if p[0].startswith('frequency')]:
                    posting_to_update[property] = posting_to_update.get(property, 0) + value

                    # print(f'need to update {tok} -> {page_doc_id} with {property}:{value}')

        self._disk_index.write_to_disk(temp_map)
        self._token_map = {}
        self._size = 0


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
        return self._size
        # document_counts = [len(token_doc_map) for token_doc_map in self._token_map.values()]
        # return sum(document_counts)




def main():
    test_bucket = TokenBucket('test-token')
    # test_bucket._token_map = test_bucket._disk_index.read_from_disk()

    # THIS SHOULD ADD ON ITS OWN NOW
    test_bucket.add_document('tokenizer', 1, doc_length=112)
    test_bucket.add_document('tokenize', 1, doc_length=112)
    test_bucket.add_document('tokenize', 1, doc_length=112)
    test_bucket.add_document('tokens', 1, doc_length=112)  # total should be 4
    test_bucket.add_document('tokens', 2, doc_length=80)
    test_bucket.add_document('test', 2, doc_length=80)
    test_bucket.add_document('test', 2, TermType.Bold, doc_length=80)
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
