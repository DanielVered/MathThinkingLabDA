import pandas as pd
from datetime import datetime as dt
import ProcessingConfig as config

# This file contains all the functions dealing with initial processing of the data
# and other processing and filtering for the analysis.

##############################
##### Envelope Functions #####
##############################

def clean_data(raw_data, outliers_threshold=config.cleaning_config['filter_threshold']
               , only_first_lines=True, filter_subjects=True, filter_trials=True, filter_steps=True):
    print(f"original shape: {raw_data.shape}")
    print(f"threshold for outliers detection: {outliers_threshold}")
    
    drop_columns(raw_data, config.cleaning_config['unnecessary_columns'])
    convert_types(raw_data, config.cleaning_config['type_conversions'])
    if filter_subjects:
        filtered_data = filter_slow_subjects(raw_data, outliers_threshold)
        filtered_data = filter_bad_subjects(filtered_data, outliers_threshold)
        filtered_data = drop_first_loop(filtered_data)
    filtered_data = is_first_line(filtered_data, only_first_lines=True)
    if filter_trials:
        filtered_data = filter_bad_trials(filtered_data
                                          , threshold=config.cleaning_config['trials_success_rate_threshold'])
    if filter_steps:
        filtered_data = filter_slow_steps(filtered_data, outliers_threshold)
        
    print(f'final shape: {filtered_data.shape}')
    return filtered_data

def save_in_excel(data, directory=config.cleaning_config['results_path']):
    path = directory + f'_{dt.now().strftime("%d.%m.%Y_%H-%M")}.xlsx'
    data.to_excel(path)

##############################
##### Initial Processing #####
##############################

def drop_columns(raw_data, cols: list):
    """ filtering out unnecessary columns according to a columns list in cleaning_config.
    """
    try:
        raw_data.drop(cols, axis=1, inplace=True)
    except:
        pass
    return None

def convert_types(raw_data, conversions: dict):
    """ making type conversions to necessary columns a conversion dict in cleaning_config.
    """
    for type_, cols in conversions.items():
        for col in cols:
            if type_ == int:
                raw_data[col].fillna(-1, inplace=True)
            else:
                raw_data[col].fillna(0, inplace=True)
            raw_data[col] = raw_data[col].astype(type_)
    return None

def drop_first_loop(raw_data):
    """ filtering out first loop within each program.
    """
    # note that 'step_id' is an id of each loop within a given program, ranging 1-9,
    # where the first loop is essentially a variable assignment.
    first_loop_filter = raw_data['step_id'] != 2
    raw_data = raw_data[first_loop_filter]
    
    n_rows_filtered = first_loop_filter.size - first_loop_filter.sum()
    print(f"drop_first_loop: {n_rows_filtered} rows were filtered out.")
    return raw_data

def is_first_line(raw_data, only_first_lines=True):    
    """ filtering out non-first lines within each loop.
    """
    # note that 'loop_step' is an id of each step in the loop, ranging 0-len(loop).
    raw_data['is_first_line'] = raw_data['loop_step'] == 0
    if only_first_lines:
        raw_data = raw_data[raw_data['is_first_line']]
    else:
        n_first_lines = raw_data.shape[0] - raw_data['is_first_line'].sum()
        print(f"is_first_line: There are {n_first_lines} first lines over all.")

    return raw_data

##############################
##### Outliers Filtering #####
##############################

def is_negative_outlier(x, x_q1, x_iqr, threshold):
    """finding if a datapoint is a negative (low) outlier using IQR, according to a given threshold."""
    if x_iqr == 0 or x > x_q1:
        return False
    
    return (x_q1 - x) / x_iqr >= threshold

def is_positive_outlier(x, x_q3, x_iqr, threshold):
    """finding if a datapoint is a negative (low) outlier using IQR, according to a given threshold."""
    if x_iqr == 0 or x < x_q3:
        return False
    
    return (x - x_q3) / x_iqr >= threshold

def get_outlier_grade(step: pd.Series, col: str):
    """ Calculating an outlier grade in terms of response time within subject, using IQR.
    It is assumed that the Series has the following indices: ['q1', 'q3', 'iqr'].
    """
    x = step.loc[col]
    q1, q3, iqr = step.loc['q1'], step.loc['q3'], step.loc['iqr']
    
    if iqr == 0 or (q1 <= x and x <= q3): # 0 means inside IQR range.
        return 0
    elif x < q1: 
        return (x - q1) / iqr # negative grade --> slow step
    elif x > q3:
        return (x - q3) / iqr # positive grade --> fast step


def filter_slow_subjects(raw_data, threshold):
    """filtering out slow subjects in terms of response time using IQR, according to a given threshold."""
    rt_per_subject = raw_data[['rt', 'subject']].groupby('subject').mean()
    rt_per_subject.columns = ['mean_rt']

    g_rt_q1, g_rt_q3 = rt_per_subject['mean_rt'].quantile([0.25, 0.75])
    g_rt_iqr = g_rt_q1 - g_rt_q3
    
    rt_per_subject = raw_data[['subject']].merge(rt_per_subject, how='left', left_on='subject', right_index=True)

    slow_subjects_mask = rt_per_subject['mean_rt'].apply(is_positive_outlier
                                                        , args=(g_rt_q3, g_rt_iqr, threshold))
    
    slow_subjects = rt_per_subject[slow_subjects_mask]
    if slow_subjects.size > 0: # if there are any slow subjects, print an explanatory message
        n_subjects_filtered = slow_subjects['subject'].nunique()
        slow_subjects['grade'] = slow_subjects['mean_rt'].apply(lambda x: (x - g_rt_q3) / g_rt_iqr)
        print(f'filter_slow_subjects: {n_subjects_filtered} slow subjects detected:')
        print('    ', slow_subjects)
    else:
        print('filter_slow_subjects: No slow subjects detected.')
        
    return raw_data[~ slow_subjects_mask]

def filter_bad_subjects(raw_data, threshold):
    """filtering out bad subjects in terms of low success rate using IQR, according to a given threshold."""
    success_per_subject = raw_data[['correct', 'subject']].groupby('subject').mean()
    success_per_subject.columns = ['success_rate']

    g_success_q1, g_success_q3 = success_per_subject['success_rate'].quantile([0.25, 0.75])
    g_success_iqr = g_success_q1 - g_success_q3
    
    success_per_subject = raw_data[['subject']].merge(success_per_subject, how='left', left_on='subject', right_index=True)

    bad_subjects_mask = success_per_subject['success_rate'].apply(is_negative_outlier
                                                        , args=(g_success_q1, g_success_iqr, threshold))
    
    bad_subjects = success_per_subject[bad_subjects_mask]
    if bad_subjects.size > 0: # if there are any bad subjects, print an explanatory message
        n_subjects_filtered = bad_subjects['subject'].nunique()
        bad_subjects['grade'] = bad_subjects['success_rate'].apply(lambda x: (g_success_q1 - x) / g_success_iqr)
        print(f'filter_bad_subjects: {n_subjects_filtered} bad subjects detected (in terms of low success rate):')
        print(bad_subjects)
    else:
        print('filter_bad_subjects: No bad subjects detected (in terms of low success rate).')
        
    return raw_data[~ bad_subjects_mask]

def filter_bad_trials(raw_data, threshold):
    """ filtering out bad trials in terms of low success rate according to an pre-determined threshold.
    It is important to note that threshold should be within (0, 1).
    """    
    # filtering only necessary columns
    response_success = raw_data[['subject', 'trial', 'correct']].copy()
    
    # calculating response success rate per trial
    success_per_trial = response_success.groupby(['subject', 'trial']).mean()
    success_per_trial.rename(columns={'correct': 'trial_success_rate'}, inplace=True)
    
    success_per_trial = raw_data[['subject', 'trial']].merge(success_per_trial, how='left'
                                                             , left_on=['subject', 'trial'], right_index=True)
    
    bad_trials_mask = success_per_trial['trial_success_rate'] < threshold
    
    bad_trials = success_per_trial[bad_trials_mask].drop_duplicates(ignore_index=True)
    n_trials_filtered = bad_trials.shape[0]
    if n_trials_filtered > 0: # if there are any bad trials, print an explanatory message
        print(f"filter_bad_trials: {n_trials_filtered} bad trials were filtered (in terms of low success rate):")
        print(bad_trials.sort_values(by='trial_success_rate'))
    else:
        print(f"filter_bad_trials: No bad trials detected (in terms of low success rate).")
        
    return raw_data[ ~ bad_trials_mask]

def filter_slow_steps(raw_data, threshold):
    """ filtering out slow steps in terms of response time using IQR, according to the given threshold."""
    response_times = raw_data[['subject', 'step_num', 'rt']].copy()
    
    # calculating response time quantiles and IQR per subject
    quantiles_per_subject = response_times[['rt', 'subject']].groupby('subject').quantile([0.25, 0.75]).unstack()
    quantiles_per_subject.columns = ['q1', 'q3']
    quantiles_per_subject['iqr'] = quantiles_per_subject['q3'] - quantiles_per_subject['q1']
    
    response_times = response_times.merge(quantiles_per_subject, how='left', left_on='subject', right_index=True)

    # actually filtering the outlier steps
    response_times['outlier_grade'] = response_times.apply(get_outlier_grade, args=(['rt']), axis=1)
    step_outlier_mask = response_times['outlier_grade'] >= threshold
    
    slow_steps = response_times[step_outlier_mask].drop_duplicates(ignore_index=True)
    n_steps_filtered = slow_steps.shape[0]
    if n_steps_filtered > 0: # if there are any bad subjects, print an explanatory message
        print(f"filter_slow_steps: {n_steps_filtered} slow steps were filtered out.")
        
        # calculating slow steps rate per subject
        slow_steps_per_subject = slow_steps[['subject', 'step_num']].groupby('subject').nunique()
        total_steps_per_subject = response_times[['subject', 'step_num']].groupby('subject').nunique()
        slow_rate_per_subject = (slow_steps_per_subject / total_steps_per_subject * 100).round(2)
        
        slow_rate_per_subject.rename(columns={'step_num': 'slow steps rate (%)'}, inplace=True)
        slow_rate_per_subject.fillna(0, inplace=True)
        slow_rate_per_subject = slow_rate_per_subject.sort_values(by='slow steps rate (%)')

        print('Here is a summary of slow steps rate per subjects:', '\n    ', slow_rate_per_subject.T)
    else:
        print("filter_slow_steps: No slow steps detected.")
    
    return raw_data[ ~ step_outlier_mask]