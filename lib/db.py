import psycopg2, config, psycopg2.extras

class PgSQL:
    def __init__(self):
        self.user   = config.db_user
        self.passwd = config.db_pass
        self.host   = config.db_host
        self.db     = config.db_name
        self.conn   = psycopg2.connect(host=self.host, user=self.user, password=self.passwd, dbname=self.db)
        self.cursor = self.conn.cursor()
    
    def truncate(self, table, row=1):
        self.cursor.execute("TRUNCATE TABLE " + table)
        self.cursor.execute("ALTER SEQUENCE " + table + "_id_seq RESTART WITH " + str(row))
        self.conn.commit()
    
    def insert(self, rows=[], table=None):
        # psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)
        # psycopg2.extensions.register_adapter(list, psycopg2.extras.Json)
        for row in rows:
            keys   = row.keys()
            values = ["'" + row[k] + "'" if isinstance(row[k], basestring) else row[k] for k in keys]
            query = "INSERT INTO %s (%s) VALUES (%s)" % (table, ", ".join(keys), ", ".join(values))
            print query + "\n"
            self.cursor.execute(query)
        self.conn.commit()
        
    def select(self, cols="*", table=None, where=None, order=None, limit=None):
        """Generalized Select statement."""
        if isinstance(cols, basestring):
            columns = cols
        if isinstance(cols, list):
            columns = ", ".join(cols)
        if where:
            if isinstance(where, basestring):
                # The parameter passed is something like: where="client='Client A' AND gender='Female'"
                clause = where
            if isinstance(where, list):
                # The parameter passed is something like: where=["client='Client A'", "gender='Female'"]
                clause = " AND ".join(where)
            if isinstance(where, dict):
                # The parameter passed is something like: where={"client":'Client A', "gender":"Female"}
                cl = []
                for k, v in where.items():
                    cl.append(k+"='"+v+"'" if isinstance(v, basestring) else k+"="+v)
                clause = " AND ".join(cl)
            if order:
                if limit:
                    query = "SELECT %s FROM %s WHERE %s ORDER BY %s LIMIT %d" % (columns, table, clause, order, limit)
                else:
                    query = "SELECT %s FROM %s WHERE %s ORDER BY %s" % (columns, table, clause, order)
            elif limit:
                query = "SELECT %s FROM %s WHERE %s LIMIT %d" % (columns, table, clause, limit)
            else:    
                query = "SELECT %s FROM %s WHERE %s" % (columns, table, clause)
        elif order:
            if limit:
                query = "SELECT %s FROM %s ORDER BY %s LIMIT %d" % (columns, table, order, limit)
            else:    
                query = "SELECT %s FROM %s ORDER BY %s" % (columns, table, order)
        else:
            query = "SELECT %s FROM %s" % (columns, table)
        
        # print query + "\n"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def sql(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()
    