from typing import Tuple


class PDDLKnowledgeUtils(object):
    @staticmethod
    def get_ordered_param_list(params: list, param_order: dict, obj_types: dict) -> Tuple[list, dict]:
        param_list = []
        param_count = 0
        updated_obj_types = dict(obj_types)
        while param_count < len(params):
            for param in params:
                param_name = param_order[param_count][0]
                param_type = param_order[param_count][1]
                if param.name == param_name:
                    param_list.append(param.value)
                    param_count += 1
                    if param_type not in updated_obj_types:
                        updated_obj_types[param_type] = []

                    if param.value not in updated_obj_types[param_type]:
                        updated_obj_types[param_type].append(param.value)
                    break
        return param_list, updated_obj_types


class PDDLPredicateLibrary(object):
    @staticmethod
    def get_assertion_param_list(predicate_name: str, predicate_params: list, obj_types: dict) -> Tuple[list, dict]:
        ordered_param_list, updated_obj_types = getattr(PDDLPredicateLibrary, predicate_name)(predicate_params, obj_types)
        return ordered_param_list, updated_obj_types

    @staticmethod
    def robot_at(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('bot', 'robot'), 1: ('loc', 'location')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def robot_in(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('bot', 'robot'), 1: ('elevator', 'elevator')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def load_at(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('load', 'load'), 1: ('loc', 'location')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def load_in(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('load', 'load'), 1: ('elevator', 'elevator')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def elevator_at(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('elevator', 'elevator'), 1: ('loc', 'location')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def empty_gripper(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('bot', 'robot')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def holding(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: 'bot', 1: 'load'}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def requested(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('bot', 'robot'), 1: ('elevator', 'elevator')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def arrived(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('elevator', 'elevator')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)


class PDDLNumericFluentLibrary(object):
    @staticmethod
    def get_assertion_param_list(fluent_name: str, fluent_params: list, obj_types: dict) -> Tuple[list, dict]:
        ordered_param_list, obj_types = getattr(PDDLNumericFluentLibrary, fluent_name)(fluent_params, obj_types)
        return ordered_param_list, obj_types

    @staticmethod
    def robot_floor(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('bot', 'robot')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def location_floor(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('loc', 'location')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def load_floor(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('load', 'load')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def elevator_floor(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('elevator', 'elevator')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)

    @staticmethod
    def destination_floor(params: list, obj_types: dict) -> Tuple[list, dict]:
        param_order = {0: ('elevator', 'elevator')}
        return PDDLKnowledgeUtils.get_ordered_param_list(params, param_order, obj_types)
