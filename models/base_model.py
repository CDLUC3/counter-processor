from peewee import *

db = SqliteDatabase('db/counter_db.sqlite3')

class BaseModel(Model):
    class Meta:
        database = db
