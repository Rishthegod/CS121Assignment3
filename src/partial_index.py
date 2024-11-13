from pathlib import Path
import json


FOLDER_NAME = 'index_files/'


def setup():
    folder = Path(FOLDER_NAME)
    if not folder.exists():
        folder.mkdir()


setup()


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
                print([entry for entry in pages.values()])
                data = (json.dumps(entry) + '\n' for entry in pages.values())
                file.writelines((f'>> {token}\n', *data))


    def get_name(self) -> str:
        return self._name



def main():
    test_index = PartialIndex('test')
    print(test_index.get_name())
    print(result := test_index.read_from_disk())
    print(test_index.write_to_disk(result))


if __name__ == '__main__':
    main()
