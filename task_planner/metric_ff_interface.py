from os.path import join
import uuid
import subprocess
from typing import Tuple
from termcolor import colored

from ropod.structs.task import TaskRequest
from ropod.structs.action import Action

from task_planner.planner_interface import TaskPlannerInterface
from task_planner.action_models import ActionModelLibrary
from task_planner.knowledge_models import PDDLPredicateLibrary, PDDLFluentLibrary

class MetricFFInterface(TaskPlannerInterface):
    def __init__(self, kb_database_name, domain_file,
                 planner_cmd, plan_file_path, debug=False):
        super(MetricFFInterface, self).__init__(kb_database_name, domain_file,
                                                planner_cmd, plan_file_path,
                                                debug)

    def plan(self, task_request: TaskRequest, robot: str, task_goals: list=None):
        # TODO: check if there are already goals in the knowledge base and,
        # if yes, add them to the task_goals list

        kb_predicate_assertions = self.kb_interface.get_predicate_assertions()
        kb_fluent_assertions = self.kb_interface.get_fluent_assertions()

        print(colored('[task_planner] Generating problem file', 'green'))
        problem_file = self.generate_problem_file(kb_predicate_assertions,
                                                  kb_fluent_assertions,
                                                  task_goals)

        planner_cmd = self.planner_cmd.replace('PROBLEM', problem_file)
        planner_cmd_elements = planner_cmd.split()

        plan_file_name = 'plan_{0}.txt'.format(str(uuid.uuid4()))
        plan_file_abs_path = join(self.plan_file_path, plan_file_name)
        print(colored('[task_planner] Planning task...', 'green'))
        with open(plan_file_abs_path, 'w') as plan_file:
            subprocess.run(planner_cmd_elements, stdout=plan_file)
            print(colored('[task_planner] Planning finished', 'green'))

        plan_found, plan = self.parse_plan(plan_file_abs_path, task_request.cart_type, robot)
        return plan_found, plan

    def generate_problem_file(self, predicate_assertions: list,
                              fluent_assertions: list,
                              task_goals: list) -> str:
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

        # we generate strings from the fluent assertions of the form
        # (= (fluent_name param_1 param_2 ... param_n) fluent_value)
        for assertion in fluent_assertions:
            ordered_param_list, obj_types = PDDLFluentLibrary.get_assertion_param_list(assertion.name,
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
        for goal_predicate, goal_params in task_goals:
            goal_str += '            ({0} {1})\n'.format(goal_predicate,
                                                         ' '.join([param[1] for param in goal_params]))
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
        problem_file_name = 'problem_{0}.txt'.format(str(uuid.uuid4()))
        problem_file_abs_path = join(self.plan_file_path, problem_file_name)
        print(colored('[task_planner] Generating planning problem...', 'green'))
        with open(problem_file_abs_path, 'w') as problem_file:
            header = '(define (problem ropod)\n'
            header += '    (:domain {0})\n'.format(self.domain_name)
            problem_file.write(header)
            problem_file.write(obj_type_str)
            problem_file.write(init_state_str)
            problem_file.write(goal_str)
            problem_file.write(')\n')
        return problem_file_abs_path

    def parse_plan(self, plan_file_abs_path: str, task: str, robot: str) -> Tuple[bool, list]:
        plan_found = False
        processing_plan = False
        plan = []
        with open(plan_file_abs_path, 'r') as plan_file:
            while True:
                line = plan_file.readline()
                if not line:
                    break

                if processing_plan:
                    if line == '\n':
                        processing_plan = False
                        if self.debug:
                            print(colored('-------------------------------', 'green'))
                    else:
                        action = self.process_action_str(line.strip())
                        plan.append(action)
                        if self.debug:
                            print(colored(line.strip(), 'yellow'))

                if 'found legal plan' in line.lower():
                    plan_found = True
                    print(colored('[task_planner] Plan for task {0} and robot {1} found'.format(task, robot), 'green'))
                    if self.debug:
                        print(colored('[task_planner] Action sequence:', 'green'))
                        print(colored('-------------------------------', 'green'))

                if 'step' in line.lower():
                    line = line[4:]
                    processing_plan = True
                    action = self.process_action_str(line.strip())
                    plan.append(action)
                    if self.debug:
                        print(colored(line.strip(), 'yellow'))

        if not plan_found:
            print(colored('[task_planner] Plan for task {0} and robot {1} not found'.format(task, robot), 'red'))
        return plan_found, plan

    def process_action_str(self, action_line: str) -> Action:
        action_data = action_line[action_line.find(':')+2:].split()
        action_name = action_data[0]
        action_params = action_data[1:]
        action = ActionModelLibrary.get_action_model(action_name, action_params)
        return action
