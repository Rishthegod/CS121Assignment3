from math import log10
# from token_bucket import TermType
import heapq
from enum import Enum


class Multipliers(Enum):
    Normal = 1
    Bold = 1.5
    Heading = 2
    Anchor = 2
    PageTitle = 3


def weighted_tf(data: dict):
    freq_ratio = data["frequency"]

    weight = 0
    total_words = 0
    for freq_type, count in data.items():
        if freq_type == "frequency_normal": 
            weight += count * Multipliers.Normal.value
        elif freq_type == "frequency_bold": 
            weight += count * Multipliers.Bold.value
        elif freq_type == "frequency_heading": 
            weight += count * Multipliers.Heading.value
        elif freq_type == "frequency_anchor": 
            weight += count * Multipliers.Anchor.value
        elif freq_type == "frequency_page_title": 
            weight += count * Multipliers.PageTitle.value
        else: continue

        total_words += count

    if total_words < 10 and freq_ratio > 0.05:
        return 0 # too few tokens for this document to be meaningful

    doc_length = total_words / freq_ratio

    avg_weight = weight / total_words
    return avg_weight * freq_ratio * log10(doc_length)



def rank_score(query, index, c_length):
    k = 5
    accumulator = {}        # Map:  doc_id ==> tf.idf
    term_collections = []
    pq = []

    for term in query:
        if term in index:
            term_collections.append(index[term])
        else:
            print('term somehow not found')

    first_idf = None
    for i, term_postings in enumerate(term_collections):
        num_docs = len(term_postings)
        if num_docs == 0: continue

        idf = log10(c_length / num_docs)
        print(f'idf = {idf} for {query[i]}')
        if not first_idf: first_idf = idf
        elif idf < first_idf / 2:
            print(f'Skipping term "{query[i]}"')
            continue

        # for key in term_postings.keys():
        #     if key not in accumulator:
        #         accumulator[key] = 0
        # for doc_id, data in term_postings.items():
        for data in term_postings:
            doc_id = data['document_id']

            log_tdf = log10(weighted_tf(data) + 1)
            # print(f'{doc_id}: tdf is {log_tdf}')
            accumulator[doc_id] = accumulator.get(doc_id, 0) + log_tdf * idf
    
    for doc_id, score in accumulator.items():
        heapq.heappush(pq, (score, doc_id))
        # if len(pq) > k:
        #     heapq.heappop(k)
        
    return sorted(pq, reverse=True)


def main():
    example_index = {
        "hello" : [
            {
                "document_id": 0,
                "frequency_normal" : 102,
                "frequency_bold" : 90,
                "frequency_page_title" : 8,
                "frequency" : 0.05
            },
            {
                "document_id": 1,
                "frequency_normal" : 21,
                "frequency_bold" : 4,
                "frequency_page_title" : 1,
                "frequency" : 0.50
            },
            {
                "document_id": 2,
                "frequency_normal" : 1,
                "frequency_bold" : 1,
                "frequency_page_title" : 2000,
                "frequency" : 0.50
            }
        ],
        "earl" : [{
            "document_id": 0,
            "frequency_normal" : 10,
            "frequency_bold" : 20,
            "frequency_page_title" : 1,
            "frequency" : 0.80
        }]
    }
    print(rank_score(["hello", "earl"], example_index, 10))
    # print(example_index)


if __name__ == "__main__":
    main()
