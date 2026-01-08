from peewee import SqliteDatabase,Model,DateField,CharField,AutoField,TimeField

# データベース接続の定義
db = SqliteDatabase('my_database.db')

class Schedule(Model):
    id=AutoField(primary_key=True)
    mode = CharField(null=True)
    start_date = DateField()
    start_time = TimeField()
    end_date = DateField()
    end_time = TimeField()
    
    class Meta:
        database = db