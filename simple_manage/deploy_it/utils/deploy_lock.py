# coding: utf-8
import os

DEPLOYING_INFO_FILE = 'deploying.info'

def is_deploying():
    if os.path.exists(DEPLOYING_INFO_FILE):
        return True

def set_deploying(deploying):
    if deploying:
        deploying_file = open(DEPLOYING_INFO_FILE, 'w')
        deploying_file.close()
    else:
        if is_deploying():
            os.remove(DEPLOYING_INFO_FILE)
