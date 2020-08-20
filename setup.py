from setuptools import find_packages, setup

setup(name='loggingbot',
      description='Helper class to provide a logging handler linked to a Telegram Bot',
      version='master',
      python_requires='>=3.7',
      install_requires=[
            'pyTelegramBotAPI==3.7.2',
      ],
      author='dmitryikh',
      author_email='',
      url='https://github.com/Guillelerial/loggingbot.git',
      packages=find_packages())