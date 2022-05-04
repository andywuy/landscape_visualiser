from viewland.utils import DisconnectivityGraph, database2graph, Converter
from viewland.storage import Database
from viewland.storage.database import create_connect_string

from matplotlib import cm
import os
import configparser
import sys
import matplotlib.pyplot as plt
import numpy as np

__all__ = ["create_graph"]

def create_graph(mindata : str, tsdata : str, conf : str,
        colour : str, output : str):
    '''
    This wrapper function read in data and create the disconnectivity graph.

    Parameters
    ----------

    '''
    # Check the existence of files
    dic = {'min.data' : mindata,
            'ts.data' : tsdata,
            'configuration file' : conf,
            'minima colouring file' : colour,
            }
    for key, value in dic.items():        
        try:
            if not os.path.exists(value):
                raise IOError("{} is missinng!".format(key))
        except IOError as err:
            print(err)
            sys.exit(1)

    # Parse the configuration file
    config = configparser.ConfigParser()
    config.read(conf)
    # Minimum value of the colorbar.
    cmin = float(config["settings"]["CMIN"])
    # Maximum value of the colorbar.
    cmax = float(config["settings"]["CMAX"])
    # Maximum energy level.
    emax = float(config["settings"]["EMAX"])
    # Minimum energy level.
    emin = float(config["settings"]["EMIN"])
    # Step size for basin analysis.
    step = float(config["settings"]["STEP"])
    # Matplotlib colormap name.
    cmap = config["settings"]["CMAP"]

    # Read in data to the database
    db = Database(create_connect_string())
    converter = Converter(db, mindata, tsdata)
    converter.convert_no_coords()

    # Define the colorbar range.
    # color_range will be scaled to [0,1] by cm.ScalarMappable.
    color_range = [cmin, cmax]

    # Read in color values of the minima.
    values = np.genfromtxt(colour)
    
    # Scale the values according to the colorbar range.
    values = values / (cmax - cmin) - cmin / (cmax - cmin)

    # Define the energy levels, which must be an ascending list of floats.
    elevels = list(np.arange(emin, emax + step, step, dtype=float))

    # Create the disconnectivity graph.
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
        minimum_to_value, colormap=cm.get_cmap(cmap), normalize_values=False
    )
    

    # Draw the disconnectivity graph and save it.
    plt.rcParams["font.size"] = 24
    plt.rcParams["figure.autolayout"] = True
    dg.plot(linewidth=3)
    fig = plt.gcf()
    fig.set_size_inches(5, 5)
    mappable = cm.ScalarMappable(cmap=cm.get_cmap(cmap))
    mappable.set_array(color_range)
    fig.colorbar(
        mappable=mappable, shrink=0.3, ticks=[cmin, 0, cmax], pad=0.01
    )
    fig.savefig(output)
    # print(dg.graph.number_of_nodes(), graph.number_of_edges())

    # Must close the database connection at the end.
    db.close()

    return
