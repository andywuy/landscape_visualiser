"""
tools for reading and writing OPTIM input and output files
"""

import numpy as np
from viewland.storage import Minimum, TransitionState
from viewland.storage import Database

class OptimDBConverter(object):
    """
    converts PATHSAMPLE to pele database

    Parameters
    ----------
    database : pele Database
        the minima and transition states will be place in here
    
    mindata, tsdata : str
        the files to read from.  The files contain
            min.data   : information about the minima (like the energy)
            min.ts     : information about transition states (like which minima they connect)

    """
    def __init__(self, database : Database, 
                 mindata="min.data",
                 tsdata="ts.data"):
        self.db = database
        self.mindata = mindata
        self.tsdata = tsdata
        return

    def ReadMinDataFast(self):
        """
        read min.data file

        this method uses bulk database inserts.  It is *MUCH* faster this way, but 
        you have to be careful that this and the Minimum object stays in sync.  e.g.
        minimum.invalid must be set to false manually here.
        """
        print("reading from", self.mindata)
        indx = 0 # record how many minima are read in.
        minima_dicts = []
        for line in open(self.mindata, 'r'):
            sline = line.split()
            coords = np.zeros(1)

            # read data from the min.data line
            # energy and vibrational free energy
            e, fvib = list(map(float, sline[:2]))
            pg = int(sline[2])  # point group order

            # create the minimum object and attach the data
            # must add minima like this.  If you use db.addMinimum()
            # some minima with similar energy might be assumed to be duplicates
            min_dict = dict(energy=e, coords=coords, invalid=0, #False,
                            fvib=fvib, pgorder=pg
                            )
            minima_dicts.append(min_dict)

            indx += 1

        self.db.engine.execute(Minimum.__table__.insert(), minima_dicts)
        self.db.session.commit()

        print("--->finished loading %s minima" % indx)

    def ReadTSdataFast(self):
        """read ts.data file

        this method uses bulk database inserts.  It is *MUCH* faster this way, but 
        you have to be careful that this and the TransitionState object stays in sync.  e.g.
        ts.invalid must be set to false manually here.

        """
        print("reading from", self.tsdata)

        indx = 0 # record how many transition states are read in.
        ts_dicts = []
        for line in open(self.tsdata, 'r'):
            sline = line.split()
            coords = np.zeros(1)

            # read data from the min.ts line
            e, fvib = list(map(float, sline[:2]))  # get energy and fvib
            pg = int(sline[2])  # point group order
            m1indx, m2indx = list(map(int, sline[3:5]))

            # must add transition states like this.  If you use db.addtransitionState()
            # some transition states might be assumed to be duplicates
            tsdict = dict(energy=e, coords=coords, invalid=0, #False,
                          fvib=fvib, pgorder=pg,
                          _minimum1_id=m1indx,
                          _minimum2_id=m2indx
                          )
            ts_dicts.append(tsdict)

            indx += 1

        self.db.engine.execute(TransitionState.__table__.insert(), ts_dicts)
        self.db.session.commit()

        print("--->finished loading %s transition states" % indx)

    def convert_no_coords(self):
        """convert pathsample database to pele database without loading coordinates"""
        self.ReadMinDataFast()
        self.ReadTSdataFast()