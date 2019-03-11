from abc import abstractmethod
from typing import Tuple
from ropod.structs.task import TaskRequest
from ropod.structs.action import Action
from task_planner.knowledge_base_interface import KnowledgeBaseInterface


class TaskPlannerInterface(object):
    def __init__(self, kb_database_name, domain_file, planner_cmd, plan_file_path, debug=False):
        self.kb_interface = KnowledgeBaseInterface(kb_database_name)
        self.domain_file = domain_file
        self.domain_name = self.__get_domain_name(self.domain_file)
        self.planner_cmd = planner_cmd.replace('DOMAIN', self.domain_file)
        self.plan_file_path = plan_file_path
        self.debug = debug

    @abstractmethod
    def plan(self, task_request: TaskRequest,
             robot: str, plan_goals: list=None):
        pass

    @abstractmethod
    def generate_problem_file(self, predicate_assertions: list,
                              fluent_assertions: list, task_goals: list) -> str:
        pass

    @abstractmethod
    def process_action_str(self, action_line: str) -> Action:
        pass

    @abstractmethod
    def parse_plan(self, plan_file_abs_path: str, task: str,
                   robot: str) -> Tuple[bool, list]:
        pass

    def __get_domain_name(self, domain_file_name: str) -> str:
        '''Extracts the name of the planning domain from the given file
        by looking for the first line that contains the words "define" and
        "domain" and then parsing the domain line from it.

        Keyword arguments:
        @param domain_file_name: str -- absolute path of a PDDL domain file

        '''
        line = ''
        with open(domain_file_name, 'r') as domain_file:
            line = ''
            domain_defn_found = False
            while not domain_defn_found:
                line = domain_file.readline().lower()
                domain_defn_found = line.find('define') != -1 and line.find('domain') != -1
        domain_idx = line.lower().find('domain') + 1
        line = line[domain_idx+6:]
        idx = 0
        while line[idx] == ' ':
            idx += 1

        domain_name_start_idx = idx
        while line[idx] != ' ' and line[idx] != ')':
            idx += 1
        domain_name_end_idx = idx - 1
        domain_name = line[domain_name_start_idx:domain_name_end_idx+1]
        return domain_name
