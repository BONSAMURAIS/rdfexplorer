import os

from environs import Env

basedir = os.path.abspath(os.path.dirname(__file__))
env = Env()
env.read_env()


class Config:
    SECRET_KEY = env.str('SECRET_KEY', 'dev')
    RDF_DATA_DIR = env.path('RDF_DATA_DIR')
