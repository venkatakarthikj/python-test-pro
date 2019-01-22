try:
    from athena_sm import AthenaStateMachine
except ImportError:
    import os
    import sys
    sys.path.append( os.path.join(os.path.dirname(__file__), "..", 'src'))
    from athena_sm import AthenaStateMachine


class PurchaseRequest(AthenaStateMachine):
    """
    Purchase Requests have
     - Quantities
     - Prices
     - Delivery Instructions
     - Payment terms (Currency and amount customer to deliver)
     - User
    """

    def __init__(self, *args, **kwargs):
        super(PurchaseRequest, self).__init__(**kwargs)

    def __repr__(self):
        return "This is a purchase request... "

    @staticmethod
    def get_states():
        return [
            'pre_price_quote',
            'price_quoted',
            'user_submitted',
            'bad_order',
            'compliance_review',
            'confirm_payment',
            'pending_payment_confirmation',
            'awaiting_delivery',
            'delivered',
        ]

    @staticmethod
    def get_transitions():
        return [
            {'trigger': 'quote_price', 'source': ['price_quoted', 'pre_price_quote'], 'dest': 'price_quoted'},
            {'trigger': 'submit', 'source': 'price_quoted', 'dest': 'pending_payment_confirmation',
                'conditions': ['is_dest_address_ok', 'is_existing_inventory_ok', 'is_within_limits', 'is_kyc_ok']},
            {'trigger': 'confirm_payment', 'source': 'pending_payment_confirmation', 'dest': 'awaiting_delivery'},
            {'trigger': 'deliver', 'source': 'awaiting_delivery', 'dest': 'delivered'},
        ]

    def is_kyc_ok(self, event_data):
        self.log.warn("Defaulting to OK KYC, override function to check KYC")
        return True

    def is_dest_address_ok(self, event_data):
        self.log.warn("Defaulting to OK address, override function to confirm that destination address is ok")
        return True

    def is_existing_inventory_ok(self, event_data):
        self.log.warn("Defaulting to OK inventory, override function to make sure we'll have enough inventory")
        return True

    def is_within_limits(self, event_data):
        self.log.warn("Defaulting to OK for limits, override function to make sure we'll have enough inventory")
        return True