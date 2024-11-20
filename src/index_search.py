from build_index import find_bucket, all_buckets
from nltk import PorterStemmer
from partial_index import documents


def main():
    query = input('term: ').split(' ')
    doc_lists = []
    final_list = []

    # Get lists for each term
    for term in query:
        stemmed = PorterStemmer().stem(term)
        print(term, stemmed, find_bucket(stemmed))
        bucket = all_buckets[find_bucket(stemmed)]

        print('Reading bucket...')
        data = bucket._disk_index.read_from_disk()
        doc_list: dict = data.get(stemmed, {})
        sorted_entries = [*doc_list.values()]
        sorted_entries.sort(key=lambda x: int(x['document_id']))
        doc_lists.append(sorted_entries)
    
    shortest_len = min([len(l) for l in doc_lists])
    print('lengths', [len(l) for l in doc_lists])
    shortest = next((l for l in doc_lists if len(l) == shortest_len))

    print(shortest_len, doc_lists.index(shortest))
    cursors = [(i for i in list) for list in doc_lists]
    recents = [{'document_id': -1}] * len(doc_lists)
    print(cursors)


    for i, posting in enumerate(shortest):
        doc_id = int(posting['document_id'])
        for j, gen in enumerate(cursors):
            try:
                first_at_or_after = recents[j] if recents[j]['document_id'] == doc_id else next(x for x in gen if int(x['document_id']) >= doc_id)
            except StopIteration:
                first_at_or_after = {'document_id': -1}

            first_at_or_after_id = int(first_at_or_after['document_id'])
            print(f'first found after {doc_id} was {first_at_or_after_id}')
            if first_at_or_after_id != doc_id:
                break
        else:
            print('completed loop successfully (found doc in all terms)')
            final_list.append(posting)
            continue # outer loop

        print('terminated loop without finishing')

    urls = [documents.get_url(int(d['document_id'])) for d in final_list[:5]]
    print(urls)



    



if __name__ == '__main__':
    main()
