import psycopg2, config, psycopg2.extras

class PgSQL:
    def __init__(self):
        self.user   = config.db_user
        self.passwd = config.db_pass
        self.host   = config.db_host
        self.db     = config.db_name
        self.conn   = psycopg2.connect(host=self.host, user=self.user, password=self.passwd, dbname=self.db)
        self.cursor = self.conn.cursor()
    
    def truncate(self, table):
        self.cursor.execute("TRUNCATE TABLE "+table)
        self.cursor.execute("ALTER SEQUENCE "+table+"_id_seq RESTART WITH 1")
        self.conn.commit()
    
    def insert(self, rows=[], table=None):
        # psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)
        # psycopg2.extensions.register_adapter(list, psycopg2.extras.Json)
        for row in rows:
            keys   = row.keys()
            values = [row[k] for k in keys]
            query = "INSERT INTO %s (%s) VALUES (%s)" % (table, ", ".join(keys), ", ".join(values))
            print query
            self.cursor.execute(query)
        self.conn.commit()
