from db_connection import *
from peewee import *


class BaseModel(Model):
    class Meta:
        database = sqlite_db


class Track(BaseModel):
    id = PrimaryKeyField(null=False)
    title = CharField(max_length=256)
    sc_id = IntegerField(null=True)

    class Meta:
        db_table = "tracks"


def add_track(title):
    row = Track(
        title=title,
    )
    row.save()
