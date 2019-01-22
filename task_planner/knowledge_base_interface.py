import pymongo as pm
from termcolor import colored

class PredicateParams(object):
    def __init__(self):
        self.name = ''
        self.value = ''

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.value == other.value

    def __ne__(self, other) -> bool:
        return self.name != other.name or self.value != other.value

    def to_dict(self) -> dict:
        dict_params = {}
        dict_params['name'] = self.name
        dict_params['value'] = self.value
        return dict_params

    @staticmethod
    def from_tuple(tuple_params):
        params = PredicateParams()
        params.name, params.value = tuple_params
        return params

    @staticmethod
    def from_dict(dict_params: dict):
        params = PredicateParams()
        params.name = dict_params['name']
        params.value = dict_params['value']
        return params

class Predicate(object):
    def __init__(self):
        self.name = ''
        self.params = []

    def __eq__(self, other) -> bool:
        equal = False
        if self.name == other.name:
            equal = True
            for param in self.params:
                if param not in other.params:
                    equal = False
                    break
        return equal

    def to_dict(self) -> dict:
        dict_predicate = {}
        dict_predicate['name'] = self.name
        dict_predicate['params'] = []
        for param_data in self.params:
            dict_params = param_data.to_dict()
            dict_predicate['params'].append(dict_params)
        return dict_predicate

    @staticmethod
    def from_tuple(tuple_predicate):
        predicate = Predicate()
        predicate.name, tuple_data = tuple_predicate
        for tuple_params in tuple_data:
            params = PredicateParams.from_tuple(tuple_params)
            predicate.params.append(params)
        return predicate

    @staticmethod
    def from_dict(dict_predicate: dict):
        predicate = Predicate()
        predicate.name = dict_predicate['name']
        dict_data = dict_predicate['params']
        for dict_params in dict_data:
            params = PredicateParams.from_dict(dict_params)
            predicate.params.append(params)
        return predicate

class KnowledgeBaseInterface(object):
    def __init__(self, kb_database_name):
        self.kb = {}
        self.goals = {}
        self.kb_database_name = kb_database_name
        self.kb_collection_name = 'knowledge_base'
        self.goal_collection_name = 'goals'

    def get_predicate_names(self) -> list:
        collection = self.__get_kb_collection(self.kb_collection_name)
        predicate_cursor = collection.find()
        names = list({p['name'] for p in predicate_cursor})
        return names

    def get_all_predicate_assertions(self) -> list:
        collection = self.__get_kb_collection(self.kb_collection_name)
        assertion_cursor = collection.find()
        instances = [Predicate.from_dict(p) for p in assertion_cursor]
        return instances

    def get_all_attributes(self, predicate_name) -> list:
        collection = self.__get_kb_collection(self.kb_collection_name)
        pred_instance_count = collection.count_documents({'name': predicate_name})
        if pred_instance_count == 0:
            return []

        pred_instance_cursor = collection.find({'name': predicate_name})
        instances = [Predicate.from_dict(p) for p in pred_instance_cursor]
        return instances

    def update_kb(self, facts_to_add: list, facts_to_remove: list) -> bool:
        insert_successful = True
        removal_successful = True
        if facts_to_add:
            insert_successful = self.insert_facts(facts_to_add)

        if facts_to_remove:
            removal_successful = self.remove_facts(facts_to_remove)

        return insert_successful and removal_successful

    def insert_facts(self, fact_list: list) -> bool:
        try:
            self.__insert_predicates(fact_list, self.kb_collection_name)
            return True
        except Exception as exc:
            print(colored('[insert_facts] Facts could not be inserted: {0}'.format(exc), 'red'))
            return False

    def remove_facts(self, fact_list: list) -> bool:
        try:
            self.__remove_predicates(fact_list, self.kb_collection_name)
            return True
        except Exception as exc:
            print(colored('[remove_facts] Facts could not be removed: {0}'.format(exc), 'red'))
            return False

    def insert_goals(self, goal_list: list) -> bool:
        try:
            self.__insert_predicates(goal_list, self.goal_collection_name)
            return True
        except Exception as exc:
            print(colored('[insert_goals] Goals could not be inserted: {0}'.format(exc), 'red'))
            return False

    def remove_goals(self, goal_list: list) -> bool:
        try:
            self.__remove_predicates(goal_list, self.goal_collection_name)
            return True
        except Exception as exc:
            print(colored('[remove_goals] Goals could not be removed: {0}'.format(exc), 'red'))
            return False

    def __get_kb_collection(self, collection_name) -> pm.collection.Collection:
        client = pm.MongoClient()
        db = client[self.kb_database_name]
        collection = db[collection_name]
        return collection

    def __predicate_exists(self, predicate: dict) -> bool:
        collection = self.__get_kb_collection(self.kb_collection_name)
        doc = collection.find_one(predicate)
        return doc is not None

    def __insert_predicates(self, predicate_list: list, collection_name: str) -> bool:
        for predicate_tuple in predicate_list:
            predicate = Predicate.from_tuple(predicate_tuple)
            predicate_dict = predicate.to_dict()
            if not self.__predicate_exists(predicate_dict):
                collection = self.__get_kb_collection(collection_name)
                collection.insert_one(predicate_dict)
            else:
                print(colored('Predicate {0} already exists'.format(predicate.name), 'yellow'))

    def __remove_predicates(self, predicate_list: list, collection_name: str) -> bool:
        for predicate_tuple in predicate_list:
            predicate = Predicate.from_tuple(predicate_tuple)
            predicate_dict = predicate.to_dict()
            if self.__predicate_exists(predicate_dict):
                collection = self.__get_kb_collection(collection_name)
                collection.remove(predicate_dict)
            else:
                print(colored('Predicate {0} does not exist'.format(predicate.name), 'yellow'))
