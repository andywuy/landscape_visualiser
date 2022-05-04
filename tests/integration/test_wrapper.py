from viewland.utils import create_graph
import os

def test_create_graph():
    """
    Test if the disconnectivity graph is generated correctly.
    """

    # Define the paths to the test data files.
    dir_testdata = "tests/testdata"
    path_conf = os.path.join(dir_testdata, "tinfo")
    path_colour = os.path.join(dir_testdata, "diff.map")
    path_min_data = os.path.join(dir_testdata, "min.data")
    path_ts_data = os.path.join(dir_testdata, "ts.data")
    
    # Define where the output file should be.
    output = os.path.join(dir_testdata, "temporary.png")

    create_graph(path_min_data, path_ts_data, path_conf, path_colour, output)
    
    assert os.path.isfile(output) == True

    os.remove(output)
    return
    


