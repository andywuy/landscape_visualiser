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
    '''
    Test the creation of the database.
    If the test fails, check the connection string first and set environment 
    variables appropriately. 
    '''
    conn = create_connect_string()
    print("The connection string is: ", conn)
    db = Database(conn)
    assert db.number_of_transition_states() == 0 and db.number_of_minima() == 0
    db.close()
    return
