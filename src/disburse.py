import os
from decimal import Decimal

try:
    from athena_sm import AthenaStateMachine
except ImportError:
    import sys
    sys.path.append( os.path.join(os.path.dirname(__file__), "..", 'src'))
    from athena_sm import AthenaStateMachine


class DisburseRequest(AthenaStateMachine):
    """
    The disburse request represents a desire to withdraw an asset from the company.

    The subclass, CryptoDisburseRquest, handles the particulars of a withdraw
    of Crypto currency.

    """
    def __init__(self, requested_by, requesting_app,
                 purpose, amount, loader=None, *args, **kwargs):
        """
        Instantiates a DisburseRequest
        :param request_id:
        :param args:
        :param kwargs:
        """
        problems = []
        self.requested_by = requested_by if requested_by else os.getlogin()
        self.requesting_app = requesting_app
        self.purpose = purpose

        if not isinstance(amount, Decimal):
            problems.append("Converting %s to a Decimal" % amount)
            self.amount = Decimal("%0.08f" % amount)
        else:
            self.amount = amount
        self.loader = loader
        self.id_field = 'request_id'

        super(DisburseRequest, self).__init__(send_event=True,
                                              prepare_event='prepare',
                                              finalize_event='finalize',
                                              after_state_change='after',
                                              before_state_change='before',
                                              **kwargs)

        if len(problems):
            self.log.warn('\n'.join(problems))

    def __repr__(self):
        return "Disbursement Request: By: %s, App %s, Amount %s" % (
            self.requested_by, self.requesting_app, self.amount)

    @staticmethod
    def get_states():
        return [
            'submitted',  # just waiting to be evaluated
            'approved',
            'sent',  # we sent it to the disbursing asset (node, bank, ach processor, exchange, etc)
            'confirmed',
            'denied',
            'failed_to_send',
        ]

    @staticmethod
    def get_transitions():
        return [
            {'trigger': 'approve', 'source': 'submitted', 'dest': 'approved'},
            {'trigger': 'deny', 'source': ['submitted', 'approved'], 'dest': 'denied'},
            {'trigger': 'node_ack', 'source': ['approved'], 'dest': 'node_ack'},
            {'trigger': 'fail_to_send', 'source': ['approved'], 'dest': 'failed_to_send'},
        ]

    def as_dict(self):
        return dict([(f, getattr(self, f)) for f in self.fields])


class CryptoDisburseRequest(DisburseRequest):

    def __init__(self, crypto_currency, crypto_address, **kwargs):
        self.crypto_currency = crypto_currency
        self.crypto_address = crypto_address

        for f in ['crypto_currency', 'crypto_address']:
            if f not in kwargs:
                continue
            kwargs.pop(f)

        super(CryptoDisburseRequest, self).__init__(**kwargs)

    @staticmethod
    def get_states():
        states_from_sub = DisburseRequest.get_states()
        states_from_sub.extend(
            ['node_ack',
            'node_broadcast',  # the node has broadcast
            ])
        return states_from_sub
