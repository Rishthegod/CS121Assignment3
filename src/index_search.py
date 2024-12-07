from build_index import find_bucket
from nltk import PorterStemmer
from partial_index import documents
from term_finder import load_glossary_from_disk
import time
import re


glossary = load_glossary_from_disk()


def search(user_input: str):
    query = user_input.split(' ')
    doc_lists = []
    final_list = []

    start = time.perf_counter()

    # Get lists for each term
    for term in query:
        stemmed = PorterStemmer().stem(term)
        # print(term, stemmed, find_bucket(stemmed))
        bucket = find_bucket(stemmed)

        print('Reading bucket...')
        lookup_position = glossary.get(stemmed, -1)
        # data = bucket._disk_index.read_from_disk()
        # doc_list: dict = data.get(stemmed, {})
        if lookup_position > -1:
            doc_list = bucket.read_term_at_position(lookup_position)
            sorted_entries = [*doc_list.values()]
            sorted_entries.sort(key=lambda x: int(x['document_id']))
        else:
            sorted_entries = []

        doc_lists.append(sorted_entries)
    
    shortest_len = min([len(l) for l in doc_lists])
    # print('lengths', [len(l) for l in doc_lists])
    shortest = next((l for l in doc_lists if len(l) == shortest_len))

    # print(shortest_len, doc_lists.index(shortest))
    cursors = [(i for i in list) for list in doc_lists]
    recents = [{'document_id': -1}] * len(doc_lists)
    # print(cursors)


    for posting in shortest:
        doc_id = int(posting['document_id'])
        for j, gen in enumerate(cursors):
            try:
                first_at_or_after = recents[j] if recents[j]['document_id'] == doc_id else next(x for x in gen if int(x['document_id']) >= doc_id)
            except StopIteration:
                first_at_or_after = {'document_id': -1}

            first_at_or_after_id = int(first_at_or_after['document_id'])
            # print(f'first found after {doc_id} was {first_at_or_after_id}')
            if first_at_or_after_id != doc_id:
                break
        else:
            # For loop finished. Entry was found in all lists.
            final_list.append(posting)
            continue # continue the outer loop

        # Terminated loop without finishing. Entry was not found in all lists
        pass

    diff = time.perf_counter() - start
    print(f'Query took {round(diff * 1000, 3)}ms\n\nResults:')

    final_list.sort(key=lambda d: -d['frequency'])
    urls_list = [documents.get_url(int(d['document_id'])) for d in final_list[:20]]
    results = urls_list[:20]
    url_set = set()
    for url in reversed(results):
        normalized = re.sub(r'#.*$', '', url)
        if normalized in url_set: results.remove(url)
        else: url_set.add(normalized)


    for url in results[:5]:
        print('  ' + url)
    
    print('\n')
    return results[:5]


def main():
    search(input('term: '))


if __name__ == '__main__':
    main()
