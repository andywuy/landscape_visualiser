from viewland.utils import DisconnectivityGraph, database2graph, Converter
from viewland.storage import Database
from viewland.storage.database import create_connect_string

import numpy as np
from matplotlib import cm
import os
import configparser
import matplotlib.pyplot as plt

plt.rcParams["font.size"] = 24
plt.rcParams["figure.autolayout"] = True


def test_gen_tree():
    """
    Test if the disconnectivity graph is generated correctly by checking the 
    number of nodes in the graph.
    """

    # Define the paths to the test data files.
    dir_testdata = "tests/testdata"
    path_tinfo = os.path.join(dir_testdata, "tinfo")
    path_min_data = os.path.join(dir_testdata, "min.data")
    path_ts_data = os.path.join(dir_testdata, "ts.data")

    # Create the database.
    string = create_connect_string()
    print("connection string to the database is: ", string)
    db = Database(string)

    # Read in data from min.data and ts.data.
    converter = Converter(db, mindata=path_min_data, tsdata=path_ts_data)
    converter.convert_no_coords()

    # Read in the configurations from tinfo.
    config = configparser.ConfigParser()
    config.read(path_tinfo)
    # Minimum value of the colorbar.
    CMIN = float(config["settings"]["CMIN"])
    # Maximum value of the colorbar.
    CMAX = float(config["settings"]["CMAX"])
    # Path to the color values of the minimum.
    PATH_COLOR = config["settings"]["PATH_COLOR"]
    PATH_COLOR = os.path.join(dir_testdata, PATH_COLOR)
    # Maximum energy level.
    EMAX = float(config["settings"]["EMAX"])
    # Minimum energy level.
    EMIN = float(config["settings"]["EMIN"])
    # Step size for basin analysis.
    STEP = float(config["settings"]["STEP"])
    # Colormap name.
    CMAP = config["settings"]["CMAP"]
    # File name for saving the disconnectivity graph.
    OUT = config["settings"]["OUT"]

    # Define the colorbar range.
    # color_range will be scaled to [0,1] by cm.ScalarMappable.
    color_range = [CMIN, CMAX]

    # Read in color values of the minima.
    values = np.genfromtxt(PATH_COLOR)

    # Scale the values according to colorbar range.
    values = values / (CMAX - CMIN) - (CMIN / (CMAX - CMIN) - 0)

    # Set the energy levels. Must be ascending list of floats.
    elevels = list(np.arange(EMIN, EMAX + STEP, STEP, dtype=float))

    # Create the disconnectivity graph
    graph = database2graph(db)
    dg = DisconnectivityGraph(graph)
    dg.set_energy_levels(elevels)
    dg.calculate()

    # Color the minima
    def minimum_to_value(mini):
        """
        Auxilary function used by dg.color_by_value.
        
        Parameter
        ---------
        mini : Minimum

        Return
        ------
        color of the minimum : float
        """
        # The index of mini starts from 1, but values index starts from 0.
        return float(values[int(mini.id()) - 1])

    dg.color_by_value(
        minimum_to_value, colormap=cm.get_cmap(CMAP), normalize_values=False
    )

    # Draw the disconnectivity graph.
    dg.plot(linewidth=3)
    fig = plt.gcf()
    fig.set_size_inches(5, 5)
    mappable = cm.ScalarMappable(cmap=cm.get_cmap(CMAP))
    mappable.set_array(color_range)
    fig.colorbar(
        mappable=mappable, shrink=0.3, ticks=[CMIN, 0, CMAX], pad=0.01
    )
    # fig.savefig(OUT)

    # Check if the graph has the right number of nodes as expected.
    assert dg.graph.number_of_nodes() == 10

    # Must close the database connection at the end.
    db.close()
