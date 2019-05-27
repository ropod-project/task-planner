from typing import Tuple
import pymongo as pm
from bson.objectid import ObjectId
from termcolor import colored
import logging


class AssertionTypes(object):
    PREDICATE = 'predicate'
    FLUENT = 'fluent'


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

    def to_tuple(self) -> Tuple[str, str]:
        '''Convert object to tuple(str, str)
        '''
        return (self.name, self.value)

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

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        return "PredicateParams(" + str(self.to_dict()) + ")"

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
        dict_predicate['type'] = AssertionTypes.PREDICATE
        dict_predicate['params'] = []
        for param_data in self.params:
            dict_params = param_data.to_dict()
            dict_predicate['params'].append(dict_params)
        return dict_predicate

    def to_tuple(self) -> Tuple[str, list]:
        '''Convert object to tuple containing 2 elements
        name -- string
        params -- list of tuple(str, str)
        '''
        return (self.name, [param.to_tuple() for param in self.params])

    @staticmethod
    def from_tuple(tuple_predicate: Tuple[str, list]):
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

    def __str__(self) -> str:
        string = "Predicate(\n" 
        string += '\t' + 'name:' + str(self.name) + '\n'
        string += '\t' + 'type:' + str(AssertionTypes.PREDICATE) + '\n'
        string += '\t' + 'params:[' + '\n'
        for param in self.params:
            string += '\t\t' + str(param) + '\n'
        string += '\t' + ']' + '\n'
        string += ")"
        return string

    def __repr__(self) -> str:
        return "Predicate(" + str(self.to_dict()) + ")"

class Fluent(object):
    '''An object representing a fluent (fluent name, list of ground values, and fluent value).

    @author Alex Mitrevski
    @contact aleksandar.mitrevski@h-brs.de

    '''
    def __init__(self):
        self.name = ''
        self.params = []
        self.value = None

    def __eq__(self, other) -> bool:
        '''Returns True if the names, values, and all parameters are the same.
        '''
        equal = False
        if self.name == other.name and self.value == other.value:
            equal = True
            for param in self.params:
                if param not in other.params:
                    equal = False
                    break
        return equal

    def to_dict(self) -> dict:
        '''Converts the object to a dictionary with three keys - "name", "params", and "value".
        The value of "params" is a list of PredicateParams dictionaries.
        '''
        dict_fluent = {}
        dict_fluent['name'] = self.name
        dict_fluent['type'] = AssertionTypes.FLUENT
        dict_fluent['value'] = self.value
        dict_fluent['params'] = []
        for param_data in self.params:
            dict_params = param_data.to_dict()
            dict_fluent['params'].append(dict_params)
        return dict_fluent

    def to_tuple(self) -> Tuple[str, list, str]:
        '''Convert the object to tuple for with 3 elements namely
        name -- string
        params -- list of tuple(str, str)
        value -- int or string
        '''
        return (self.name, [param.to_tuple() for param in self.params], self.value)

    @staticmethod
    def from_tuple(tuple_fluent: tuple):
        '''Returns a Fluent object created from the input tuple.

        Keyword arguments:
        @param tuple_fluent -- a tuple with three entries, the first representing
                               the name of the predicate, the second a list of
                               ("name", "value") pairs for the predicate parameters,
                               and the third the fluent value

        '''
        fluent = Fluent()
        fluent.name, tuple_data, fluent.value = tuple_fluent
        for tuple_params in tuple_data:
            params = PredicateParams.from_tuple(tuple_params)
            fluent.params.append(params)
        return fluent

    @staticmethod
    def from_dict(dict_fluent: dict):
        '''Returns a Fluent object created from the input dictionary.

        Keyword arguments:
        @param dict_fluent-- a dictionary with three keys - "name", "params", and "value",
                             where "params" is a list of PredicateParams dictionaries

        '''
        fluent = Fluent()
        fluent.name = dict_fluent['name']
        fluent.value = dict_fluent['value']
        dict_data = dict_fluent['params']
        for dict_params in dict_data:
            params = PredicateParams.from_dict(dict_params)
            fluent.params.append(params)
        return fluent

    def __str__(self) -> str:
        string = "Fluent(\n" 
        string += '\t' + 'name:' + str(self.name) + '\n'
        string += '\t' + 'value:' + str(self.value) + '\n'
        string += '\t' + 'type:' + str(AssertionTypes.FLUENT) + '\n'
        string += '\t' + 'params:[' + '\n'
        for param in self.params:
            string += '\t\t' + str(param) + '\n'
        string += '\t' + ']' + '\n'
        string += ")"
        return string

    def __repr__(self) -> str:
        return "Fluent(" + str(self.to_dict()) + ")"

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
        self.logger = logging.getLogger('task.planner.kb.interface')

    def get_predicate_names(self) -> list:
        '''Returns a list of all stored predicate names in the knowledge base.
        '''
        collection = self.__get_kb_collection(self.__kb_collection_name)
        predicate_cursor = collection.find({'type': AssertionTypes.PREDICATE})
        names = list({p['name'] for p in predicate_cursor})
        return names

    def get_fluent_names(self) -> list:
        '''Returns a list of all stored fluent names in the knowledge base.
        '''
        collection = self.__get_kb_collection(self.__kb_collection_name)
        fluent_cursor = collection.find({'type': AssertionTypes.FLUENT})
        names = list({f['name'] for f in fluent_cursor})
        return names

    def get_predicate_assertions(self, predicate_name: str=None) -> list:
        '''Returns a list of Predicate objects representing all assertions
        of the given predicate in the knowledge base. If "predicate_name" is None,
        returns all predicate assertions in the knowledge base.

        Keyword arguments:
        @param predicate_name: str -- name of a predicate in the knowledge base
                                      (default None, in which case all assertions
                                       are retrieved)

        '''
        instances = []
        collection = self.__get_kb_collection(self.__kb_collection_name)
        if predicate_name:
            pred_instance_count = collection.count_documents({'name': predicate_name})
            if pred_instance_count == 0:
                return []

            pred_instance_cursor = collection.find({'name': predicate_name})
            instances = [Predicate.from_dict(p) for p in pred_instance_cursor]
        else:
            assertion_cursor = collection.find({'type': AssertionTypes.PREDICATE})
            instances = [Predicate.from_dict(p) for p in assertion_cursor]
        return instances

    def get_fluent_assertions(self) -> list:
        '''Returns a list of Fluent objects representing all fluent assertions
        in the knowledge base.
        '''
        instances = []
        collection = self.__get_kb_collection(self.__kb_collection_name)
        assertion_cursor = collection.find({'type': AssertionTypes.FLUENT})
        instances = [Fluent.from_dict(p) for p in assertion_cursor]
        return instances

    def get_fluent_value(self, fluent: Tuple[str, list]) -> list:
        '''Returns the value of the given fluent in the knowledge base.
        Returns None if an assertion for the fluent is not found.

        Keyword arguments:
        @param fluent: Tuple[str, list] -- a tuple representing a fluent, where
                                           the first entry is the fluent name and
                                           the second entry is a list of fluent parameters

        '''
        fluent_value = None

        # we add a dummy fluent value so that we can create a fluent dictionary
        fluent_full = (fluent[0], fluent[1], -1)
        fluent_dict = Fluent.from_tuple(fluent_full).to_dict()

        collection = self.__get_kb_collection(self.__kb_collection_name)
        fluent_cursor = collection.find({'name': fluent_dict['name']})
        fluent_assertion = None
        for f in fluent_cursor:
            found = True
            for param in f['params']:
                if param not in fluent_dict['params']:
                    found = False
                    break
            if found:
                fluent_assertion = f
                break

        if fluent_assertion:
            fluent_value = fluent_assertion['value']
        else:
            self.logger.warning('Fluent %s not found', fluent_dict['name'])
        return fluent_value

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
            self.logger.error('[insert_facts] Facts could not be inserted: ', exc_info=True)
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
            self.logger.error('[remove_facts] Facts could not be removed: ', exc_info=True)
            return False

    def insert_fluents(self, fluent_list: list) -> bool:
        '''Inserts a list of fluents into the knowledge base.

        Keyword arguments:
        @param fluents_to_add: list -- fluents to add to the knowledge base. The entries are
                                       tuples with three entries of the form
                                       (name, [parameters], value), namely the first entry
                                       represents the name of the fluent, the second
                                       a list of ("name", "value") pairs for the
                                       fluent parameters, and the third the fluent value

        '''
        try:
            self.__insert_fluents(fluent_list, self.__kb_collection_name)
            return True
        except Exception as exc:
            self.logger.error('[insert_fluents] Fluents could not be inserted:', exc_info=True)
            return False

    def remove_fluents(self, fluent_list: list) -> bool:
        '''Removes a list of fluents from the knowledge base.

        Keyword arguments:
        @param fluents_to_remove: list -- fluents to remove from the knowledge base. The entries
                                          are tuples with two entries of the form
                                          (name, [parameters], value), namely the first entry
                                          represents the name of the fluent and the second
                                          a list of ("name", "value") pairs for the
                                          fluent parameters

        '''
        try:
            self.__remove_fluents(fluent_list, self.__kb_collection_name)
            return True
        except Exception as exc:
            self.logger.error('[remove_fluents] Fluents could not be removed: ', exc_info=True)
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
            self.logger.error('[insert_goals] Goals could not be inserted: ', exc_info=True)
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
            self.logger.error('[remove_goals] Goals could not be removed: ', exc_info=True)
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

    def __item_exists(self, item: dict, item_type: str, collection_name: str) -> ObjectId:
        '''Returns True if the given predicate or fluent exists in the knowledge base.

        Keyword arguments:
        @param item: dict -- a dictionary representation of a Predicate or a Fluent object
        @param item_type: str -- an AssertionTypes string indicating whether
                                 the item is a predicate or a fluent

        '''
        collection = self.__get_kb_collection(collection_name)
        item_cursor = collection.find({'name': item['name'], 'type': item_type})
        exists = False
        object_id = None
        for kb_item in item_cursor:
            exists = True
            for param in kb_item['params']:
                if param not in item['params']:
                    exists = False
                    break
            if exists:
                object_id = kb_item['_id']
                break
        return object_id

    def __insert_predicates(self, predicate_list: list, collection_name: str) -> bool:
        '''Inserts a list of predicates into the given collection.

        Keyword arguments:
        @param predicate_list: list -- tuple representations of Predicate objects
        @param collection_name: pm.collection.Collection -- a MongoDB collection

        '''
        for predicate_tuple in predicate_list:
            predicate = Predicate.from_tuple(predicate_tuple)
            predicate_dict = predicate.to_dict()
            if not self.__item_exists(predicate_dict, AssertionTypes.PREDICATE, collection_name):
                collection = self.__get_kb_collection(collection_name)
                collection.insert_one(predicate_dict)
            else:
                self.logger.warning('Predicate %s already exists', predicate.name)

    def __remove_predicates(self, predicate_list: list, collection_name: str) -> bool:
        '''Removes a list of predicates from the given collection.

        Keyword arguments:
        @param predicate_list: list -- tuple representations of Predicate objects
        @param collection_name: pm.collection.Collection -- a MongoDB collection

        '''
        collection = self.__get_kb_collection(collection_name)
        for predicate_tuple in predicate_list:
            predicate = Predicate.from_tuple(predicate_tuple)
            predicate_dict = predicate.to_dict()
            object_id = self.__item_exists(predicate_dict, AssertionTypes.PREDICATE, collection_name)
            if object_id:
                collection.delete_one({'_id': object_id})
            else:
                self.logger.warning('Predicate %s does not exist', predicate.name)

    def __insert_fluents(self, fluent_list: list, collection_name: str) -> bool:
        '''Inserts a list of fluents into the given collection.
        If a fluent already exists, its value is updated.

        Keyword arguments:
        @param fluent_list: list -- tuple representations of Fluent objects
        @param collection_name: pm.collection.Collection -- a MongoDB collection

        '''
        for fluent_tuple in fluent_list:
            fluent = Fluent.from_tuple(fluent_tuple)
            fluent_dict = fluent.to_dict()
            collection = self.__get_kb_collection(collection_name)
            if not self.__item_exists(fluent_dict, AssertionTypes.FLUENT, collection_name):
                collection.insert_one(fluent_dict)
            else:
                self.logger.warning('Fluent %s already exists; updating the value', fluent.name)
                collection.replace_one({'name': fluent_dict['name'],
                                        'params': fluent_dict['params']},
                                       fluent_dict)

    def __remove_fluents(self, fluent_list: list, collection_name: str) -> bool:
        '''Removes a list of fluents from the given collection.

        Keyword arguments:
        @param fluent_list: list -- tuple representations of Fluent objects
        @param collection_name: pm.collection.Collection -- a MongoDB collection

        '''
        collection = self.__get_kb_collection(collection_name)
        for fluent_tuple in fluent_list:
            fluent = Fluent.from_tuple(fluent_tuple)
            fluent_dict = fluent.to_dict()
            object_id = self.__item_exists(fluent_dict, AssertionTypes.FLUENT, collection_name)
            if object_id:
                collection.delete_one({'_id': object_id})
            else:
                self.logger.warning('Fluent %s does not exist; nothing to remove', fluent.name)
