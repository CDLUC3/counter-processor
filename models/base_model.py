from peewee import *

# db = SqliteDatabase('db/counter_db.sqlite3')
deferred_db = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = deferred_db
