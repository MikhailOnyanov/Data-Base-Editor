import psycopg2 as psycopg2
import psycopg2.extras
import urllib.parse as up
import os
from dotenv import load_dotenv


class MyDbManager:
    def __init__(self, local_db=True):
        #  Loads db connection info from .env file
        load_dotenv()
        #  Connect to local Postgres db
        if local_db:
            self.conn = psycopg2.connect(database=os.getenv("POSTGRESQL_DB"),
                                         user=os.getenv("POSTGRESQL_USER"),
                                         password=os.getenv("POSTGRESQL_PASS"))
        else:
            #  Connect to ElephantSQL
            up.uses_netloc.append("postgres")
            url = up.urlparse(os.environ["DATABASE_URL"])
            self.conn = psycopg2.connect(database=url.path[1:],
                                         user=url.username,
                                         password=url.password,
                                         host=url.hostname,
                                         port=url.port)
        self.conn.autocommit = True

    #  Creates table by given name and fields
    def create_table(self, table_name: str, d_fields: tuple):
        field_count = len(d_fields)
        j = 0

        fields_sql = ""
        for field in d_fields:
            j += 1
            fields_sql += f"{field['name']} {field['datatype']}"
            if field['primary_key'] == 'True':
                fields_sql += ' PRIMARY KEY'
            #  Add separator to the field
            if j != field_count:
                fields_sql += ', '
        #  Result query
        query = f"CREATE TABLE IF NOT EXISTS {table_name}({fields_sql})"
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            cursor.close()
            return query
        except Exception as error:
            print('Whoops! Something went wrong. ', error)

    # Returns list of table names
    def get_table_names(self):
        query = """SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"""

        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            for elem in result:
                print(elem)
                if elem[0] == "pg_stat_statements":
                    result.remove(elem)
            cursor.close()
        except Exception as error:
            print('Whoops! Something went wrong. ', error)

        #  Because we get strange format of table names
        return [result[i][0] for i in range(len(result))]

    # Returns fields with datatype for specified table
    def get_table_fields(self, table_name):
        query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';"
        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as error:
            print('Whoops! Something went wrong. ', error)

    def delete_table(self, table_name):
        with self.conn:
            cursor = self.conn.cursor()
            query = f"DROP TABLE IF EXISTS {table_name}"
            try:
                cursor.execute(query)
                cursor.close()
            except Exception as error:
                print('Whoops! Something went wrong. ', error)

    def update_table_name(self, table_name_old, table_name_new):
        query = f"ALTER TABLE {table_name_old} RENAME TO {table_name_new};"
        with self.conn:
            cursor = self.conn.cursor()
            try:
                cursor.execute(query)
                cursor.close()
                return query
            except Exception as error:
                return('Whoops! Something went wrong. ', error)

    def add_table_column(self, table_name, field_name, datatype):
        query = f"ALTER TABLE {table_name}  ADD COLUMN {field_name} {datatype};"
        with self.conn:
            cursor = self.conn.cursor()
            try:
                cursor.execute(query)
                cursor.close()
                return query
            except Exception as error:
                return('Whoops! Something went wrong.', error)

    def close_connection(self):
        if self.conn.closed:
            pass
        else:
            self.conn.close()