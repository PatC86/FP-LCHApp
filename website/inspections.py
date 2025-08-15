# Name      : inspections
# Author    : Patrick Cronin
# Date      : 14/08/2025
# Updated   : 15/08/2025
# Purpose   : Functions for lifting equipment inspections, calculation of health score for lifting chains and pass status.

import logging
from flask import flash

PASS_SCORE_THRESHOLD = 60
MIN_CHAIN_LENGTH = 1.0
MAX_CHAIN_LENGTH = 50.0
MIN_PITCH_LENGTH = 100
MAX_PITCH_LENGTH = 500
MIN_PITCHES_MEASURED = 10
CONDITION_FAILURE_THRESHOLD = 5

def conditioncheck(condition):
    '''function to check the condition provided by the user and determines the asset has failed the inspection based on the condition score'''
    try:
        condition = int(condition)

        if condition >= CONDITION_FAILURE_THRESHOLD:
            return False
        else:
            return True

    except ValueError as e:
        flash('Invalid condition score provided. Please try again.', 'error')
        logging.error(f"An error occurred while processing the condition score{e}")
        raise
    except Exception as e:
        flash('An error occurred while processing the condition score', 'error')
        logging.error(f"An error occurred while processing the condition score{e}")
        raise