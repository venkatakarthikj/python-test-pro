
"""
nosetests tests\test_entropyMailParse.py
"""
import unittest
import logging

from src.disburse import DisburseRequest
from src.purchase import PurchaseRequest

log = logging.getLogger('parseEntropyEmails')

all_machines = [
    DisburseRequest,
    PurchaseRequest,
]


class TestInstantiate(unittest.TestCase):
    """

    

    def test_noparam_create(self):
        for machine in all_machines:
            machine_instance = machine()

            self.assertIsInstance(machine_instance, AthenaStateMachine)
            self.assertIsNotNone(machine_instance.state)

            print "Created: %s" % machine_instance
    """
    pass

if __name__ == "__main__":
    unittest.main()