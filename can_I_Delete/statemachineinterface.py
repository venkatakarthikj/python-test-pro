import abc


class abstractstatic(staticmethod):
    """
    https://stackoverflow.com/a/4474495/1257603
    """
    __slots__ = ()

    def __init__(self, function):
        super(abstractstatic, self).__init__(function)
        function.__isabstractmethod__ = True

    __isabstractmethod__ = True


class StateMachineInterface(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __initialize__(self,  **kwargs):
        """"
        Create a list of states to pass to the Machine initializer.
        We can mix types; in this case, we pass one State, one string, and one dict.
        states = [
            State(name='state_name'),
            'state_name',
            { 'name': 'state_name'}
        ]
        machine = Machine(states='states', transitions='transitions', initial='initial')
        """
        raise NotImplementedError('users must define __initialize_ to use this base class')

    def __repr__(self):
        raise RuntimeError("__repr__ Must be implemented")

    @abc.abstractmethod
    def add_model(self, model_instance, state_initial):
        """
        machine.add_model(model_instance, initial='state_initial')
        """
        pass

    # Injected model instance
    @abc.abstractproperty
    def model_instance(self):
        return

    @model_instance.setter
    def model_instance(self, new_model_instance):
        return

    # Injected state machine instance
    @abc.abstractproperty
    def state_machine(self):
        return

    @state_machine.setter
    def state_machine(self, new_state_machine):
        return

    @abc.abstractmethod
    def add_state(self, state_machine, state_value):
        """
        machine.add_states([state_value])
        """
        pass

    @abc.abstractmethod
    def current_state(self, state_machine):
        """
        machine.get_state(lump.state).name
        """
        pass

    @abc.abstractmethod
    def get_state(self, state_machine, state_name):
        """
        get state_name from states list
        """
        raise RuntimeError("get_states Must be implemented")

    @abc.abstractmethod
    def set_state(self, state_machine, state_name):
        """
        machine.set_state(state_name)
        """
        pass

    @abstractstatic
    def get_states_list(self):
        """
        Returns the states this object may be in
        """
        raise RuntimeError("get_states_list Must be implemented")

    @abc.abstractmethod
    def get_transition(self, state_machine, transition_name):
        """
        Returns transition_name from transitions list
        """
        pass

    @abc.abstractmethod
    def add_transition(self, state_machine, transition_name, source, destination):
        """
        add transition_name to state
        """
        pass

    @abc.abstractmethod
    def run_transition(self, state_machine, transition_name):
        """
        state_machine.transition_name()
        """
        pass

    @abstractstatic
    def get_transitions_list(self, state_machine):
        """
        describes the transitions allowed by this statemachine
        """
        raise RuntimeError("get_transitions_list Must be implemented")

    @abc.abstractmethod
    def on_enter(self, state_machine, state_name):
        """
        state_machine.on_enter_state_name()
        """
        pass

    @abc.abstractmethod
    def on_exit(self, state_machine, state_name):
        """
        state_machine.on_exit_state_name()
        """
        pass
