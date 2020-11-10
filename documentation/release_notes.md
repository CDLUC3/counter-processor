# Release Notes

## 2020-11
- Python 3.7+ is now required because some Sqlite3 library changes are only available in that version
of python or later.  These are changes that allow backing up in-memory to on-disk databases and the reverse.
- This adds some optimizations such as adding an index on country and reducing some unique value lengths
(used for deduplicating similar requests) by subsitituing a hash for a longer string.
- Now loads database from disk into memory on startup and saves to disk again after new items are added.
  - This speeds up data insertion and stat generation speed at the expense of using some memory.
  - If the sqlite database gets too large then storing in memory on normal hardware may not be feasible.
  However, at that scale a number of kinds of re-architecting may be required, even if not storing in
  memory.
- Refactoring of `config.py` to make it look more like a standard Python object, though it is a singleton.
- Rudimentary tests added.
  -  Examples: `python3 -m unittest test/test_main.py` and `python3 -m unittest test/config/test_config.py`
 