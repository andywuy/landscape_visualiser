import numpy as np
from viewland.storage import Minimum, TransitionState, Database

__all__ = ["Converter"]


class Converter(object):
    """
    Converts PATHSAMPLE files (min.data and ts.data) about minima and 
    transition states into the database

    Parameters
    ----------
    database : viewland Database
        the minima and transition states will be place in here.
    mindata : str, optional
        Path to min.data, which is the file that contains information about the 
        minima (like the energy).
    tsdata : str, optional
        Path to min.ts which is a file that contains information about 
        transition states (like which minima they connect).

    Attributes
    ----------
    db : viewland Database
        the minima and transition states will be place in here.
    mindata : str
        Path to min.data, which is the file that contains information about the 
        minima (like the energy).
    tsdata : str
        Path to min.ts which is a file that contains information about 
        transition states (like which minima they connect). 

    """

    def __init__(
        self, database: Database, mindata="min.data", tsdata="ts.data"
    ):
        self.db = database
        self.mindata = mindata
        self.tsdata = tsdata
        return

    def read_min_data(self):
        """Read min.data file."""

        print("reading from", self.mindata)
        # record how many minima are read in.
        indx = 0
        minima_dicts = []
        for line in open(self.mindata, "r"):
            sline = line.split()
            coords = np.zeros(1)

            # read data from the min.data line
            # energy and vibrational free energy
            e, fvib = list(map(float, sline[:2]))
            # point group order
            pg = int(sline[2])

            # create the minimum object and attach the data
            min_dict = dict(
                energy=e, coords=coords, invalid=0, fvib=fvib, pgorder=pg
            )
            minima_dicts.append(min_dict)

            indx += 1

        self.db.engine.execute(Minimum.__table__.insert(), minima_dicts)
        self.db.session.commit()

        print("--->finished loading %s minima" % indx)

    def read_ts_data(self):
        """read ts.data file """
        print("reading from", self.tsdata)

        # record how many transition states are read in.
        indx = 0
        ts_dicts = []
        for line in open(self.tsdata, "r"):
            sline = line.split()
            coords = np.zeros(1)

            # read data from the min.ts line
            e, fvib = list(map(float, sline[:2]))  # get energy and fvib
            pg = int(sline[2])  # point group order
            m1indx, m2indx = list(map(int, sline[3:5]))

            tsdict = dict(
                energy=e,
                coords=coords,
                invalid=0,
                fvib=fvib,
                pgorder=pg,
                _minimum1_id=m1indx,
                _minimum2_id=m2indx,
            )
            ts_dicts.append(tsdict)

            indx += 1

        self.db.engine.execute(TransitionState.__table__.insert(), ts_dicts)
        self.db.session.commit()

        print("--->finished loading %s transition states" % indx)

    def convert_no_coords(self):
        """Convert pathsample database without loading coordinates."""
        self.read_min_data()
        self.read_ts_data()
