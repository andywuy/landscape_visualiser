from viewland.storage import Database
from viewland.storage.database import create_connect_string


def test_create_connect_string():
    string = create_connect_string(
        "user", "password", "dbname", "1234", "localhost"
    )
    assert (
        string == "postgresql+psycopg2://user:password@localhost:1234/dbname"
    )


def test_database_create():
    conn = create_connect_string()
    print("The connection string is: ", conn)
    db = Database(conn)
    assert db.number_of_transition_states() == 0 and db.number_of_minima() == 0
    db.close()
    return
