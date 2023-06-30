import pandas as pd
from scipy import stats
from ProcessingConfig import *

def get_sample_size(data, subject_col='subject', session_col='trial_set'):
    """This func is used to get the amount of session and subjects in data."""
    n_subjects = data[subject_col].nunique()
    n_sessions = data[[subject_col, session_col]].drop_duplicates().shape[0]

    print(f'There are {n_sessions} sessions from {n_subjects} subjects.')
    
def test_rt_switch_corr(data, alpha=0.05):
    """checking for a significant pearson correlation between switching and response time."""
    r, p_val = stats.pearsonr(data['loop_type_switch'], data['rt'])
    significance = 'significant' if p_val < alpha else 'not significant'
    print(f"""Pearson correlation between loop type switching and response time 
          is {significance} (p = {round(p_val, 3)}), with value of r = {round(r, 3)}""")