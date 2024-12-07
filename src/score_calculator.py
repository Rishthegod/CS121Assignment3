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



def calculate_idf(data: dict, c_length: int):
    df = len(data)
    print(df)
    return log10(c_length / df)
    
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
        elif freq_type == "frequency_title": 
            weight += count * Multipliers.PageTitle.value

        total_words += count

    avg_weight = weight / total_words
    return avg_weight*freq_ratio



def rank_score(query, index, c_length):
    k = 5
    accumulator = {}
    term_postings = []
    pq = []

    for term in query:
        if term in index:
            term_postings.append(index[term])


    for posting in term_postings:
        num_docs = len(posting)
        for key in posting.keys():
            if key not in accumulator:
                accumulator[key] = 0
        for doc_id, data in posting.items():
            log_tdf = log10(weighted_tf(data) + 1)
            idf = c_length / num_docs
            accumulator[doc_id] +=  log_tdf * idf
    
    for doc_id, score in accumulator.items():
        heapq.heappush(pq, (score, doc_id))
        if len(pq) > k:
            heapq.heappop(k)
        
    return sorted(pq, reverse=True)

def main():
    example_index = {
        "hello" : {
            0 : {
                "frequency_normal" : 102,
                "frequency_bold" : 90,
                "frequency_title" : 8,
                "frequency" : 0.05
            },

            1 : {
                "frequency_normal" : 21,
                "frequency_bold" : 4,
                "frequency_title" : 1,
                "frequency" : 0.50
            },
            
            2 : {
                "frequency_normal" : 1,
                "frequency_bold" : 1,
                "frequency_title" : 2000,
                "frequency" : 0.40
            }
        },
        "earl" : {
            0 : {
                "frequency_normal" : 10,
                "frequency_bold" : 20,
                "frequency_title" : 1,
                "frequency" : 0.80
            }
        }
    }
    print(rank_score(["hello", "earl"], example_index, 10))
    # print(example_index)
if __name__ == "__main__":

    main()
