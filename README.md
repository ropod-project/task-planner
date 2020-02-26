# task-planner

1. [Summary](#summary)
2. [Dependencies](#dependencies)
3. [Design principles](#design-principles)
4. [Usage examples](#usage-examples)
5. [API description](#api-description)
    1. [Planner API](#planner-api)
    2. [Knowledge base API](#knowledge-base-api)
        1. [KnowledgeBaseInterface](#knowledgebaseinterface)
        2. [Predicate](#predicate)
        3. [Fluent](#fluent)
        4. [PredicateParams](#predicateparams)
        5. [AssertionTypes](#assertiontypes)

## Summary

Defines a package (`task_planner`) that exposes interfaces to a knowledge base and a task planner.

Both [LAMA](https://arxiv.org/abs/1401.3839) and [Metric-FF](https://arxiv.org/abs/1106.5271) are currently supported.

Parameters for the planner are specified in `config/planner_config.yaml`; in particular, the following parameters need to be specified:
* `planner_name`: Name of the used planner
* `domain_file`: Absolute path of a planning domain file
* `planner_cmd`: Command used for running the task planner executable; the words "DOMAIN" and "PROBLEM" are expected to be in the command so that they can be appropriately replaced with the paths of domain and problem files
* `plan_file_path`: Directory where generated plan files should be saved

Note: The package is developed for Python 3.5+ since it makes use of Python typing.

## Dependencies

* `pymongo`
* `termcolor`
* [`ropod_common`](https://github.com/ropod-project/ropod_common)

## Design principles and assumptions

The task planner is based on the following assumptions:
* A planner working with PDDL domains is used
* The parameters of the domain predicates, fluents, and actions are explicitly typed
* Only single-robot planning is done

The following main design principles were followed in the development of this package:
* Knowledge is stored in a MongoDB database since having persistent storage of the knowledge makes it possible to recover from software failures
* To simplify the use of domain predicates, fluents, and actions within the application, an appropriate mapping needs to be defined for these (see [`task_planner/knowledge_models.py`](task_planner/knowledge_models.py) for the mapping of fluents and predicates and [`task_planner/action_models.py`](task_planner/action_models.py) for the mapping of actions)
* The design of the knowledge base interface is based on [`mas_knowledge_base`](https://github.com/b-it-bots/mas_knowledge_base)

## Usage examples

### Knowledge base

The knowledge base can be used by creating an instance of the `task_planner.knowledge_base_interface.KnowledgeBaseInterface` class:

```
from task_planner.knowledge_base_interface import KnowledgeBaseInterface
kb_interface = KnowledgeBaseInterface('ropod_kb')
```

Let's say we want to add and remove certain facts (e.g. we want to say that the gripper of a robot "frank" is empty and that it is not holding the load "mobidik_123" anymore); we can specify these facts as follows:

```
facts_to_add = [('empty_gripper', [('bot', 'frank')])]
facts_to_remove = [('holding', [('bot', 'frank'), ('load', 'mobidik_123')])]
```

Note that we represent a predicate as a tuple in which the first entry is the predicate name and the second is a list of predicate parameters ("name" and "value" pairs).

We can add and remove these facts from the knowledge base as follows:

```
kb_interface.insert_facts(facts_to_add)
kb_interface.remove_facts(facts_to_remove)
```

or with one function call:

```
kb_interface.update_kb(facts_to_add, facts_to_remove)
```

If the facts are fluents instead of predicate assertions (e.g. we want to state that the robot "frank" is at the location "BRSU_L0_C1" and that the load "mobidik_123" is not at "BRSU_L0_C1" anymore, and we also want to insert the fact that the robot "frank" is on the second floor, while the load "mobidik_123" is not on the ground floor), we can insert/remove them as follows:

```
fluents_to_add = [('robot_at', [('bot', 'frank'), ('loc', 'BRSU_L0_C1')]),
                  ('robot_floor', [('bot', 'frank')], floor2)]
fluents_to_remove = [('load_at', [('load', 'mobidik_123'), ('loc', 'BRSU_L0_C1')]),
                     ('load_floor', [('bot', 'frank')], floor0)]

# adding the fluents to the knowledge base
kb_interface.insert_fluents(fluents_to_add)

# or removing them from it
kb_interface.remove_fluents(fluents_to_remove)
```

Note that a fluent is also represented as a tuple, but with three entries instead of two, such that the first entry is the fluent name, the second a list of predicate parameters ("name" and "value" pairs), and the third the fluent value.

Planning goals can be inserted/removed just as facts, only that the function calls change (`insert_goals` and `remove_goals` respectively). Note that only predicates can be inserted as planning goals.

For a list of defined predicates and fluents, please consult the [knowledge_models](task_planner/knowledge_models.py) collection of domain mappings.

### Task planner

An example of using the LAMA task planner to create a plan for a Mobidik transportation task is given below:

```
from task_planner.lama_interface import LAMAInterface

# reading the planner configuration parameters
domain_file = ''
planner_cmd = ''
plan_file_path = ''
with open('config/planner_config.yaml', 'r') as config_file:
    planner_config = yaml.load(config_file)
    domain_file = planner_config['domain_file']
    planner_cmd = planner_config['planner_cmd']
    plan_file_path = planner_config['plan_file_path']

planner = LAMAInterface('ropod_kb', domain_file, planner_cmd, plan_file_path, debug=True)

# creating a task request
task_request = TaskRequest()
task_request.load_id = 'mobidik_123'
task_request.delivery_pose.id = 'BRSU_L0_C0'

robot_name = 'frank'

# creating the list of task goals
task_goals = [('load_at', [('load', task_request.load_id),
                           ('loc', task_request.delivery_pose.id)]),
              ('empty_gripper', [('bot', robot_name)])]

# requesting a plan
plan_found, plan = planner.plan(task_request, robot_name, task_goals)
```

## Tests

Unit tests are included under [test](test) (currently only for the LAMA planner).

## API description

### Planner API

The task planner exposes functionalities for creating a task plan given a task request and a robot task assignment. The package includes a generic interface definition - the abstract `TaskPlannerInterface` class in [`task_planner/planner_interface.py`](task_planner/planner_interface.py) - as well as planner-specific implementations, namely:
* the `LAMAInterface` class in [`task_planner/lama_interface.py`](task_planner/lama_interface.py)
* the `MetricFFInterface` class in [`task_planner/metric_ff_interface.py`](task_planner/metric_ff_interface.py)

#### TaskPlannerInterface

An abstract class containing the following fields:
* `kb_database_name`: Name of a database for storing the knowledge base
* `domain_file`: Absolute path of a planning domain file
* `domain_name`: Name of the planning domain (extracted from the domain file)
* `planner_cmd`: Command used for running a task planner; the words "DOMAIN" and "PROBLEM" are expected to be in the command so that they can be appropriately replaced with the paths of domain and problem files; for LAMA, the word "PLAN-FILE" is also expected to be passed since the planner potentially generates multiple plan files
* `plan_file_path`: Directory where generated plan files should be saved
* `debug`: A Boolean indicating whether to run the planner in debug mode (thus providing more detailed debugging output)

The following abstract methods are declared in the interface:
* `plan`: Returns a list of `ropod.structs.action.Action` objects representing a task plan for a task request and robot
* `generate_problem_file`: Generates a PDDL problem file given a list of predicate and fluent assertions and task goals
* `parse_plan`: Parses a generated plan from a file. Returns a tuple of type Tuple[bool, list], the first entry of which indicates whether the plan was found and the second of which is a list of `ropod.structs.action.Action` objects (an empty list if no plan was found)
* `process_action_str`: Converts an action string read from a plan file to a `ropod.structs.action.Action` object

### Knowledge base API

The knowledge base API defines various functionalities for working with a knowledge base and a planning domain. The primary interface for the knowledge base is the `KnowledgeBaseInterface` class in [`task_planner/knowledge_base_interface.py`], which allows inserting, retrieving, and removing positive assertions (both predicate and fluent assertions), as well as inserting and removing planning goals.

We distinguish between *predicates*, *(numerical) fluents*, and *planning goals* in the knowledge base. A predicate *p* is defined as a binary function *p(x_1, ..., x_n)* with named parameters; a fluent *f* is also a function *f(x_1, ..., x_n)* with named parameters, but can take a numerical value. Only predicates are supported as planning goals.

The interface uses custom-defined Python objects for working with predicates and fluents (see `Predicate` and `Fluent` below); however, to reduce the code verbosity for users of the interface, the methods for inserting and removing predicates/fluents/planning goals take tuple rather than the custom objects:
* A predicate tuple has two entries, the first representing the name of the predicate and the second a list of ("name", "value") pairs for the predicate parameters; in other words `p(x_1, ..., x_n)` is equivalent to `('p', [('name-x_1', 'value-x_1'), ..., ('name-x_n', 'value-x_n')])` in tuple form
* A fluent tuple takes three entries, the first representing the name of the predicate, the second a list of ("name", "value") pairs for the predicate parameters, and the third the fluent value; in other words `f(x_1, ..., x_n) = k` is equivalent to `('f', [('name-x_1', 'value-x_1'), ..., ('name-x_n', 'value-x_n')], k)` in tuple form

#### KnowledgeBaseInterface

The knowledge base interface exposes functionalities for working with a knowledge base, such as inserting, retrieving, and removing assertions (both predicate and fluent assertions), as well as inserting and removing planning goals.

The following methods are exposed by the interface:

* `get_predicate_names`: Returns a list with the names of all predicates stored in the knowledge base
* `get_fluent_names`: Returns a list with the names of all fluents stored in the knowledge base
* `get_predicate_assertions`: Returns a list of `Predicate` objects representing all assertions of a given predicate in the knowledge base. If no predicate name is given, returns all predicate assertions in the knowledge base
* `get_fluent_assertions`: Returns a list of `Fluent` objects representing all fluent assertions in the knowledge base
* `get_fluent_value`: Returns the value of a given fluent in the knowledge base (the fluent is passed as a tuple). Returns `None` if an assertion for the fluent is not found
* `update_kb`: Inserts a list of facts (predicate assertions) into the knowledge base and removes a list of facts (also predicate assertions) from it. The predicate assertions are expected to be passed as tuples
* `insert_facts`: Inserts a list of facts (predicate assertions) into the knowledge base. The facts are expected to be passed as tuples
* `remove_facts`: Removes a list of facts (predicate assertions) from the knowledge base. The facts are expected to be passed as tuples
* `update_predicate`: Updates a given predicate. The predicate is expected to be passed as a tuple
* `insert_fluents`: Inserts a list of fluents (fluent assertions) into the knowledge base. The fluents are expected to be passed as tuples
* `remove_fluents`: Removes a list of fluents (fluent assertions) from the knowledge base. The fluents are expected to be passed as tuples
* `update_fluent`: Updates a given fluent. The fluent is expected to be passed as a tuple
* `insert_goals`: Inserts a list of goals (predicate assertions) into the knowledge base. The goals are expected to be passed as tuples
* `remove_goals`: Removes a list of goal (predicate assertions) from the knowledge base. The goals are expected to be passed as tuples

#### Predicate

`Predicate` is a class representing a predicate `p(x_1, ..., x_n)`. The class has the following two fields:
* `name`: The name of the predicate
* `params`: A list of `PredicateParams` objects representing the predicate parameters

The following methods are exposed by the `Predicate` class:
* `to_dict`: Converts a `Predicate` object to a dictionary with two keys - "name" and "params", where the value of "params" is a list of `PredicateParams` dictionaries
* `from_tuple` (static): Creates a `Predicate` object from a given tuple
* `from_dict` (static): Creates a `Predicate` object from a given predicate dictionary (in the form returned by `to_dict`)
* `__eq__`: The comparison operator is overridden for comparing two `Predicate` objects; returns True if both the names and all parameters are the same

#### Fluent

The `Fluent` class represents a fluent `f(x_1, ..., x_n) = k`. The class has the following three fields:
* `name`: The name of the fluent
* `params`: A list of `PredicateParams` objects representing the fluent parameters
* `value`: The value taken by the fluent at the current time instant

The following methods are exposed by the `Fluent` class:
* `to_dict`: Converts a `Fluent` object to a dictionary with three keys - "name", "params", and "value", where the value of "params" is a list of `PredicateParams` dictionaries
* `from_tuple` (static): Creates a `Fluent` object from a given tuple
* `from_dict` (static): Creates a `Fluent` object from a given predicate dictionary (in the form returned by `to_dict`)
* `__eq__`: The comparison operator is overridden for comparing two `Fluent` objects; returns True if both the names and all parameters are the same

#### PredicateParams

`PredicateParams` represents an argument of a predicate or a fluent, namely the argument's name and value. The following fields are defined in the class:
* `name`: The name of an argument
* `value`: The argument value

The following methods are exposed by the `PredicateParams` class:
* `to_dict`: Converts a `PredicateParams` object to a dictionary with two keys - "name" and "value"
* `from_tuple` (static): Creates a `PredicateParams` object from a given tuple
* `from_dict` (static): Creates a `PredicateParams` object from a given predicate dictionary (in the form returned by `to_dict`)
* `__eq__`: The comparison operator is overridden for comparing two `PredicateParams` objects; returns True if both the names and values of two parameters are the same
* `__neq__`: The comparison operator is overridden for comparing two `PredicateParams` objects; returns True if either the names or the values of two parameters differ

#### AssertionTypes

A class defining constants for working with assertions. The following two constants are defined in the class:
* `PREDICATE = 'predicate'`
* `FLUENT = 'fluent'`
