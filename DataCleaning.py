import pandas as pd
from os import listdir
from os.path import isfile, join
from ProcessingConfig import *

######################################
##### clean functions definition #####
######################################

# initial pre-processing

def drop_columns(raw_data, cols: list):
    """ filtering out unnecessary columns according to a columns list in cleaning_config.
    """
    raw_data.drop(cols, axis=1, inplace=True)
    return None

def convert_types(raw_data, conversions: dict):
    """ making type conversions to necessary columns a conversion dict in cleaning_config
    """
    for type_, cols in conversions.items():
        for col in cols:
            raw_data.fillna(0, inplace=True)
            raw_data[col] = raw_data[col].astype(type_)
    return None


# taking out first loop in a program, first line in a loop

def drop_first_loop(raw_data):
    """ filtering out first loop within each program.
    """
    # note that 'step_id' is an id of each loop within a given program, ranging 1-9,
    # where the first loop is essentially a variable assignment.
    first_loop_filter = raw_data['step_id'] != 2
    raw_data = raw_data[first_loop_filter]
    return raw_data

def drop_first_line(raw_data):
    # note that 'loop_step' is an id of each step in the loop, ranging 0-len(loop).
    first_line_filter = raw_data['loop_step'] != 0
    raw_data = raw_data[first_line_filter]
    return raw_data


###########################
##### actual cleaning #####
###########################

raw_data = pd.read_excel(cleaning_config['raw_data_path'])

def main(raw_data):
    drop_columns(raw_data, cleaning_config['unnecessary_columns'])
    convert_types(raw_data, cleaning_config['type_conversions'])
    raw_data = drop_first_loop(raw_data)
    raw_data = drop_first_line(raw_data)
    return raw_data

raw_data = main(raw_data)