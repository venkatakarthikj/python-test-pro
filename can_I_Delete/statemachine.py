"""
Module include the base class for all our state machines

Lets figure out how to use a real orm....
https://github.com/pytransitions/transitions


 - can we show something like this for audit:
    https://github.com/pytransitions/transitions#-diagrams

"""
import logging

from transitions import Machine as PyTransitionsMachine
from statemachineinterface import StateMachineInterface

logging.getLogger('transitions').setLevel(logging.DEBUG)


class AthenaStateMachine(PyTransitionsMachine):
    """
        State machines track the state of some object within the Athena environment

        Some examples:
            - Disbursements
            - Orders
            - Users (for onboarding)
        """

    def __init__(self, *args, **kwargs):
        self.log = logging.getLogger(self.__class__.__name__)

        assert ('transitions' not in kwargs)
        assert ('states' not in kwargs)
        super(AthenaStateMachine, self).__init__(
            states=self.get_states(),
            transitions=self.get_transitions(),
            **kwargs)

    def get_state(self, state_name):
        """
        Returns the state fr
        :return:
        """
        return

    def get_states_list(self):
        """
        Returns the states this object may be in
        :return:
        """
        return

    def get_transitions_list(self):
        """
        describes the transitions allowed by this statemachine
        :return:
        """
        return

