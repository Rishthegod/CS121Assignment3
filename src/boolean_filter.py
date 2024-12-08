'''
The M2 implementation of the search engine: finding the boolean AND of queries
This is not used for M3
'''

def find_conjunction(doc_lookup: dict):
    final_list = []

    doc_lists = [l for l in doc_lookup.values()]
    for l in doc_lists:
        l.sort(key=lambda x: int(x['document_id']))

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
    
    final_list.sort(key=lambda d: -d['frequency'])
    return final_list
