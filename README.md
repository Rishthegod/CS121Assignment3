# CS 121 Project 3

## Creating the Index (M1)

- Create a folder `index_files` and inside that, create a folder `output`
- `python3 src/build_index.py` with the folder name `data_dump` when prompted

## Performing a Search (M2)

- Ensure you have the partial index files in `index_files/output`
- `python3 src/index_search.py`
- Enter a query and hit enter

## Upgrading to M3
- Rebuild the index
- Rebuild the glossary: `python3 src/term_finder.py`
- Move the `glossary.json` into the `index_files` folder
- Run the index search or web server script
