import pytest
import pytest_asyncio
from uop.core.plugin_testing.harness import Plugin, AsyncPlugin
from uop.sql.postgres import adaptor
from uop.meta.schemas.predefined import pkm_schema
import uuid


@pytest.fixture(scope="session")
def db_harness():
    """
    Pytest fixture to set up and tear down a SQLite test database.
    """
    db_name = f"test_db_{uuid.uuid4().hex}"
    master = adaptor.MasterDatabase(
        database="mydatabase",
        user="myuser",
        password="mypassword",
        port=5432,
        host="localhost",
    )

    master.ensure_database_named(db_name)
    db = adaptor.SQLDatabase(
        db_name, 'pkm_schema', username="myuser", password="mypassword"
    )
    db.open_db()
    plug_in = Plugin(db)

    yield plug_in  # Provide the database adapter instance to the tests

    # No need to drop the default database, just close the connection
    db.close_db()
    master.drop_database_named(db_name)
    # TODO: get rid of this postgres database after tests complete


@pytest_asyncio.fixture(scope="function")
async def async_db_harness():
    """
    Pytest fixture to set up and tear down a PostgreSQL test database.
    """
    db_name = f"test_db_{uuid.uuid4().hex}"
    master = adaptor.MasterDatabase(
        database="mydatabase",
        user="myuser",
        password="mypassword",
        port=5432,
        host="localhost",
    )

    master.ensure_database_named(db_name)
 #   db = adaptor.AsyncSQLDatabase(
 #       db_name, 'pkm_schema', username="myuser", password="mypassword", driver="asyncpg"
 #   )
    db = adaptor.AsyncSQLDatabase(
        db_name, 'pkm_schema', username="myuser", password="mypassword"
    )
    await db.open_db()
    plug_in = AsyncPlugin(db)

    yield plug_in  # Provide the database adapter instance to the tests

    # No need to drop the default database, just close the connection
    await db.close_db()
    master.drop_database_named(db_name)
