'''
Script to read all of the partial index files. While reading each one, we need to find the
position in each file where the term resides.

Example: suppose...
  - ac --> "ace" at position 0
  - ac --> "act" at position 12
  - to --> "top" at position 4
  - to --> "tot" at position 12
Result ==> { ace: 0, act: 12, top: 4, tot: 12 }

Then write that dictionary back to disk to persist between program runs
We will read that dictionary from `index_search.py`
'''

from build_index import all_buckets
from pathlib import Path
import json


def read_buckets():
    glossary = {}
    for name, bucket in all_buckets.items():
        partial_index = bucket._disk_index
        partial_index.read_from_disk()
        glossary |= partial_index._term_positions
        print('Finished reading bucket', name)
    return glossary


def load_glossary_from_disk():
    return json.loads(Path('index_files/glossary.json').read_text())


def main():
    glossary = read_buckets()
    jsonstr = json.dumps(glossary, indent=2)
    Path('glossary.json').write_text(jsonstr)


if __name__ == '__main__':
    main()
