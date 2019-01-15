from setuptools import setup, find_packages

setup(name='task_planner',
      version='1.0.0',
      description='A planning library',
      url='https://github.com/ropod-project/task-planning',
      author='Alex Mitrevski',
      author_email='aleksandar.mitrevski@h-brs.de',
      keywords='robotics task_planning',
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      project_urls={
          'Source': 'https://github.com/ropod-project/task-planning'
      })
