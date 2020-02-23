from os import listdir
from os.path import join
from typing import Tuple, Sequence
import uuid
import subprocess
import numpy as np
import logging

from ropod.structs.task import TaskRequest
from ropod.structs.action import Action
from ropod.structs.area import Area

from task_planner.planner_interface import TaskPlannerInterface
from task_planner.knowledge_base_interface import Predicate
from task_planner.action_models import ActionModelLibrary
from task_planner.knowledge_models import PDDLPredicateLibrary, PDDLNumericFluentLibrary


class LAMAInterface(TaskPlannerInterface):
    _plan_file_name = 'plan.txt'

    def __init__(self, kb_database_name, domain_file,
                 planner_cmd, plan_file_path, debug=False):
        super(LAMAInterface, self).__init__(kb_database_name, domain_file,
                                            planner_cmd, plan_file_path,
                                            debug)
        self.logger = logging.getLogger('task.planner')

    def plan(self, task_request: TaskRequest, robot: str, task_goals: list=None):
        '''
        task_goals can be a list of any of the following variation of Predicate object
            - Object itself
            - tuple
            - dict
        '''
        # TODO: check if there are already goals in the knowledge base and,
        # if yes, add them to the task_goals list

        predicate_task_goals = []
        for task_goal in task_goals:
            if isinstance(task_goal, Predicate):
                predicate_task_goals.append(task_goal)
            elif isinstance(task_goal, tuple):
                predicate_task_goals.append(Predicate.from_tuple(task_goal))
            elif isinstance(task_goal, dict):
                predicate_task_goals.append(Predicate.from_dict(task_goal))
            else:
                raise Exception('Invalid type to task_goal encountered')

        kb_predicate_assertions = self.kb_interface.get_predicate_assertions()
        kb_fluent_assertions = self.kb_interface.get_fluent_assertions()

        self.logger.info('Generating problem file')
        problem_file = self.generate_problem_file(kb_predicate_assertions,
                                                  kb_fluent_assertions,
                                                  predicate_task_goals)

        planner_cmd = self.planner_cmd.replace('PROBLEM', problem_file)
        planner_cmd = planner_cmd.replace('PLAN-FILE', self._plan_file_name)
        planner_cmd_elements = planner_cmd.split()

        self.logger.info('Planning task...')
        subprocess.run(planner_cmd_elements)
        self.logger.info('Planning finished')

        plan_found, plan = self.parse_plan(task_request.load_type, robot)
        return plan_found, plan

    def generate_problem_file(self, predicate_assertions: list,
                              fluent_assertions: list,
                              task_goals: Sequence[Predicate]) -> str:
        obj_types = {}
        init_state_str = ''

        # we generate strings from the predicate assertions of the form
        # (predicate_name param_1 param_2 ... param_n)
        for assertion in predicate_assertions:
            ordered_param_list, obj_types = PDDLPredicateLibrary.get_assertion_param_list(assertion.name,
                                                                                          assertion.params,
                                                                                          obj_types)
            assertion_str = '        ({0} {1})\n'.format(assertion.name, ' '.join(ordered_param_list))
            init_state_str += assertion_str


        # for numeric fluents, we generate strings of the form
        # (= (fluent_name param_1 param_2 ... param_n) fluent_value); otherwise,
        # we generate strings just like for predicate assertions
        for assertion in fluent_assertions:
            if hasattr(PDDLPredicateLibrary, assertion.name):
                ordered_param_list, obj_types = PDDLPredicateLibrary.get_assertion_param_list(assertion.name,
                                                                                              assertion.params,
                                                                                              obj_types)
                assertion_str = '        ({0} {1} {2})\n'.format(assertion.name,
                                                                 ' '.join(ordered_param_list),
                                                                 assertion.value)
            else:
                ordered_param_list, obj_types = PDDLNumericFluentLibrary.get_assertion_param_list(assertion.name,
                                                                                                  assertion.params,
                                                                                                  obj_types)
                assertion_str = '        (= ({0} {1}) {2})\n'.format(assertion.name,
                                                                     ' '.join(ordered_param_list),
                                                                     assertion.value)
            init_state_str += assertion_str

        # we combine the assertion strings into an initial state string of the form
        # (:init
        #     assertions
        # )
        init_state_str = '    (:init\n{0}\n    )\n\n'.format(init_state_str)

        # we generate a string with the object types of the form
        # (:objects
        #     obj_11 obj_12 - type_1
        #     ...
        #     obj_n1 - type_n
        # )
        obj_type_str = ''
        for obj_type in obj_types:
            obj_type_str += '        {0} - {1}\n'.format(' '.join(obj_types[obj_type]), obj_type)
        obj_type_str = '    (:objects\n{0}    )\n\n'.format(obj_type_str)

        # we generate a string with the planning goals of the form
        # (:goals
        #     (and
        #         (predicate_1_name param_1 param_2 ... param_n)
        #         ...
        #         (predicate_n_name param_1 param_2 ... param_n)
        #     )
        # )
        goal_str = ''
        for task_goal in task_goals:
            goal_predicate, goal_params = task_goal.name, task_goal.params
            goal_str += '            ({0} {1})\n'.format(goal_predicate,
                                                         ' '.join([param.value for param in goal_params]))
        goal_str = '    (:goal\n        (and\n{0}        )\n    )\n'.format(goal_str)

        # we finally write the problem file, which will be in the format
        # (define (problem problem-name)
        #     (:domain domain-name)
        #     (:objects
        #         ...
        #     )
        #     (:objects
        #         ...
        #     )
        #     (:goals
        #         ...
        #     )
        # )
        problem_file_name = 'problem_{0}.pddl'.format(str(uuid.uuid4()))
        problem_file_abs_path = join(self.plan_file_path, problem_file_name)
        self.logger.info('Generating planning problem...')
        with open(problem_file_abs_path, 'w') as problem_file:
            header = '(define (problem ropod)\n'
            header += '    (:domain {0})\n'.format(self.domain_name)
            problem_file.write(header)
            problem_file.write(obj_type_str)
            problem_file.write(init_state_str)
            problem_file.write(goal_str)
            problem_file.write(')\n')
        return problem_file_abs_path

    def parse_plan(self, task: str, robot: str) -> Tuple[bool, list]:
        plan_files = [f for f in listdir(self.plan_file_path)
                      if f.find(self._plan_file_name) != -1]
        if not plan_files:
            self.logger.error('Plan for task %s and robot %s not found', task, robot)
            return False, []

        plans = []
        action_strings_per_plan = []
        for plan_file_name in plan_files:
            plan = []
            plan_action_strings = []
            with open(join(self.plan_file_path, plan_file_name), 'r') as plan_file:
                while True:
                    line = plan_file.readline()
                    if line.find(';') != -1:
                        break
                    else:
                        action_line = line.strip()[1:-1]
                        action = self.process_action_str(action_line)
                        for i in range(len(action.areas)):
                            floor_fluent = ('location_floor', [('loc', action.areas[i].name)])
                            floor = self.kb_interface.get_fluent_value(floor_fluent)

                            # "floor" is either a string of the form "floorX"
                            # or the "unknown" string; we thus throw away the word
                            # "floor" to get the actual floor number - or catch an
                            # exception and set a default unreasonable floor
                            # if the floor is not known
                            try:
                                floor_number = int(floor[5:])
                            except ValueError:
                                floor_number = -100
                            action.areas[i].floor_number = floor_number
                        plan.append(action)
                        plan_action_strings.append(action_line)
                        self.logger.debug(action_line)
                plans.append(plan)
                action_strings_per_plan.append(plan_action_strings)

        plan_lengths = [len(plan) for plan in plans]
        shortest_plan_idx = np.argmin(plan_lengths)

        self.logger.info('Plan for task %s and robot %s found', task, robot)
        self.logger.debug('Action sequence:')
        self.logger.debug('-------------------------------')
        for action_string in action_strings_per_plan[shortest_plan_idx]:
            self.logger.debug(action_string)
        self.logger.debug('-------------------------------')
        return True, plans[shortest_plan_idx]

    def process_action_str(self, action_line: str) -> Action:
        action_data = action_line[action_line.find(':')+2:].split()
        action_name = action_data[0]
        action_params = action_data[1:]
        action = ActionModelLibrary.get_action_model(action_name, action_params)
        return action
