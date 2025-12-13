import psycopg2
import psycopg2.extras

class Database:
    def __init__(self, dbname, user, password, host="localhost", port=5432):
        self.conn = None
        try:
            self.conn = psycopg2.connect(
                database=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            print("Connected to PostgreSQL successfully!")
        except Exception as e:
            print("Database connection failed:", e)

    def execute_query(self, query, params=None, fetch=False):
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(query, params)

                if fetch:
                    return cur.fetchall()

                self.conn.commit()
                return True
        except Exception as e:
            # Rollback to clear connection error state, log and propagate the
            # exception so callers (UI) can display accurate error messages and
            # avoid continuing as if the operation succeeded.
            try:
                if self.conn:
                    self.conn.rollback()
            except Exception:
                pass
            print("Query error:", e)
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            print("Connection closed.")
