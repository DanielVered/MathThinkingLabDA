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
    
# filtering out first loop in a program, first line in a loop

def drop_first_loop(raw_data):
    """ filtering out first loop within each program.
    """
    # note that 'step_id' is an id of each loop within a given program, ranging 1-9,
    # where the first loop is essentially a variable assignment.
    first_loop_filter = raw_data['step_id'] != 2
    raw_data = raw_data[first_loop_filter]
    
    n_rows_filtered = first_loop_filter.size - first_loop_filter.sum()
    print(f"-- drop_first_loop: {n_rows_filtered} rows were filtered out.")
    return raw_data

def drop_first_line(raw_data):    
    """ filtering out first line within each loop.
    """
    # note that 'loop_step' is an id of each step in the loop, ranging 0-len(loop).
    first_line_filter = raw_data['loop_step'] != 0
    raw_data = raw_data[first_line_filter]
    
    n_rows_filtered = first_line_filter.size - first_line_filter.sum()
    print(f"-- drop_first_line: {n_rows_filtered} rows were filtered out.")
    return raw_data

# filtering out the outliers

def is_outlier(x, x_q1, x_q3, x_iqr, threshold):
    """finding if a datapoint is an outlier using IQR, according to a given threshold."""
    return (x_q1 - x) / x_iqr >= threshold or (x - x_q3) / x_iqr >= threshold


def filter_trail_outliers(raw_data, threshold):
    """ filtering out outlier trials in terms of success rate within subject using IQR,
        according to the given threshold.
    """
    # filtering only necessary columns
    response_success = raw_data[['subject', 'trial', 'correct']].copy()
    
    # calculating response success rate per trial
    success_per_trial = response_success.groupby(['subject', 'trial']).mean()
    success_per_trial.rename(columns={'correct': 'trial_success_rate'}, inplace=True)
    
    # actually finding the trial outliers in terms of success rate within subject
    trial_success_q1, trial_success_q3 = success_per_trial['trial_success_rate'].quantile([0.25, 0.75])
    trial_success_iqr = trial_success_q1 - trial_success_q3
    
    success_per_trial = raw_data[['subject', 'trial']].merge(success_per_trial
                                                             , how='left', left_on=['subject', 'trial'], right_index=True)
    outlier_trials_mask = success_per_trial['trial_success_rate'].apply(is_outlier
                                                                        , args=(trial_success_q1, trial_success_q3
                                                                                , trial_success_iqr, threshold))
    
    n_rows_filtered = outlier_trials_mask.sum() 
    print(f"-- filter_trail_outliers: {n_rows_filtered} rows were filtered out.")
    return raw_data[ ~ outlier_trials_mask]

def filter_step_outliers(raw_data, threshold):
    """ filtering out outlier steps in terms of response time using IQR,
        according to the given threshold.
    """
    response_times = raw_data[['subject', 'step_num', 'rt']].copy()
    
    # calculating general response time quantiles
    g_rt_q1, g_rt_q3 = response_times['rt'].quantile([0.25, 0.75])
    g_rt_iqr = g_rt_q3 - g_rt_q1    
    
    # calculating response time quantiles and IQR per subject
    quantiles_per_subject = response_times[['rt', 'subject']].groupby('subject').quantile([0.25, 0.75]).unstack()
    quantiles_per_subject.columns = ['q1', 'q3']
    quantiles_per_subject['iqr'] = quantiles_per_subject['q3'] - quantiles_per_subject['q1']

    def is_subjective_outlier(step):
        """ finding if a step is an outlier in terms of response time within subject,
            using IQR. this function is used only for 'filter_step_outliers'.
        """
        rt = step.loc['rt']
        subject = step.loc['subject']
            
        subject_quantiles = quantiles_per_subject.loc[subject]
        q1, q3, iqr = subject_quantiles['q1'], subject_quantiles['q3'], subject_quantiles['iqr']
        return is_outlier(rt, q1, q3, iqr, threshold)

    # actually filtering the outlier steps
    step_outlier_mask = response_times.apply(is_subjective_outlier, axis=1)
    
    n_rows_filtered = step_outlier_mask.sum()
    print(f"-- filter_step_outliers: {n_rows_filtered} rows were filtered out.")
    return raw_data[ ~ step_outlier_mask]

    

###########################
##### actual cleaning #####
###########################

# raw_data = pd.read_excel(cleaning_config['raw_data_path'])

def clean_data(raw_data):
    drop_columns(raw_data, cleaning_config['unnecessary_columns'])
    convert_types(raw_data, cleaning_config['type_conversions'])
    raw_data = drop_first_loop(raw_data)
    raw_data = drop_first_line(raw_data)
    raw_data = filter_trail_outliers(raw_data, threshold=cleaning_config['filter_threshold'])
    raw_data = filter_step_outliers(raw_data, threshold=cleaning_config['filter_threshold'])
    
    raw_data.reset_index(inplace=True)
    return raw_data


if __name__ == '__main__':
    raw_data = pd.read_excel(cleaning_config['raw_data_path'])
    raw_data = clean_data(raw_data)