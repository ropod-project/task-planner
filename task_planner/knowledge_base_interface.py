from typing import Tuple
import pymongo as pm
from termcolor import colored

class PredicateParams(object):
    '''An object representing a predicate parameter (variable name and ground value).

    @author Alex Mitrevski
    @contact aleksandar.mitrevski@h-brs.de

    '''
    def __init__(self):
        self.name = ''
        self.value = ''

    def __eq__(self, other) -> bool:
        '''Returns True if both the names and the values are the same.
        '''
        return self.name == other.name and self.value == other.value

    def __ne__(self, other) -> bool:
        '''Returns True if either the name or the value differ.
        '''
        return self.name != other.name or self.value != other.value

    def to_dict(self) -> dict:
        '''Converts the object to a dictionary with two keys: "name" and "value".
        '''
        dict_params = {}
        dict_params['name'] = self.name
        dict_params['value'] = self.value
        return dict_params

    @staticmethod
    def from_tuple(tuple_params: Tuple[str, str]):
        '''Returns a PredicateParams object created from the input tuple.

        Keyword arguments:
        @param tuple_params -- a tuple with two entries - "name" and "value"

        '''
        params = PredicateParams()
        params.name, params.value = tuple_params
        return params

    @staticmethod
    def from_dict(dict_params: dict):
        '''Returns a PredicateParams object created from the input dictionary.

        Keyword arguments:
        @param dict_params -- a dictionary with two keys - "name" and "value"

        '''
        params = PredicateParams()
        params.name = dict_params['name']
        params.value = dict_params['value']
        return params

class Predicate(object):
    '''An object representing a predicate (predicate name and list of ground values).

    @author Alex Mitrevski
    @contact aleksandar.mitrevski@h-brs.de

    '''
    def __init__(self):
        self.name = ''
        self.params = []

    def __eq__(self, other) -> bool:
        '''Returns True if both the names and all parameters are the same.
        '''
        equal = False
        if self.name == other.name:
            equal = True
            for param in self.params:
                if param not in other.params:
                    equal = False
                    break
        return equal

    def to_dict(self) -> dict:
        '''Converts the object to a dictionary with two keys - "name" and "params".
        The value of "params" is a list of PredicateParams dictionaries.
        '''
        dict_predicate = {}
        dict_predicate['name'] = self.name
        dict_predicate['params'] = []
        for param_data in self.params:
            dict_params = param_data.to_dict()
            dict_predicate['params'].append(dict_params)
        return dict_predicate

    @staticmethod
    def from_tuple(tuple_predicate):
        '''Returns a Predicate object created from the input tuple.

        Keyword arguments:
        @param tuple_predicate -- a tuple with two entries, the first representing
                                  the name of the predicate and the second a list of
                                  ("name", "value") pairs for the predicate parameters

        '''
        predicate = Predicate()
        predicate.name, tuple_data = tuple_predicate
        for tuple_params in tuple_data:
            params = PredicateParams.from_tuple(tuple_params)
            predicate.params.append(params)
        return predicate

    @staticmethod
    def from_dict(dict_predicate: dict):
        '''Returns a Predicate object created from the input dictionary.

        Keyword arguments:
        @param dict_predicate -- a dictionary with two keys - "name" and "params",
                                 where "params" is a list of PredicateParams
                                 dictionaries

        '''
        predicate = Predicate()
        predicate.name = dict_predicate['name']
        dict_data = dict_predicate['params']
        for dict_params in dict_data:
            params = PredicateParams.from_dict(dict_params)
            predicate.params.append(params)
        return predicate

class KnowledgeBaseInterface(object):
    '''Defines an interface for interacting with a robot knowledge base.

    Constructor arguments:
    @param __kb_database_name -- name of a database in which the knowledge base will be stored

    @author Alex Mitrevski
    @contact aleksandar.mitrevski@h-brs.de

    '''
    def __init__(self, __kb_database_name):
        self.__kb_database_name = __kb_database_name
        self.__kb_collection_name = 'knowledge_base'
        self.__goal_collection_name = 'goals'

    def get_predicate_names(self) -> list:
        '''Returns a list of all stored predicate names in the knowledge base.
        '''
        collection = self.__get_kb_collection(self.__kb_collection_name)
        predicate_cursor = collection.find()
        names = list({p['name'] for p in predicate_cursor})
        return names

    def get_all_assertions(self) -> list:
        '''Returns a list of Predicate objects representing all
        assertions in the knowledge base.
        '''
        collection = self.__get_kb_collection(self.__kb_collection_name)
        assertion_cursor = collection.find()
        instances = [Predicate.from_dict(p) for p in assertion_cursor]
        return instances

    def get_all_predicate_assertions(self, predicate_name: str) -> list:
        '''Returns a list of Predicate objects representing all assertions
        of the given predicate in the knowledge base.

        Keyword arguments:
        @param predicate_name: str -- a name of a predicate in the knowledge base

        '''
        collection = self.__get_kb_collection(self.__kb_collection_name)
        pred_instance_count = collection.count_documents({'name': predicate_name})
        if pred_instance_count == 0:
            return []

        pred_instance_cursor = collection.find({'name': predicate_name})
        instances = [Predicate.from_dict(p) for p in pred_instance_cursor]
        return instances

    def update_kb(self, facts_to_add: list, facts_to_remove: list) -> bool:
        '''Inserts a list of facts into the knowledge base and removes
        a list of facts from it.

        Keyword arguments:
        @param facts_to_add: list -- facts to add to the knowledge base. The entries are
                                     tuples with two entries, the first representing
                                     the name of the predicate and the second a list of
                                     ("name", "value") pairs for the predicate parameters
        @param facts_to_remove: list -- facts to remove from the knowledge base. The entries are
                                        tuples with two entries, the first representing
                                        the name of the predicate and the second a list of
                                        ("name", "value") pairs for the predicate parameters

        '''
        insert_successful = True
        removal_successful = True
        if facts_to_add:
            insert_successful = self.insert_facts(facts_to_add)

        if facts_to_remove:
            removal_successful = self.remove_facts(facts_to_remove)

        return insert_successful and removal_successful

    def insert_facts(self, fact_list: list) -> bool:
        '''Inserts a list of facts into the knowledge base.

        Keyword arguments:
        @param facts_to_add: list -- facts to add to the knowledge base. The entries are
                                     tuples with two entries, the first representing
                                     the name of the predicate and the second a list of
                                     ("name", "value") pairs for the predicate parameters

        '''
        try:
            self.__insert_predicates(fact_list, self.__kb_collection_name)
            return True
        except Exception as exc:
            print(colored('[insert_facts] Facts could not be inserted: {0}'.format(exc), 'red'))
            return False

    def remove_facts(self, fact_list: list) -> bool:
        '''Removes a list of facts from the knowledge base.

        Keyword arguments:
        @param facts_to_remove: list -- facts to remove from the knowledge base. The entries are
                                        tuples with two entries, the first representing
                                        the name of the predicate and the second a list of
                                        ("name", "value") pairs for the predicate parameters

        '''
        try:
            self.__remove_predicates(fact_list, self.__kb_collection_name)
            return True
        except Exception as exc:
            print(colored('[remove_facts] Facts could not be removed: {0}'.format(exc), 'red'))
            return False

    def insert_goals(self, goal_list: list) -> bool:
        '''Inserts a list of planning goals into the knowledge base.

        Keyword arguments:
        @param goals_to_add: list -- goals to add to the knowledge base. The entries are
                                     tuples with two entries, the first representing
                                     the name of the predicate and the second a list of
                                     ("name", "value") pairs for the predicate parameters

        '''
        try:
            self.__insert_predicates(goal_list, self.__goal_collection_name)
            return True
        except Exception as exc:
            print(colored('[insert_goals] Goals could not be inserted: {0}'.format(exc), 'red'))
            return False

    def remove_goals(self, goal_list: list) -> bool:
        '''Removes a list of goals from the knowledge base.

        Keyword arguments:
        @param goals_to_remove: list -- goals to remove from the knowledge base. The entries are
                                        tuples with two entries, the first representing
                                        the name of the predicate and the second a list of
                                        ("name", "value") pairs for the predicate parameters

        '''
        try:
            self.__remove_predicates(goal_list, self.__goal_collection_name)
            return True
        except Exception as exc:
            print(colored('[remove_goals] Goals could not be removed: {0}'.format(exc), 'red'))
            return False

    def __get_kb_collection(self, collection_name: str) -> pm.collection.Collection:
        '''Returns a pymongo collection with the given name.

        Keyword arguments:
        @param collection_name: str -- name of a MongoDB collection

        '''
        client = pm.MongoClient()
        db = client[self.__kb_database_name]
        collection = db[collection_name]
        return collection

    def __predicate_exists(self, predicate: dict) -> bool:
        '''Returns True if the given predicate exists in the knowledge base.

        Keyword arguments:
        @param predicate: dict -- a dictionary representation of a Predicate object

        '''
        collection = self.__get_kb_collection(self.__kb_collection_name)
        doc = collection.find_one(predicate)
        return doc is not None

    def __insert_predicates(self, predicate_list: list, collection_name: pm.collection.Collection) -> bool:
        '''Inserts a list of predicates into the given collection.

        Keyword arguments:
        @param predicate_list: list -- dictionary representations of Predicate objects
        @param collection_name: pm.collection.Collection -- a MongoDB collection

        '''
        for predicate_tuple in predicate_list:
            predicate = Predicate.from_tuple(predicate_tuple)
            predicate_dict = predicate.to_dict()
            if not self.__predicate_exists(predicate_dict):
                collection = self.__get_kb_collection(collection_name)
                collection.insert_one(predicate_dict)
            else:
                print(colored('Predicate {0} already exists'.format(predicate.name), 'yellow'))

    def __remove_predicates(self, predicate_list: list, collection_name: pm.collection.Collection) -> bool:
        '''Removes a list of predicates from the given collection.

        Keyword arguments:
        @param predicate_list: list -- dictionary representations of Predicate objects
        @param collection_name: pm.collection.Collection -- a MongoDB collection

        '''
        for predicate_tuple in predicate_list:
            predicate = Predicate.from_tuple(predicate_tuple)
            predicate_dict = predicate.to_dict()
            if self.__predicate_exists(predicate_dict):
                collection = self.__get_kb_collection(collection_name)
                collection.remove(predicate_dict)
            else:
                print(colored('Predicate {0} does not exist'.format(predicate.name), 'yellow'))
