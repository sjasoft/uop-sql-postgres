from re import A
from uop.sql.base import adaptor as base
from uop.sql.base import async_adaptor as async_base
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool, AsyncConnectionPool

class MasterDatabase:
    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    def get_connection(self):   
        return psycopg.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database
        )
    
    def ensure_database_named(self, db_name):
        conn = self.get_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.close()
        conn.close()

    def drop_database_named(self, db_name):
        conn = self.get_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
        cursor.close()
        conn.close()

class SQLDatabase(base.SQLBaseDatabase):
    """PostgreSQL adaptor."""

    _pool: ConnectionPool = None

    @classmethod
    def init_pool(cls, user, password, host, port, database, min_size=2, max_size=10):
        """Initialize connection pool once at application startup."""
        cls._pool = ConnectionPool(
            min_size,
            max_size,
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
            cursor_factory=dict_row,
        )
    

    def get_connection(self):
        return self._pool.getconn()


    def open_db(self):
        """Opens the database connection."""
        if not self._pool:
            self.init_pool(
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
            )
        self._conn = self.get_connection()
        self._autoconn = self.get_connection()
        self.set_autocommit(self._autoconn, True)
        super().open_db()

    def get_existing_tables(self):
        with self._conn.cursor() as cursor:
            cursor.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            )
            return [row[0] for row in cursor.fetchall()]


class SQLCollection(base.SQLBaseCollection):
    """MariaDB collection."""

    pass

class AsyncSQLCollection(async_base.AsyncSQLBaseCollection):
    """PostgreSQL async collection."""
    pass

class AsyncSQLDatabase(async_base.AsyncSQLBaseDatabase):
    """PostgreSQL async database."""

_pool: AsyncConnectionPool = None

@classmethod
def init_pool(cls, user, password, host, port, database, min_size=2, max_size=10):
    """Initialize connection pool once at application startup."""
    cls._pool = AsyncConnectionPool(
        min_size,
        max_size,
        user=user,
        password=password,
        host=host,
        port=port,
        database=database,
        cursor_factory=dict_row,
    )
    