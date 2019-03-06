#!/usr/bin/env python3
import os
import time
from task_planner.knowledge_base_interface import KnowledgeBaseInterface
import logging


def get_predicate_values(instance):
    values = [v.value for v in instance.params]
    return values


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)

    kb_interface = KnowledgeBaseInterface('ropod_kb')
    try:
        while True:
            predicates = kb_interface.get_predicate_names()
            for predicate in predicates:
                predicate_instances = kb_interface.get_predicate_assertions(predicate)
                if predicate_instances:
                    logging.info(predicate)
                    logging.info('--------------------')
                    for instance in predicate_instances:
                        predicate_values = get_predicate_values(instance)
                        instance_str = ''
                        for v in predicate_values[0:-1]:
                            instance_str += '{0}, '.format(v)
                        instance_str += '{0}'.format(predicate_values[-1])
                        logging.debug('%s: ( %s )', predicate, instance_str)
            time.sleep(1.)
            os.system('clear')
    except (KeyboardInterrupt, SystemExit):
        logging.info('Ending knowledge base visualiser')
