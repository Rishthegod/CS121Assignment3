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
