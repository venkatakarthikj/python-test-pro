
"""
Test Simple persistence
"""
import unittest
import sqlite3
import datetime
import base64
#must use dill, not cPickle for machines
import dill as pickle
#import cPickle as pickle

from src.athena_sm import AthenaStateMachine

class SimplePersistedStateMachine(AthenaStateMachine):

    def __init__(self, *args, **kwargs):
       super(SimplePersistedStateMachine, self).__init__(
           initial='created', **kwargs)

    @staticmethod
    def get_states():
        return ['created', 'changed', 'persisted']

    @staticmethod
    def get_transitions():
        return [{
            'trigger': 'persist',
            'source': ['created', 'changed', 'persisted'],
            'dest': 'persisted'
        },]

    def __repr__(self):
        return u"Test Object @ State=%s" % self.state

    def prepare(self, event):
        self.log.debug('Preparing')
        #if self.loader:
        #    #self.transistion_event('prepare', self, event)
        #    pass

    def finalize(self, event):
        self.log.debug('Finalizing')

class SqlLiteStorage(object):
    """
    approach described here:
        https://docs.python.org/3.4/library/pickle.html#persistence-of-external-objects
    """

    def __init__(self):

        #super(pickle.Pickler, self).__init__(file=None)

        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("create table simple_persistence (v1 varchar(10), v2 BLOB, saved_at datetime, "
                          "id INTEGER PRIMARY KEY AUTOINCREMENT)")

    def __del__(self):
        self.conn.close()
        del self.conn
        self.conn = None

    def store(self, machine, event_trigger, event, *args, **kwargs ):

        if not isinstance(machine, SimplePersistedStateMachine):
            raise NotImplementedError
        pickled = pickle.dumps(
            {'machine': machine,
             'meta': {
                 'previous_persistent_id': machine.persistent_id,
                 'event_trigger': event_trigger,
                 'utc_time': datetime.datetime.utcnow()
             }}
        )
        cur = self.conn.cursor()

        cur.execute("insert into simple_persistence(v1, v2, saved_at) values (?, ?, ?)",
                    (machine.state, base64.b64encode(pickled), datetime.datetime.utcnow()))
        cur.connection.commit()
        return cur.lastrowid


    def retrieve(self, id):
        cur = self.conn.cursor()

        cur.execute("select v2 from simple_persistence where id = ?",
                    (id, ))

        for v2, in cur.fetchall():

            as_blob = base64.b64decode(v2)

            loaded = pickle.loads(as_blob)

            #make sure this thing wasn't modified or manipulated... pickles aren't secure
            return loaded['machine']


        raise LookupError("Could not find %s" % id)

class TestSimplePersistence(unittest.TestCase):
    """

    """

    def setUp(self):

        self.pickler = SqlLiteStorage()
        self.spsm = SimplePersistedStateMachine(loader=self.pickler)

        self.assertEqual(self.spsm.state, 'created')

    def tearDown(self):
        self.assertIsInstance(self.spsm, AthenaStateMachine)
        del self.spsm
        self.spsm = None

        del self.pickler
        self.pickler = None

    def get_table_size(self):
        cur = self.pickler.conn.cursor()
        cur.execute("select count(*) from simple_persistence")
        row = cur.fetchone()
        return row[0]

    def test_persist_change_and_store(self):
        self.assertEqual(self.spsm.state, 'created')
        self.assertEqual(self.get_table_size(), 0)

        self.spsm.persist()

        self.assertEqual(self.get_table_size(), 1)
        self.assertEqual(self.spsm.state, 'persisted')

        # Now lets try to load it.
        new_object = self.spsm.load_from_persistence(self.spsm.persistent_id)
        self.assertNotEqual(self.spsm, new_object)
        self.assertIsInstance(new_object, SimplePersistedStateMachine)

    def test_persist_load(self):
        spsm2 = SimplePersistedStateMachine(persist_store=self.pickler,
                                            store_success_transition_only=False)
        self.assertEqual(spsm2.state, 'created')
        self.assertEqual(self.get_table_size(), 0)

        spsm2.persist()

        #one saved for the before; the other for the after
        self.assertEqual(self.get_table_size(), 2)
        self.assertEqual(spsm2.state, 'persisted')

        # Now lets try to load it.
        new_object = spsm2.load_from_persistence(spsm2.persistent_id)
        self.assertNotEqual(spsm2, new_object)
        self.assertIsInstance(new_object, SimplePersistedStateMachine)

    def test_persist_change_and_store(self):
        self.assertEqual(self.spsm.state, 'created')
        self.assertEqual(self.get_table_size(), 0)

        for i in range(100):
            self.spsm.persist()

            self.assertEqual(self.spsm.state, 'persisted')
            self.assertEqual(self.spsm.persistent_id, i + 1)

    def test_simple_w_fields(self):

        spsmwf = SimplePersistedStateMachine(persist_store=self.pickler,
                                            store_success_transition_only=True)
        spsmwf.fake_receive_address = 'abc'

        self.assertEqual(spsmwf.state, 'created')
        self.assertEqual(spsmwf.fake_receive_address, 'abc')
        spsmwf.persist()

        self.assertEqual(self.get_table_size(), 1)
        self.assertEqual(spsmwf.state, 'persisted')

        self.assertEqual(spsmwf.fake_receive_address, 'abc')

        #try retrieving another
        s2 = spsmwf.load_from_persistence(spsmwf.persistent_id)

        self.assertTrue(hasattr(s2, 'fake_receive_address'))

        self.assertEqual(s2.fake_receive_address, spsmwf.fake_receive_address)
        self.assertEqual(s2.persistent_id, spsmwf.persistent_id)
        self.assertEqual(s2.fake_receive_address, 'abc')

        spsmwf.fake_receive_address = 'def'
        self.assertNotEqual(s2.fake_receive_address, spsmwf.fake_receive_address)

        persisted = spsmwf.persist()
        self.assertTrue(persisted)
        self.assertEqual('def', spsmwf.fake_receive_address)

        self.assertNotEqual(s2.fake_receive_address, spsmwf.fake_receive_address)

        s2b = spsmwf.load_from_persistence(spsmwf.persistent_id, set_persistent_id=False)
        self.assertEqual('def', s2b.fake_receive_address)
        #self.assertIsNone(s2b.persistent_id)


if __name__ == "__main__":
    unittest.main()