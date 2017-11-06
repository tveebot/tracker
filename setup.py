from setuptools import setup, find_packages

setup(
    name='tveebot-tracker',
    version='0.1',
    description='Tool to track new episodes from TV Shows',
    url='https://github.com/tveebot/tracker',
    license='MIT',
    author='David Fialho',
    author_email='fialho.david@protonmail.com',

    packages=find_packages(),

    package_data={
        'tveebot_tracker': ['config.ini'],
    },
)
