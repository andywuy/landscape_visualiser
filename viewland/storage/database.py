"""Database for simulation data in a relational database
"""
import numpy as np

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Float, PickleType

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, deferred
from sqlalchemy.ext.declarative import declarative_base


__all__ = ["Minimum", "TransitionState", "Database"]

verbose = False

Base = declarative_base()


class Minimum(Base):
    """
    The Minimum class represents a minimum in the database.

    Parameters
    ----------
    energy : float
        energy of the minimum.
    coords : numpy array
        coordinates of the minimum.

    Attributes
    ----------
    energy :
        the energy of the minimum.
    coords :
        the coordinates of the minimum.  This is stored as a pickled numpy
        array which SQL interprets as a BLOB.
    fvib :
        the log product of the squared normal mode frequencies.
    pgorder :
        point group order
    invalid :
        a flag that can be used to indicate a problem with the minimum.  E.g. if
        the Hessian has more zero eigenvalues than expected.
    user_data :
        Space to store anything that the user wants.  This is stored in SQL
        as a BLOB, so you can put anything here you want as long as it's serializable.
        Usually a dictionary works best.


    See Also
    --------
    Database, TransitionState
    """
    __tablename__ = 'tbl_minima'

    _id = Column(Integer, primary_key=True)
    energy = Column(Float)
    # deferred means the object is loaded on demand, that saves some time / memory for huge graphs
    coords = deferred(Column(PickleType))
    '''coordinates of the minimum'''
    fvib = Column(Float)
    """log product of the squared normal mode frequencies"""
    pgorder = Column(Integer)
    """point group order"""
    invalid = Column(Integer)
    """flag indicating if the minimum is invalid"""
    user_data = deferred(Column(PickleType))
    """this can be used to store information about the minimum"""

    def __init__(self, energy, coords):
        self.energy = energy
        self.coords = np.copy(coords)
        self.invalid = False

    def id(self):
        """return the sql id of the object"""
        return self._id

    def __eq__(self, m):
        """m can be integer or Minima object"""
        assert self.id() is not None
        if isinstance(m, Minimum):
            assert m.id() is not None
            return self.id() == m.id()
        else:
            return self.id() == m

    def __hash__(self):
        _id = self.id()
        assert _id is not None
        return _id

    def __repr__(self):
        return "<Minimum(id='{}', energy='{}'>".format(self._id, self.energy)


class TransitionState(Base):
    """
    The TransitionState class represents a saddle point in the database.

    Parameters
    ----------
    energy : float
        energy of the transition state.
    coords : numpy array
        coordinates of the transition state.
    min1 : Minimum object
        first minimum connected to the transition state.
    min2 : Minimum object
        second minimum connected to the transition state.
    eigenval : float, optional
        lowest (single negative) eigenvalue of the saddle point
    eigenvec : numpy array, optional
        eigenvector which corresponds to the negative eigenvalue
    fvib : float
        log product of squared frequencies for free energy calculation
    pgorder : integer
        point group order



    Attributes
    ----------
    energy :
        The energy of the transition state
    coords :
        The coordinates of the transition state.  This is stored as a pickled numpy
        array which SQL interprets as a BLOB.
    fvib :
        The log product of the squared normal mode frequencies.  This is used in
        the free energy calcualations
    pgorder :
        The point group order
    invalid :
        A flag that is used to indicate a problem with the transition state.  E.g. if
        the Hessian has more than one negaive eigenvalue then it is a higher order saddle.
    user_data :
        Space to store anything that the user wants.  This is stored in SQL
        as a BLOB, so you can put anything here you want as long as it's serializable.
        Usually a dictionary works best.
    minimum1, minimum2 :
        These returns the minima on either side of the transition state
    eigenvec :
        The vector which points along the direction crossing the transition state.
        This is the eigenvector of the lowest non-zero eigenvalue.
    eigenval :
        The eigenvalue corresponding to `eigenvec`.  A.k.a. the curvature
        along the direction given by `eigenvec`


    See Also
    --------
    Database, Minimum
    """
    __tablename__ = "tbl_transition_states"
    _id = Column(Integer, primary_key=True)

    energy = Column(Float)
    '''energy of transition state'''

    coords = deferred(Column(PickleType))
    '''coordinates of transition state'''

    _minimum1_id = Column(Integer, ForeignKey('tbl_minima._id'))
    minimum1 = relationship("Minimum",
                            primaryjoin="Minimum._id==TransitionState._minimum1_id")
    '''first minimum which connects to transition state'''

    _minimum2_id = Column(Integer, ForeignKey('tbl_minima._id'))
    minimum2 = relationship("Minimum",
                            primaryjoin="Minimum._id==TransitionState._minimum2_id")
    '''second minimum which connects to transition state'''

    eigenval = Column(Float)
    '''coordinates of transition state'''

    eigenvec = deferred(Column(PickleType))
    '''coordinates of transition state'''

    fvib = Column(Float)
    """log product of the squared normal mode frequencies"""
    pgorder = Column(Integer)
    """point group order"""
    invalid = Column(Integer)
    """flag indicating if the transition state is invalid"""
    user_data = deferred(Column(PickleType))
    """this can be used to store information about the transition state """

    def __init__(self, energy, coords, min1, min2, eigenval=None, eigenvec=None):
        assert min1.id() is not None
        assert min2.id() is not None

        self.energy = energy
        self.coords = np.copy(coords)
        if min1.id() < min2.id():
            self.minimum1 = min1
            self.minimum2 = min2
        else:
            self.minimum1 = min2
            self.minimum2 = min1

        if eigenvec is not None:
            self.eigenvec = np.copy(eigenvec)
        self.eigenval = eigenval
        self.invalid = False

    def id(self):
        """return the sql id of the object"""
        return self._id

    def __repr__(self):
        return "<TransitionState(id='{}', energy='{}'>".format(self._id, self.energy)


class Database(object):
    """
    Database storage class
    The Database class uses SQLAlchemy to handle the connection to the database. 

    Parameters
    ----------
    connect_string : string
        connection string for sqlalchemy.create_engine .
    createdb : boolean, optional
        create database if not exists, default is true.

    Attributes
    ----------
    engine : sqlalchemy database engine
    session : sqlalchemy session

    Examples
    --------
    >>> from viewland.storage import Database
    >>> db = Database()
    >>> # TODO: show how to add minima and TS to the database
    >>> for minimum in database.minima():
    >>>     print minimum.energy
    
    See Also
    --------
    Minimum
    TransitionState
    """
    engine = None
    session = None

    def __init__(self,
                 connect_string='postgresql+psycopg2://temp:12345678@localhost:5432/books',
                 createdb=True):

        self.engine = create_engine(connect_string)
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

        # set up the session which will manage the frontend connection to the database
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_lowest_energy_minimum(self):
        """return the minimum with the lowest energy"""
        candidates = self.session.query(Minimum).order_by(Minimum.energy).\
            limit(1).all()
        return candidates[0]

    def get_minimum_from_id(self, id):
        """return the minimum with a given id """
        return self.session.query(Minimum).get(id)

    def get_transition_state_from_id(self, id):
        """return the transition state with id """
        return self.session.query(TransitionState).get(id)

    def get_transition_state_between_minima(self, min1: Minimum, min2: Minimum):
        """return the TransitionState between two minima.

        Returns
        -------
        ts : None or TransitionState
        """
        m1, m2 = min1, min2
        candidates = self.session.query(TransitionState).\
            filter(or_(
                and_(TransitionState.minimum1 == m1,
                     TransitionState.minimum2 == m2),
                and_(TransitionState.minimum1 == m2,
                     TransitionState.minimum2 == m1),
            ))

        for m in candidates:
            return m
        return None

    def get_transition_states_connected_to_minimum(self, min1: Minimum):
        """return all transition states connected to a minimum.

        Returns
        -------
        ts : None or TransitionState
        """
        candidates = self.session.query(TransitionState).\
            filter(or_(TransitionState.minimum1 == min1,
                       TransitionState.minimum2 == min1))

        return candidates.all()

    def minima(self, order_energy=True):
        """return an iterator over all minima in database

        Parameters
        ----------
        order_energy : bool
            order the minima by energy

        Returns
        -------
        min : Minimum
        """
        if order_energy:
            return self.session.query(Minimum).order_by(Minimum.energy).all()
        else:
            return self.session.query(Minimum).all()

    def transition_states(self, order_energy=False):
        """return an iterator over all transition states in database

        Returns
        -------
        ts : TransitionState
        """
        if order_energy:
            return self.session.query(TransitionState).order_by(TransitionState.energy).all()
        else:
            return self.session.query(TransitionState).all()

    def number_of_minima(self):
        """return the number of minima in the database"""
        return self.session.query(Minimum).count()

    def number_of_transition_states(self):
        """return the number of transition states in the database"""
        return self.session.query(TransitionState).count()
