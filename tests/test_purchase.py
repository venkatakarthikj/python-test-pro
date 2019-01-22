
"""
nosetests tests\test_entropyMailParse.py
"""
import unittest
import logging

from src.purchase import PurchaseRequest


class TestPurchase(unittest.TestCase):
    """

    """

    def test_transitions(self):
        pr = PurchaseRequest()

        pr.quote_price()
        self.assertIs(pr.state, 'price_quoted')

        pr.submit()
        self.assertIs(pr.state, 'pending_payment_confirmation')

        pr.confirm_payment()
        self.assertIs(pr.state, 'awaiting_delivery')

        pr.deliver()
        self.assertIs(pr.state, 'delivered')


if __name__ == "__main__":
    unittest.main()