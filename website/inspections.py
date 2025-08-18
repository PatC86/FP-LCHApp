# Name      : inspections
# Author    : Patrick Cronin
# Date      : 14/08/2025
# Updated   : 15/08/2025
# Purpose   : Functions for lifting equipment inspections, calculation of health score for lifting chains and pass status.

import logging
from flask import flash

PASS_SCORE_THRESHOLD = 80
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

    except Exception as e:
        flash('An error occurred while processing the condition score', 'error')
        logging.error(f"An error occurred while processing the condition score{e}")
        raise


def lchealthscore(measure_mean_pitch_length, chain_pitch_length):
    '''function to calculate lifting chain health score based on original pitch length of chain and measure mean pitch length'''
    try:
        measure_mean_pitch_length = int(measure_mean_pitch_length)
        chain_pitch_length = int(chain_pitch_length)

        if chain_pitch_length < MIN_PITCH_LENGTH:
            flash(f'Chain pitch length must be greater than or equal to minimum length of chain {MIN_PITCH_LENGTH} mm.',
                  'error')
        if chain_pitch_length > MAX_PITCH_LENGTH:
            flash(f'Chain pitch length must be less than or equal to maximum chain length {MAX_PITCH_LENGTH} mm.',
                  'error')
        if measure_mean_pitch_length < chain_pitch_length:
            flash('Mean measured pitch length should be greater than or equal to the chain pitch length.', 'error')

        health_score = float((chain_pitch_length / measure_mean_pitch_length) * 100)
        return health_score
    except Exception as e:
        logging.error(f'Failure to calculate percentage wear: {e}')
        raise


def lcpass(condition_pass, health_score):
    '''function to calculate if lifting chain has passed inspection'''
    try:
        if condition_pass == False:
            return False
        elif health_score < PASS_SCORE_THRESHOLD:
            return False
        else:
            return True

    except Exception as e:
        flash('An error occurred while processing the lifting chain score', 'error')
        logging.error(f"An error occurred while processing the lifting chain score{e}")
        raise
