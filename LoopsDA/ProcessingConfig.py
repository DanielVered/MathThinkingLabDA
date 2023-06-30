cleaning_config = {
    'raw_data_path': r'Results\FinalResultsRaw.xlsx'
    , 'unnecessary_columns': ['text2', 'step', 'variables', 'var_mapping'
                              ,'updated_var', 'updated_var_name', 'same_as_prev_loop_type']
    , 'type_conversions': {
        int: ['rt', 'loop_step']
        , bool: ['response_needed', 'is_loop', 'loop_type_switch', 'correct']
    }
    , 'filter_threshold': 2.25 # iqr_grade limit for outliers detection
    , 'trials_success_rate_threshold': 0.5
    , 'results_path': r'Results/CleanedData'
}

analysis_config = {
    
}