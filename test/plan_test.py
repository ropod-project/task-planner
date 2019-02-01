#!/usr/bin/env python3
import yaml
from ropod.structs.task import TaskRequest
from task_planner.metric_ff_interface import MetricFFInterface

planner_name = ''
domain_file = ''
planner_cmd = ''
plan_file_path = ''
with open('config/planner_config.yaml', 'r') as config_file:
    planner_config = yaml.load(config_file)
    planner_name = planner_config['planner_name']
    domain_file = planner_config['domain_file']
    planner_cmd = planner_config['planner_cmd']
    plan_file_path = planner_config['plan_file_path']

planner = MetricFFInterface('ropod_kb', domain_file, planner_cmd, plan_file_path, debug=True)

task_request = TaskRequest()
task_request.cart_id = 'mobidik_123'
task_request.delivery_pose.id = 'BRSU_L0_C0'

robot_name = 'frank'
task_goals = [('cart_at', [('cart', task_request.cart_id),
                           ('loc', task_request.delivery_pose.id)]),
              ('empty_gripper', [('bot', robot_name)])]
plan_found, plan = planner.plan(task_request, robot_name, task_goals)
