from build_index import find_bucket
from nltk import PorterStemmer
from partial_index import documents
from term_finder import load_glossary_from_disk
import time
import re
from pathlib import Path
from score_calculator import rank_score
from math import log10


glossary = load_glossary_from_disk()
total_docs = len(documents._url_lookup)
print(f'Loaded Glossary with {len(glossary.keys())} keys and {total_docs} docs')


def get_idf(t):
    return log10(total_docs / t[2]) if t[2] != 0 else 0


def search(user_input: str):
    query = {*user_input.strip().split(' ')}
    doc_lists = {}
    final_list = []

    stemmer = PorterStemmer()
    terms = [(term, *glossary.get(stemmer.stem(term), [-1, 0])) for term in query]  # [term, position, doc_count]
    terms.sort(key = lambda t: t[2])                                                # ascending doc count
    highest_idf = max([get_idf(t) for t in terms])
    idf_threshold = (highest_idf / 3) if highest_idf > 3 else \
        (highest_idf / 2 if highest_idf > 0.75 else 0)
    terms = [t for t in terms if get_idf(t) >= idf_threshold]     # Kept terms
    all_stopwords = highest_idf <= 0.5           # highest idf <= 0.5
    print('Kept terms:', terms, all_stopwords)


    start = time.perf_counter()

    # Get lists for each term
    for term, lookup_position, doc_freq in terms:
        stemmed = PorterStemmer().stem(term)
        # print(term, stemmed, find_bucket(stemmed))
        bucket = find_bucket(stemmed)

        print(f'Reading bucket for "{term}" (idf={log10(total_docs / doc_freq)})...')
        # lookup_position, doc_freq = glossary.get(stemmed, [-1, 0])
        # print(f'pos={lookup_position}, ct={doc_freq}')
        # data = bucket._disk_index.read_from_disk()
        # doc_list: dict = data.get(stemmed, {})
        if lookup_position > -1:
            doc_list = bucket.read_term_at_position(lookup_position)
            entries = [*doc_list.values()]
            # sorted_entries.sort(key=lambda x: int(x['document_id']))
        else:
            entries = []

        doc_lists[term] = entries
    

    # if all_stopwords:
    #     # perform boolean matching
    #     start2 = time.perf_counter()
    #     ranked = find_conjunction(doc_lists)
    #     start2, t = time.perf_counter(), time.perf_counter() - start2
    #     print(f'Join: {round(t*1000, 2)}ms')
    #     ranked = rank_score([t[0] for t in terms], doc_lists, total_docs)
    #     t = time.perf_counter() - start2
    #     print(f'Rank: {round(t*1000, 2)}ms')
    # else:
    ranked = rank_score([t[0] for t in terms], doc_lists, total_docs)

    
    print(ranked[:5])


    diff = time.perf_counter() - start
    print(f'Query took {round(diff * 1000, 3)}ms\n\nResults:')

    # final_list.sort(key=lambda d: -d['frequency'])
    final_list = ranked
    urls_list = [documents.get_url(int(d[1])) for d in final_list[:20]]
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
    search(input('Query: '))


if __name__ == '__main__':
    main()
