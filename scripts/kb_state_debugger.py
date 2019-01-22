#!/usr/bin/env python3
import os
import time
from termcolor import colored
from task_planner.knowledge_base_interface import KnowledgeBaseInterface

def get_predicate_values(instance):
    values = []
    values = [v.value for v in instance.params]
    return values

if __name__ == '__main__':
    kb_interface = KnowledgeBaseInterface('ropod_kb')
    try:
        while True:
            predicates = kb_interface.get_predicate_names()
            for predicate in predicates:
                predicate_instances = kb_interface.get_all_attributes(predicate)
                if predicate_instances:
                    print(colored(predicate, 'green'))
                    print('--------------------')
                    for instance in predicate_instances:
                        predicate_values = get_predicate_values(instance)
                        instance_str = ''
                        for v in predicate_values[0:-1]:
                            instance_str += '{0}, '.format(v)
                        instance_str += '{0}'.format(predicate_values[-1])
                        print(colored(predicate, 'green'),
                              colored('(', 'green'),
                              colored(instance_str, 'red'),
                              colored(')', 'green'))
                    print()
            time.sleep(1.)
            os.system('clear')
    except (KeyboardInterrupt, SystemExit):
        print('Ending knowledge base visualiser')
