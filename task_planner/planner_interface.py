from os.path import join
import uuid
import subprocess
from termcolor import colored
from task_planner.knowledge_base_interface import KnowledgeBaseInterface
from task_planner.action_models import ActionModelLibrary
from ropod.structs.task import TaskRequest
from ropod.structs.action import Action

class TaskPlannerInterface(object):
    def __init__(self, kb_database_name, planner_cmd, plan_file_path, debug=False):
        self.kb_interface = KnowledgeBaseInterface(kb_database_name)
        self.planner_cmd = planner_cmd
        self.plan_file_path = plan_file_path
        self.debug = debug
        self.__planner_cmd_elements = self.planner_cmd.split(' ')

    def plan(self, task_request: TaskRequest,
             robot: str, plan_goals: list=None):

        task_goals = [('cart_at', [('cart', task_request.cart_id),
                                   ('loc', task_request.delivery_pose.id)]),
                      ('empty_gripper', [('bot', robot)])]

        # TODO: check if the specified goals are contradicting the overall task goals
        if plan_goals is not None:
            task_goals.extend(plan_goals)

        kb_assertions = self.kb_interface.get_all_predicate_assertions()

        # TODO: generate a problem file from the knowledge base
        # and the list of goals before calling the planner

        plan_file_name = 'plan_{0}.txt'.format(str(uuid.uuid4()))
        plan_file_abs_path = join(self.plan_file_path, plan_file_name)
        print(colored('[task_planner] Planning task...', 'green'))
        with open(plan_file_abs_path, 'w') as plan_file:
            subprocess.run(self.__planner_cmd_elements, stdout=plan_file)
            print(colored('[task_planner] Planning finished', 'green'))

        plan_found, plan = self.__parse_plan(plan_file_abs_path, task_request.cart_type, robot)
        return plan_found, plan

    def process_action_str(self, action_line: str) -> Action:
        action_data = action_line[action_line.find(':')+2:].split()
        action_name = action_data[0]
        action_params = action_data[1:]
        action = ActionModelLibrary.get_action_model(action_name, action_params)
        print(action.to_dict())
        return action

    def __parse_plan(self, plan_file_abs_path: str, task: str, robot: str) -> list:
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
