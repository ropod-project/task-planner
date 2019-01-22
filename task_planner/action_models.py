import uuid
from ropod.structs.action import Action
from ropod.structs.area import Area

class ActionModelLibrary(object):
    @staticmethod
    def get_action_model(action_name: str, action_params: list) -> Action:
        action = Action()
        action.id = str(uuid.uuid4())
        action.type = action_name
        action = getattr(ActionModelLibrary, action_name)(action, action_params)
        return action

    @staticmethod
    def GOTO(action: Action, params: list) -> Action:
        destination_area = Area()
        destination_area.name = params[2]
        action.areas.append(destination_area)
        return action

    @staticmethod
    def DOCK(action: Action, params: list) -> Action:
        pickup_area = Area()
        pickup_area.name = params[2]
        action.areas.append(pickup_area)
        return action

    @staticmethod
    def UNDOCK(action: Action, params: list) -> Action:
        return action

    @staticmethod
    def REQUEST_ELEVATOR(action: Action, params: list) -> Action:
        return action

    @staticmethod
    def WAIT_FOR_ELEVATOR(action: Action, params: list) -> Action:
        return action

    @staticmethod
    def ENTER_ELEVATOR(action: Action, params: list) -> Action:
        return action

    @staticmethod
    def RIDE_ELEVATOR(action: Action, params: list) -> Action:
        return action

    @staticmethod
    def EXIT_ELEVATOR(action: Action, params: list) -> Action:
        return action
