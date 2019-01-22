import unittest
import random
import socket
from contextlib import closing

import docker
import boto3

from src.machine_storage import DynamoStore
from src.purchase import PurchaseRequest

class ThinPurchaseRequest(PurchaseRequest):
    pass


class TestDynamoPersistence(unittest.TestCase):
    """

    """

    @staticmethod
    def get_aws_profile():
        #return "dirtydev"
        return None

    @staticmethod
    def get_aws_session():
        """
         docker run -p 8000:8000 amazon/dynamodb-local
         https://github.com/docker/docker-py

         docker_db = docker_client.containers.run('amazon/dynamodb-local', detach=True, ports={8000:8001})
         c = boto3.client("dynamodb", endpoint_url="http://localhost:8000")

        :return:
        """
        return boto3.Session(profile_name=TestDynamoPersistence.get_aws_profile())

    @staticmethod
    def find_open_port():
        """
        https://codereview.stackexchange.com/a/116453
        """

        port = random.randint(8000, 8999)
        while True:
            port = port % 65535
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
                res = sock.connect_ex(('127.0.0.1', port))
                if res == 0:
                    return port
            port += 1

    @staticmethod
    def setUpClass():
        """
        TODO: WE should be trying to use the downloadable one:
        https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/DynamoDBLocal.html
        :return:
        """
        sess = TestDynamoPersistence.get_aws_session()

        open_port = random.randint(8000, 8999)
        #open_port = TestDynamoPersistence.find_open_port()
        docker_client = docker.from_env()
        try:
            TestDynamoPersistence.docker_db = docker_client.containers.run('amazon/dynamodb-local',
                                                                       detach=True,
                                                                       ports={8000:open_port})

        except Exception, e:
            print "Failed starting a container"
            raise e
        db = sess.resource('dynamodb', endpoint_url="http://localhost:%s" % open_port)
        test_table_name = 'testing_%s_%06d' % ("TestDynamoPersistence",  random.randint(0, 10000))
        print("Testing with %s in %s" % (test_table_name, TestDynamoPersistence.get_aws_profile()))

        db_params = {
            'AttributeDefinitions': [
                {
                    'AttributeName':'uuid',
                    'AttributeType':'S'
                }
            ],
            'KeySchema': [
                {
                    'AttributeName': 'uuid',
                    'KeyType': "HASH"
                }
            ],
            'TableName': test_table_name,
            'ProvisionedThroughput': {'ReadCapacityUnits': 1,
                                     'WriteCapacityUnits': 1}
        }
        TestDynamoPersistence.dynamodb_tbl = None
        try:
            TestDynamoPersistence.dynamodb_tbl = db.create_table(**db_params)
        except ValueError, Ve:
            # Getting an error, but the table is still being created
            for t in db.tables.all():
                if t.table_name == test_table_name:
                    TestDynamoPersistence.dynamodb_tbl = t
                    break
            if not TestDynamoPersistence.dynamodb_tbl:
                raise

    @staticmethod
    def tearDownClass():
        """
        :return:
        """
        try:
            TestDynamoPersistence.dynamodb_tbl.delete()
        except ValueError, e:
            print ("TODO: Figure out what about this call is bad & fix it.")
            pass
        TestDynamoPersistence.docker_db.kill()


    def setUp(self):
        self.table = TestDynamoPersistence.dynamodb_tbl
        self.assertIsNotNone(self.table)

    def tearDown(self):
        pass

    def test_create_and_save(self):
        test_table = TestDynamoPersistence.dynamodb_tbl
        persistent_storage = DynamoStore(table=test_table)
        thinest_request = ThinPurchaseRequest(persist_store=persistent_storage)

        self.assertEqual(thinest_request.state, thinest_request.get_states()[0])

        try:
            original_size = test_table.item_count
        except ValueError, ve:
            print ("TODO: timezone errors?  WTF")
            original_size = 1
        self.assertIsNone(thinest_request.persistent_id)

        thinest_request.quote_price()

        self.assertIsNotNone(thinest_request.persistent_id)
        try:
            item_count = test_table.item_count
        except ValueError:
            print("Sort out what is causing item count to fail")
            pass
        else:
            self.assertEqual(original_size + 1, item_count)

    def test_lookup(self):
        test_table = TestDynamoPersistence.dynamodb_tbl
        persistent_storage = DynamoStore(table=test_table)

        thinest_request = ThinPurchaseRequest(persist_store=persistent_storage)
        self.assertIsNone(thinest_request.persistent_id)
        thinest_request.quote_price()

        self.assertIsNotNone(thinest_request.persistent_id)
        loaded_request = ThinPurchaseRequest.from_persistence(persistent_storage,
                                             thinest_request.persistent_id)

        self.assertEqual(loaded_request.state, thinest_request.state)
        self.assertEqual(loaded_request.persistent_id, thinest_request.persistent_id)

        self.assertEqual(thinest_request.state, thinest_request.get_states()[0])
