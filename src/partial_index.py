from pathlib import Path
import json


FOLDER_NAME = 'index_files/'


def setup():
    folder = Path(FOLDER_NAME)
    if not folder.exists():
        folder.mkdir()


setup()


class _DocumentIdLookup:
    def __init__(self) -> None:
        self._lines = []
        self._url_lookup = {}
        self._path = Path(FOLDER_NAME + 'documents.txt')
        if not self._path.exists():
            self._path.touch(777, False)
        else:
            for i, line in enumerate(self._path.open().readlines()):
                self._lines.append(line.strip())
                self._url_lookup[line.strip()] = i
        
        self._file = self._path.open('a+')
    
    
    def get_url(self, doc_id: int) -> str:
        if not 0 <= doc_id < len(self._lines): return None
        return self._lines[doc_id]
    
    def add_url(self, url: str) -> int:
        if url in self._url_lookup: return self._url_lookup[url]

        new_id = len(self._lines)
        self._url_lookup[url] = new_id
        self._lines.append(url)
        self._file.writelines([url + '\n'])
        return new_id
        


documents = _DocumentIdLookup()


class PartialIndex:
    FILE_EXT = '.index.dat'

    def __init__(self, name: str) -> None:
        self._name = name
        self._path = Path(FOLDER_NAME + self._name + PartialIndex.FILE_EXT)


    '''Reads line and returns the current token'''
    def _read_line(self, map: dict, line: str, current_token: str) -> str:
        if line.startswith('>> '):
            # Encountering a new token
            current_token = line[3:].strip()
            map[current_token] = {}
        else:
            # Encountering an entry
            data = json.loads(line)
            map[current_token][data['document_id']] = data
        
        return current_token


    def read_from_disk(self) -> dict:
        if not self._path.exists():
            self._path.touch(777, False)
        
        result_map = {}
        token = ''
        with self._path.open() as file:
            [token := self._read_line(result_map, line, token) for line in file.readlines()]
        
        return result_map
    
    
    def write_to_disk(self, data: dict):
        with self._path.open('w') as file:
            for token, pages in data.items():
                print(f'Writing entry: {[entry for entry in pages.values()]}')
                data = (json.dumps(entry) + '\n' for entry in pages.values())
                file.writelines((f'>> {token}\n', *data))


    def get_name(self) -> str:
        return self._name



def main():
    test_index = PartialIndex('test')
    test_map ={
        "token": {
            "https://1.1.1.1": { "document_id": "https://1.1.1.1", "frequency_normal": 4, "frequency": 4 },
            "second_id":       { "document_id": "second_id",       "frequency_normal": 1, "frequency": 1 }
        },
        "test": {
            "second_id": { "document_id": "second_id", "frequency_normal": 1, "frequency": 2, "frequency_bold": 1 }
        }
    }
    
    test_index.write_to_disk(test_map)

    # print(test_index.get_name())
    result = test_index.read_from_disk()
    print(f'-----Testing: read_from_disk\n   {result}')
    # print(test_index.write_to_disk(result))

    # print('Existing first:', documents.get_url(0))
    # print('Existing second:', documents.get_url(1))

    # documents.add_url('https://example.com')
    # new_id = documents.add_url('https://example.net')

    # print('New example.net:', documents.get_url(new_id))


if __name__ == '__main__':
    main()
