import pandas as pd
from scipy import stats
import ProcessingConfig as config

# This file contains all the functions dealing with processing of the data
# directly for analysis.

##############################
##### General Information ####
##############################

def get_sample_size(data, subject_col='subject', session_col='trial_set'):
    """This func is used to get the amount of session and subjects in data."""
    n_subjects = data[subject_col].nunique()
    n_sessions = data[[subject_col, session_col]].drop_duplicates().shape[0]

    print(f'There are {n_sessions} sessions from {n_subjects} subjects.')
    return None
    
##############################
###### Statistical Tests #####
##############################

def test_rt_switch_corr(data, alpha=0.05, col1='loop_type_switch', col2='rt', print_msg=True):
    """Checking for a significant pearson correlation between switching and response time."""
    r, p_val = stats.pearsonr(data[col1], data[col2])
    if print_msg:
        significance = 'significant' if p_val < alpha else 'not significant'
        print(f"""Pearson correlation between loop type switching and response time 
            is {significance} (p = {round(p_val, 3)}), with value of r = {round(r, 3)}""")
        return None
    else:
        return r
    
##############################
########## Filtering #########
##############################

def is_prev_correct(raw_data, data, columns: dict = config.analysis_config['is_prev_correct_cols']
                    , check_loop_type_switch=True):
    """For each step in data, checking whether previous step is correct."""
    index_columns = [columns['subject'], columns['session'], columns['step']]
    indexed = raw_data.set_index(index_columns)
    indexed = indexed[[columns['correct'], columns['loop_step'], columns['step_type']]]
    
    def get_prev_correct(row):
        subject = row.loc[columns['subject']]
        session = row.loc[columns['session']]
        step = row.loc[columns['step']]
        step_type = row.loc[columns['step_type']]
        
        prev_loop_step = indexed.loc[(subject, session, (step - 2)), columns['loop_step']]
        if step_type == 'assign':
            print('Problem in get_prev_correct: assign step is found within data.')
        else: # previous step required a response
            return indexed.loc[(subject, session, (step - 1)), columns['correct']]
        
    data['is_prev_correct'] = data.apply(get_prev_correct, axis=1)
    
    incorrect_steps = data['is_prev_correct'].size - (data['is_prev_correct'] == 1).sum()
    print(f'There are {incorrect_steps} steps whose previous step is incorrect.')
    return None

def get_arithmetics(data, arithmetics_col = 'arithmetic_type'
                    , columns: dict = config.analysis_config['get_arithmetics_cols']):
    """Extracting the type of arithmetic subject is making in every step.
    Arithmetic types include: [+, -, /, *, average, round_up, round_down, loop_end].
    This func adds a column to the data (DataFrame) with tuples of arithmetics in each line. 
    """
    loop_lines_col, loop_step_col, text_col = columns['loop_lines'], columns['loop_step'], columns['text']
    arithmetics = ['+', '-', '/', '*', 'average', 'round_up', 'round_down']
    
    data[arithmetics_col] = [[] for _ in range(data.shape[0])]
    
    def get_arith(row):
        text, loop_lines, loop_step = row.loc[text_col], row.loc[loop_lines_col], row.loc[loop_step_col]
        if loop_step == -1:
            row.loc[arithmetics_col].append('loop_end')
        else:        
            curr_line_idx = loop_step % loop_lines + 1 # index of current code line
            curr_line = text.splitlines()[curr_line_idx] # text of current code line
            for arith in arithmetics:
                if curr_line.find(arith) != -1:
                    row.loc[arithmetics_col].append(arith)
        return None
    
    data.apply(get_arith, axis=1)
    data[arithmetics_col] = data[arithmetics_col].apply(lambda x: str(x))
    
    return None

def get_n_session(data, participant_ids_path=config.analysis_config['participant_ids']):
    """ Getting the right session number using the configuration file.
    Notice that the columns' names both of 'data' and participant_ids is fixed.
    """
    participant_ids = pd.read_excel(participant_ids_path)
    participant_ids = participant_ids[['Subject ID', 'In session #1, run block #']]

    data = data.merge(participant_ids, how='left', left_on=['subject', 'trial_set']
                        , right_on=['Subject ID', 'In session #1, run block #'])

    data.rename(columns={'In session #1, run block #': 'n_session'}, inplace=True)
    data['n_session'] = data['n_session'].replace(2.0, 1.0)
    data['n_session'].fillna(2.0, inplace=True)
    data['n_session'] = data['n_session'].astype(int)
    
    data.drop('Subject ID', axis=1)
    return data