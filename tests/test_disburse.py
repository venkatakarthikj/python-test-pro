import unittest
import logging
from decimal import Decimal

from src.disburse import DisburseRequest, CryptoDisburseRequest

log = logging.getLogger('parseEntropyEmails')

all_machines = [
    DisburseRequest
]


class TestDisburse(unittest.TestCase):
    """

    """

    default_params = dict(initial='submitted',  # Initial state
                  requested_by='test_user',
                  requesting_app='test_program',
                  purpose='test',
                  amount=Decimal('0.0001'),
                  crypto_currency='BTC',
                  crypto_address='1HB5XMLmzFVj8ALj6mfBsbifRoD4miY36v')

    def test_transitions_easy(self):
        params = dict(TestDisburse.default_params)
        params.pop('crypto_currency')
        params.pop('crypto_address')
        dr = DisburseRequest(**params)

        cdr = CryptoDisburseRequest(**TestDisburse.default_params)

        self.assertEqual(dr.state, cdr.state)
        self.assertEqual(dr.state, 'submitted')

        cdr.to_approved()
        dr.to_approved()

        self.assertEqual(dr.state, cdr.state)
        self.assertEqual(dr.state, 'approved')

        cdr.to_node_ack()
        # the general Disbursement Request does not have a 'node acknowledgement state'; The crypto subclass does
        with self.assertRaises(AttributeError):
            dr.to_node_ack()

    def test_decimal_conversion(self):
        params = dict(TestDisburse.default_params)
        for amt in [1, 1.5, 1.234, Decimal(1.34456), 1]:
            params['amount'] = amt
            cdr = CryptoDisburseRequest(**params)
            self.assertIsInstance(cdr.amount, Decimal)
            try:
                self.assertAlmostEqual(amt, cdr.amount, places=4)
            except TypeError:
                self.assertAlmostEqual(Decimal(amt), cdr.amount, places=4)

    def test_complete_instantiation(self):
        dr = CryptoDisburseRequest(
            initial='submitted',#Initial state
            requested_by='test_user',
            requesting_app='test_program',
            purpose='test',
            amount=Decimal('0.0001'),
            crypto_currency='BTC',
            crypto_address='1HB5XMLmzFVj8ALj6mfBsbifRoD4miY36v')


        self.assertTrue(dr.is_submitted(),
                        'submitted state')
        dr.to_approved()
        self.assertTrue(dr.is_approved(),
                        'approved state')

        if dr.is_approved():
            # Send it (could write a send_to_node() function
            dr.to_sent()
            self.assertEqual(dr.state, 'sent',
                             'After sending we should be in the sent state')

        print dr

if __name__ == "__main__":
    unittest.main()