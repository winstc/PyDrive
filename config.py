import json
import os

HOME_DIR = os.path.expanduser('~')
CONFIG_DIR = os.path.join(HOME_DIR, '.PyDrive')


def get_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    return CONFIG_DIR


def mk_config():
    config_file = os.path.join(CONFIG_DIR, 'PyDriveCfg.json')
    if not os.path.isfile(config_file):
        f = open(config_file, "w+")
        f.write("Py Drive Config File")
        f.close()

mk_config()
