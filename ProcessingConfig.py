cleaning_config = {
    'raw_data_path': r'Results\FinalResultsRaw.xlsx'
    , 'unnecessary_columns': ['text2', 'step', 'variables']
    , 'type_conversions': {
        'int': ['rt', 'loop_step']
        , 'bool': ['response_needed', 'is_loop', 'loop_type_switch', 'correct', 'same_as_prev_loop_type']
    }
}