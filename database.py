import sqlite3


class DataBase:

    def __init__(self, vk_id):
        self.conn = sqlite3.connect('data.db')
        self.cur = self.conn.cursor()
        self.vk_id = vk_id

    def create_table(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users(
                                           vk_id INT,
                                           stage INT,
                                           login TEXT,
                                           password TEXT); """)
        self.conn.commit()

    def information(self):
        self.cur.execute(f"""SELECT * from users where vk_id = {self.vk_id}""")
        return self.cur.fetchone()

    def new_user(self):
        self.cur.execute("""SELECT * from users """)
        id_list = [row[0] for row in self.cur.fetchall()]
        if self.vk_id not in id_list:
            self.cur.execute(
                f"""INSERT INTO users (vk_id,stage,login, password) VALUES ('{self.vk_id}' , -1 , NULL , NULL)""")
            self.conn.commit()

    def update_stage(self, stage):
        self.cur.execute(f"""UPDATE users set stage = '{stage}' where vk_id = {self.vk_id}""")
        self.conn.commit()

    def update_information(self, login=0, password= 0):
        if login == 0: login = self.information()[1]
        if password == 0: password = self.information()[2]

        self.cur.execute(f"""UPDATE users set login = '{login}' where vk_id = {self.vk_id}""")
        self.cur.execute(f"""UPDATE users set password = '{password}' where vk_id = {self.vk_id}""")
        self.conn.commit()

    def writer(self,column_name,data):
        self.cur.execute(f"""UPDATE users set '{column_name}' = '{data}' where vk_id = {self.vk_id}""")
        self.conn.commit()

    def delete_user(self):
        self.cur.execute(f"""DELETE from users where vk_id = {self.vk_id}""")
        self.conn.commit()