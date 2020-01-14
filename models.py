import sqlite3
from sqlite3 import Error
import pandas.io.sql as sql


class DataBase:
    database = "pythonsqlite.db"

    def create_connection(self, db_file):
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return conn


    def create_table(self, conn, create_table_sql):
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)


    def create_project(self, conn, project):
        sql = ''' INSERT INTO projects(filename,path,md5sum)
                  VALUES(?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, project)
        return cur.lastrowid


    def main(self):
        sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS projects (
                                            id integer PRIMARY KEY,
                                            filename text NOT NULL,
                                            path text,
                                            md5sum text
                                        ); """

        conn = self.create_connection(self.database)

        if conn is not None:
            self.create_table(conn, sql_create_projects_table)
        else:
            print("Error! cannot create the database connection.")


    def create_record(self, filename, path, md5sum):
        conn = self.create_connection(self.database)
        with conn:
            project = (filename, path, md5sum);
            self.create_project(conn, project)


    def delete_all_tasks(self):
        conn = self.create_connection(self.database)
        sql = 'DELETE FROM projects;'
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

    def export_to_csv(self):
        conn = sqlite3.connect(self.database)
        table = sql.read_sql('select * from projects', conn)
        table.to_csv('results.csv', index=False, header=False)
