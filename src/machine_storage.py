import logging
import datetime
import uuid
import time
from decimal import Decimal

#must use dill, not cPickle for machines
import dill as pickle
#import cPickle as pickle
from boto3.dynamodb.types import Binary

from __init__ import __version__

class DynamoStore(object):

    def __init__(self, table):
        self.log = logging.getLogger("DynamoStorage")
        if not table:
            raise ValueError("Must supply a table")

        if str(type(table)).find('dynamodb.Table') == -1:
            raise TypeError("table must be of type dynamo table; got %s" % type(table))

        self.table = table

        # TODO: make these variables, but at a minimum, I think we need:
        self.storage_details = {
            'blob_field': 'pickled',
            'persistent_id': 'uuid',
            'previous_id': 'previous_id',
            'persist_dt': 'save_utc'
        }

    def _to_pickle(self, machine, utc_now, event_trigger):
        return pickle.dumps(
            {'machine': machine,
             'meta': {
                 'previous_persistent_id': machine.persistent_id,
                 'event_trigger': event_trigger,
                 'utc_time': utc_now,
                 'apsm':{
                     '__version__': __version__,
                 }
             }})

    def store(self, machine, event_trigger, event, *args, **kwargs):
        """
        Stores a machine into a dynamo table

        :param machine:
        :param event_trigger:
        :param event:
        :param args:
        :param kwargs:
        :return:
        """
        new_id = uuid.uuid4().get_hex()
        old_id = machine.persistent_id
        utc_now = datetime.datetime.utcnow()
        original_store = machine.persist_store

        # We do not want to store all the underlying implementation of this object,
        #  so we'll remove the store attribute
        delattr(machine, 'persist_store')
        try:
            pickled = self._to_pickle(machine, utc_now, event_trigger)
        finally:
            setattr(machine, 'persist_store', original_store)
        binary_pickle = Binary(pickled)
        self.log.debug("Pickle is %s long... Binary pickle ??", len(pickled))
        result = self.table.put_item(
            Item={
                self.storage_details['persistent_id']: new_id,
                self.storage_details['blob_field']: binary_pickle,
                self.storage_details['previous_id']: old_id,
                self.storage_details['persist_dt']: Decimal(time.mktime(utc_now.timetuple()))
            }
        )

        if not result:
            raise NotImplementedError()

        return new_id

    def retrieve(self, persistent_id, *args, **kwargs):
        """
        retrieves this
        :param persistent_id:
        :param args:
        :param kwargs:
        :return:
        """
        key = {
            self.storage_details['persistent_id']: {
                'S': persistent_id
            }
        }
        try:
            raw_row = self.table.get_item(key)
        except Exception, e:
            self.log.exception("Failed looking up key=%s in %s",
                               key,
                               self.table.table_arn)
            raise

        data = raw_row[self.storage_details['blob_field']]
        pickle.loads(data)