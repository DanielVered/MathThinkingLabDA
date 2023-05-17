cleaning_config = {
    'raw_data_path': r'Results\FinalResultsRaw.xlsx'
    , 'unnecessary_columns': ['text2', 'step', 'variables', 'updated_var', 'updated_var_name']
    , 'type_conversions': {
        'int': ['rt', 'loop_step']
        , 'bool': ['response_needed', 'is_loop', 'loop_type_switch', 'correct', 'same_as_prev_loop_type']
    }
    , 'filter_threshold': 2.25 # iqr_grade limit for outliers detection
}