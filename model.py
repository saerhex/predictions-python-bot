import sqlite3


class Participants:

    def __init__(self, datbase_name):
        self.dbn = datbase_name
        self.create_database()

    def create_database(self):
        db = sqlite3.connect(self.dbn)
        cursor = db.cursor()
        cursor.execute("""create table if not exists participants
                          (user_id text,username text,prediction text,money real);
                       """)
        db.commit()
        db.close()

    def insert_values(self, values: tuple):
        str_vals = values[:-1]
        _money = values[-1]
        db = sqlite3.connect(self.dbn)
        cursor = db.cursor()
        cursor.execute("insert into participants values (?, ?, ?, ?);", (*str_vals, _money,))
        db.commit()
        db.close()

    def get_value(self, user_id: str):
        db = sqlite3.connect(self.dbn)
        cursor = db.cursor()
        cursor.execute("select username,prediction,sum(money) from participants group by username having user_id=?;",
                       (user_id, ))
        db.commit()
        results = cursor.fetchone()
        db.close()
        return results

    def get_prediction(self, user_id: str):
        db = sqlite3.connect(self.dbn)
        cursor = db.cursor()
        cursor.execute('select prediction from participants where user_id="id";', {"id": user_id})
        db.commit()
        results = cursor.fetchone()
        db.close()
        return results

    def get_all(self):
        db = sqlite3.connect(self.dbn)
        cursor = db.cursor()
        cursor.execute('select user_id, username, prediction, sum(money) from participants group by user_id')
        db.commit()
        results = cursor.fetchall()
        db.close()
        return results
