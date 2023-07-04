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

def test_rt_switch_corr(data, alpha=0.05):
    """Checking for a significant pearson correlation between switching and response time."""
    r, p_val = stats.pearsonr(data['loop_type_switch'], data['rt'])
    significance = 'significant' if p_val < alpha else 'not significant'
    print(f"""Pearson correlation between loop type switching and response time 
          is {significance} (p = {round(p_val, 3)}), with value of r = {round(r, 3)}""")
    return None
    
##############################
########## Filtering #########
##############################

def is_prev_correct(raw_data, data, columns: dict = config.analysis_config['is_prev_correct_cols']):
    """For each step in data, checking whether previous step is correct."""
    index_columns = [columns['subject'], columns['session'], columns['step']]
    indexed = raw_data.set_index(index_columns)
    indexed = indexed[[columns['correct']]]
    
    def get_prev_correct(row):
        subject = row.loc[columns['subject']]
        session = row.loc[columns['session']]
        step = row.loc[columns['step']]
        
        return indexed.loc[(subject, session, (step - 1)), [columns['correct']]] 
        
    data['is_prev_correct'] = data.apply(get_prev_correct, axis=1)
    
    incorrect_steps = data['is_prev_correct'].size - data['is_prev_correct'].sum()
    print(f'There are {incorrect_steps} steps whose previous step is incorrect.')
    return None