from graphviz import Digraph

from transitions.extensions import MachineFactory


class Matter(object):
    def is_hot(self):
        return True

    def is_too_hot(self):
        return False


GraphMachine = MachineFactory.get_predefined(graph=True, nested=True)

states = ['standing', 'walking', {'name': 'caffeinated', 'children':['dithering', 'running']}]
transitions = [
  ['walk', 'standing', 'walking'],
  ['go', 'standing', 'walking'],
  ['stop', 'walking', 'standing'],
  {'trigger': 'drink', 'source': '*', 'dest': 'caffeinated_dithering',
   'conditions':'is_hot', 'unless': 'is_too_hot'},
  ['walk', 'caffeinated_dithering', 'caffeinated_running'],
  ['relax', 'caffeinated', 'standing'],
  ['sip', 'standing', 'caffeinated']
]

model = Matter()
machine = GraphMachine(model=model,
                       states=states,
                       transitions=transitions,
                       auto_transitions=False,
                       initial='standing',
                       title="Mood Matrix",
                       show_conditions=True)
model.go()
dot = Digraph(comment='FSM')

for label, event in machine.events.items():
    for event_transitions in event.transitions.values():
        for transition in event_transitions:
            dot.edge(transition.source, transition.dest, label)

machine.get_graph().draw('apsm_diagram_05.png', prog='dot')
print(dot)