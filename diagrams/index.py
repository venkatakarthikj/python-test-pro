from transitions.extensions import GraphMachine as Machine
from graphviz import Digraph


class MachineState(object):
    pass


# The states
states = ['init', 'new', 'assigned', 'pending', 'paid', 'delivered']

# And some transitions between states.
transitions = [{'trigger': 'select_product', 'source': 'new', 'dest': 'assigned'}]


# Initialize
machine = MachineState()
fsm = Machine(machine, states=states, transitions=transitions, initial=states[0],
              auto_transitions=False)
dot = Digraph(comment='FSM')

for label, event in fsm.events.items():
    for event_transitions in event.transitions.values():
        for transition in event_transitions:
            dot.edge(transition.source, transition.dest, label)
machine.get_graph().draw('apsm_diagram_03.png', prog='dot')
print(dot)
