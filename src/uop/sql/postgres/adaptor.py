from re import A
from uop.sql.base import adaptor as base
from uop.sql.base import async_adaptor as async_base
from uop.sql.postgres import table
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
            dbname=self.database,
        )

    def ensure_database_named(self, db_name):
        conn = self.get_connection()
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE {db_name}")
        cursor.close()
        conn.close()

    def drop_database_named(self, db_name):
        conn = self.get_connection()
        conn.autocommit = True
        conn.execute(
            f"""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = %s AND pid <> pg_backend_pid()
    """,
            (db_name,),
        )
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE  {db_name}")
        cursor.close()
        conn.close()


class SQLDatabase(base.SQLBaseDatabase):
    """PostgreSQL adaptor."""

    Table_Class = table.Table

    _pool: ConnectionPool = None
    JSON_SUPPORTED = True  # Postgres supports JSON natively

    @classmethod
    def init_pool(cls, user, password, host, port, database, min_size=2, max_size=10):
        """Initialize connection pool once at application startup."""
        cls._pool = ConnectionPool(
            min_size=min_size,
            max_size=max_size,
            open=True,
            kwargs={
                "user": user,
                "password": password,
                "host": host,
                "port": port,
                "dbname": database,
                "row_factory": dict_row,
            },
        )

    def get_connection(self):
        return self._pool.getconn()

    def open_db(self):
        """Opens the database connection."""
        host = self._credentials.get("host", "localhost")
        port = self._credentials.get("port", 5432)
        if not self._pool:
            self.init_pool(
                user=self.db_user,
                password=self.db_password,
                host=host,
                port=port,
                database=self._dbname,
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
            return {row['table_name'] for row in cursor.fetchall()}


class SQLCollection(base.SQLBaseCollection):
    """PostgreSQL collection."""

    pass


class AsyncSQLCollection(async_base.AsyncSQLBaseCollection):
    """PostgreSQL async collection."""

    pass


class AsyncSQLDatabase(async_base.AsyncSQLBaseDatabase):
    """PostgreSQL async database."""

    Table_Class = table.Table
    JSON_SUPPORTED = True  # Postgres supports JSON natively

    _pool: AsyncConnectionPool = None

    @classmethod
    def init_pool(cls, user, password, host, port, database, min_size=2, max_size=10):
        """Initialize connection pool once at application startup."""
        cls._pool = AsyncConnectionPool(
            min_size=min_size,
            max_size=max_size,
            open=True,
            kwargs={
                "user": user,
                "password": password,
                "host": host,
                "port": port,
                "dbname": database,
                "row_factory": dict_row,
            },
        )
