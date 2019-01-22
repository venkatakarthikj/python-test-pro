import logging
from transitions import Machine

logging.basicConfig(level=logging.DEBUG)
# Set transitions' log level to INFO; DEBUG messages will be omitted
logging.getLogger('transitions').setLevel(logging.INFO)


class StateMachine(object):

    def __init__(self):
        pass

    def __get__(self, instance, owner):
        pass

