from peewee import SqliteDatabase, Model, DateField, CharField, AutoField, TimeField
import os

# データベース接続の定義
db = SqliteDatabase("my_database.db", timeout=10.0)


def is_database_exists() -> bool:
    """データベースファイルが存在するか確認"""
    return os.path.exists("my_database.db")


class Schedule(Model):
    id = AutoField(primary_key=True)
    mode = CharField(null=True)
    name = CharField()
    start_date = DateField()
    start_time = TimeField()
    end_date = DateField()
    end_time = TimeField()

    class Meta:
        database = db
