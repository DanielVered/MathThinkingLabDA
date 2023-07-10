cleaning_config = {
    'raw_data_path': r'Results\FinalResultsRaw.xlsx'
    , 'unnecessary_columns': ['text2', 'step', 'variables', 'var_mapping'
                              ,'updated_var', 'updated_var_name', 'same_as_prev_loop_type']
    , 'type_conversions': {
        int: ['rt', 'loop_step']
        , bool: ['response_needed', 'is_loop', 'loop_type_switch', 'correct']
    }
    , 'filter_threshold': 3 # iqr_grade limit for outliers detection
    , 'trials_success_rate_threshold': 0.5
    , 'results_path': r'Results/CleanedData'
}

analysis_config = {
    'is_prev_correct_cols': { # col names for 'is_prev_correct'
        'subject': 'subject'
        , 'session': 'trial_set'
        , 'step': 'step_num'
        , 'correct': 'correct'
        , 'loop_step': 'loop_step'
        , 'step_type': 'step_type'
    }
    , 'get_arithmetics_cols':{
        'loop_lines': 'n_loop_lines'
        , 'loop_step': 'loop_step'
        , 'text': 'text1'
        
    }
    , 'participant_ids': '../../msa-1/scripts/loops1/exp1_data/results/raw/Participant IDs.xlsx'
}

