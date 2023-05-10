import pandas as pd
from os import listdir
from os.path import isfile, join

trials_plans_path = r'C:\Users\97254\Desktop\Projects\MathThinkingLabDA\TrialsPlans'
trials_results_path = r'C:\Users\97254\Desktop\Projects\MathThinkingLabDA\Results'


def get_plan_trials(trials_plans_path: str):
    """ This function imports the uids of every trial plan, 
    in order to allow uids comparisons with actual results files.
    
    parameters:
        trials_plans_path: a path to a directory of csv files containing the original trails plans.

    return: a list in the following format: [(file_name, uids)]
    """
    
    # importing the file names from directory
    trials_plans = [f for f in listdir(trials_plans_path) if isfile(join(trials_plans_path, f))]
    
    # creating a dict of {plan_file_name: uids_list}
    plans_uids = []
    for plan_file_name in trails_plans:
        plan_path = trials_plans_path + f'\{plan_file_name}'
        plan = pd.read_csv(plan_path, usecols=['uid'])
        plan['uid'] = plan['uid'].astype(int) # making sure all uids are ints
        plan.dropna(inplace=True)
        plan.drop_duplicates(inplace=True)
        plans_uids.append((plan_file_name, plan['uid'].to_list()))
    
    return plans_uids


def find_actual_trials(trials_plans_path: str, trials_results_path: str, trials_results: list=[]):
    """ This function helps to determine which trail plan has been used for each trail.
    
    parameters:
        trials_plans_path: a path to a directory of csv files containing the original trails plans.
        trials_results_path: a path to a directory of csv files containing the actual trails results.
        trials_results: a subset of the csv file names, to check.
        
    return: a dictionary in the following format: {trail_results_file_name: trail_plans_file_name}
    """
    
    # importing the file names from directory
    print(f"searching for: {trials_results if trials_results else 'all'}")    
    if not trials_results: # if no specific results files are chosen
        trials_results = [f for f in listdir(trials_results_path) if isfile(join(trials_results_path, f))]
    
    # searching for the correct original plan for each results file
    actual_trials = {}
    plans_uids = get_plan_trials(trials_plans_path) # importing original plans' uids
    for res_file_name in trials_results:
        res_path = trials_results_path + f'\{res_file_name}'
        res = pd.read_csv(res_path, usecols=['uid'])
        res.dropna(inplace=True)
        res.drop_duplicates(inplace=True)
        res['uid'] = res['uid'].astype(int) # making sure all uids are ints
        res_uids = res['uid'].to_list()
        
        # iterating over all plan files to check for a match
        # found = True # a status bool, if not changes - we found the plan file
        curr_plan_uids = plans_uids.copy()
        for r_uid in res_uids:
            curr_plan_uids = [(p_name, p_uids) for p_name, p_uids in curr_plan_uids if p_uids != -1]
            curr_plan_uids = [(p_name, p_uids[p_uids.index(r_uid):]) if r_uid in p_uids else (-1, -1) for p_name, p_uids in curr_plan_uids]
        matched_plan_name = curr_plan_uids[0][0] if curr_plan_uids != [] else 'not found'
        actual_trials.update({res_file_name: matched_plan_name})

    return actual_trials