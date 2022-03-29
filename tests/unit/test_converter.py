from viewland.utils import Converter
from viewland.storage import Database
from viewland.storage.database import create_connect_string


def test_converter():
    db = Database(create_connect_string())
    converter = Converter(
        db, mindata="tests/testdata/min.data", tsdata="tests/testdata/ts.data"
    )
    converter.convert_no_coords()
    assert (
        db.number_of_minima() == 10 and db.number_of_transition_states() == 105
    )
    db.close()
