"""
Module include the base class for all our state machines

Lets figure out how to use a real orm....
https://github.com/pytransitions/transitions


 - can we show something like this for audit:
    https://github.com/pytransitions/transitions#-diagrams

"""
import abc
import time
import logging
from exceptions import DeprecationWarning

from transitions import Machine

# from transitions.extensions import GraphMachine as Machine


class abstractstatic(staticmethod):
    """
    https://stackoverflow.com/a/4474495/1257603
    """
    __slots__ = ()

    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True

    __isabstractmethod__ = True


logging.getLogger('transitions').setLevel(logging.DEBUG)


class AthenaStateMachine(Machine):
    """
    State machines track the state of some object within the Athena environment

    Some examples:
        - Disbursements
        - Orders
        - Users (for onboarding)
    """

    def __init__(self, *args, **kwargs):
        """

        :param initial: initial state, bust be in get_states()
        :param persist_store: if we want to persist this object on transitions, pass in this object
                if there is no object passed, in we won't persist.
        :param persistent_id_field: the name of the field that is the persistent id.  It will be
            set when we persist and used to look up
        :param store_success_transition_only: True or False; whether we want to store before and after
        :param args:
        :param kwargs:
        """
        self.log = logging.getLogger(self.__class__.__name__)

        assert('transitions' not in kwargs)
        assert('states' not in kwargs)

        params = {
            'transitions': self.get_transitions(),
            'states': self.get_states(),
        }
        if 'initial' not in kwargs:
            first_listed_state = params['states'][0]
            self.log.warn("You should provide an initial state, defaulting to %s", first_listed_state)
            params['initial'] = first_listed_state

        for param, value in [('prepare_event', 'prepare'),
                             ('finalize_event', 'finalize'),
                            ('after_state_change', 'after'),
                            ('before_state_change', 'before'),
                            ('send_event', True)]:
            if param in kwargs:
                continue
            self.log.debug("Defaulting %s to %s", param, value)
            params[param] = value

        self.persist_store = None
        if 'loader' in kwargs:
            self.persist_store = kwargs.pop('loader')
            logging.warnings.warn("Use persist_store rather than loader",
                                  category=DeprecationWarning)

        if 'persist_store' in kwargs:
            self.persist_store = kwargs.pop('persist_store')

        try:
            self.store_success_transition_only = kwargs.pop('store_success_transition_only')
        except KeyError:
            self.store_success_transition_only = True

        try:
            self.persistent_id_field = kwargs.pop('persistent_id_field')
        except KeyError:
            self.persistent_id_field = 'uuid'
        setattr(self, self.persistent_id_field, None)

        params.update(kwargs)

        super(AthenaStateMachine, self).__init__(**params)

    @abc.abstractmethod
    def __repr__(self):
        raise RuntimeError("__repr__ Must be implemented")

    @abstractstatic
    def get_states():
        """
        Returns the states this object may be in
        :return:
        """
        raise RuntimeError("get_states Must be implemented")

    @abstractstatic
    def get_transitions():
        """
        describes the transitions allowed by this statemachine
        :return:
        """
        raise RuntimeError("get_transitions Must be implemented")


    def prepare(self, event):
        self.log.debug('Preparing %s', event)
        #if self.loader:
        #    #self.transistion_event('prepare', self, event)
        #    pass

    def finalize(self, event):
        self.log.debug('Finalizing')

    def after(self, event):
        self.log.debug('After %s', event)

        if self.persist_store:
            self.persist_on_event(event_trigger='after', event=event)

    def before(self, event):
        self.log.debug('Before %s', event)

        if not self.store_success_transition_only:
            assert(self.persist_store)
            self.persist_on_event('before', event)

    @property
    def persistent_id(self):
        """
        Returns the persistent id.  This id refers to the keys used to uniquely identify the states that are persisted,
        not the object itself.
        :return:
        """
        return getattr(self, self.persistent_id_field)

    @staticmethod
    def from_persistence(persistent_store, persistent_id, set_persistent_id=True):
        if not hasattr(persistent_store, 'retrieve'):
            raise NotImplementedError("If you want to use %s for persistence, implement 'retrieve'" % persistent_store)

        object = persistent_store.retrieve(persistent_id)
        if not object:
           logging.getLogger("PersistenceLoad").debug("Failed looking up %s", persistent_id)
        elif set_persistent_id:
            setattr(object, object.persistent_id_field, persistent_id)

        return object

    def load_from_persistence(self, persistent_id, set_persistent_id=True, loader=None):
        """

        :param persistent_id:
        :param loader:
        :return:
        """

        return AthenaStateMachine.from_persistence(
            loader if loader else self.persist_store,
            persistent_id=persistent_id,
            set_persistent_id=set_persistent_id)

    def persist_on_event(self, event_trigger, event):
        self.log.debug("Persisting %s", self)

        if not hasattr(self.persist_store, 'store'):
            raise NotImplementedError("If you want to use %s for persistence, implement 'store'" % self.persist_store)

        start_time = time.time()
        try:
            persisted_key = self.persist_store.store(machine=self,
                                                     event_trigger=event_trigger,
                                                     event=event)
        except (NameError, TypeError), ne:
            # These are programming errors
            raise
        except Exception, e:
            self.log.exception("Failed storing %s", self)
            raise
        self.log.debug("Stored in %s seconds", time.time() - start_time)
        try:
            key_as_int = int(persisted_key)
        except ValueError:
            received_negative = False
        else:
            received_negative = key_as_int <= 0

        if persisted_key is None or received_negative:
            self.log.warn("When we stored %s, we received back %s", self, persisted_key)
            return

        setattr(self, self.persistent_id_field, persisted_key)
