import argparse
import json
import math
import os

# Take too long to load in forking process so try to delay it.
# import pandas as pd
# import plotly.graph_objects as go

from cellsolvertools.generate_code import ModelGenerationError, return_generated_python_code
from cellsolvertools.utilities import import_code


def process_arguments():
    parser = argparse.ArgumentParser(description="Investigate simulation output data.")
    parser.add_argument('--data-directory', required=True,
                        help='directory containing the output files')
    parser.add_argument('--config', required=True,
                        help='the JSON configuration file')
    parser.add_argument('--solution-index', default=None, type=int,
                        help='the index of the solution to use in the plot')
    parser.add_argument('--list-solutions', action='store_true',
                        help='instead of plotting list the available solutions')
    parser.add_argument('--model-file', required=True,
                        help='the CellML model file associated with the data in the data directory')
    parser.add_argument('--plot-traces', store_default=True,
                        help='plot individual traces.')

    return parser


def _load_files(filenames, cols):
    import pandas as pd
    """
    Load csv files one by one yielding the wanted columns.
    Only the first file keeps the first col, assumed to be time.
    Subsequent files only have cols[1:].
    :param filenames: csv filenames to read.
    :param cols: list of columns to keep.
    :return: yield a dataframe.
    """
    first = True
    for filename in filenames:
        yield pd.read_csv(
            filename,
            usecols=cols
        )
        if first:
            first = False
            cols.pop(0)


def _plot_traces(data):
    import plotly.graph_objects as go
    data.to_csv('full_data.csv')
    data.to_json('full_data.json')

    fig = go.Figure()
    names = data.columns
    for index, name in enumerate(names[1:]):
        fig.add_trace(go.Scatter(
            x=data['time'],
            y=data.iloc[:, index + 1],
            name=name
        ))

    fig.show()


def _plot_aggs(parameter_names, epochs, data):
    import plotly.graph_objects as go
    import pandas as pd

    no_time_df = data.drop('time', 1)
    no_time_df = no_time_df.assign(epochs=epochs)
    reformed_df = no_time_df.groupby('epochs').agg(['min', 'mean', 'max', "std"])
    print(reformed_df.columns)
    fig = go.Figure()
    for name in parameter_names:
        y_upper = reformed_df[name, 'mean'] + reformed_df[name, 'std']
        y_lower = reformed_df[name, 'mean'] - reformed_df[name, 'std']
        df = pd.concat([y_upper, y_lower[::-1]])
        df.to_csv('lower_upper.csv')
        # fig.add_trace(go.Scatter(
        #     x=data['time'],
        #     y=pd.concat([y_upper, y_lower[::-1]]),
        #     fill='toself',
        #     hoveron='points',
        #     name=name
        # ))
        fig.add_trace(go.Scatter(
            x=data['time'],
            y=reformed_df[name, 'mean'],
            hoveron='points',
            name=f"{name} - mean"
        ))
        min_ = reformed_df[name, 'min']
        max_ = reformed_df[name, 'max']
        fig.add_trace(go.Scatter(
            x=data['time'],
            y=pd.concat([max_, min_[::-1]]),
            hoveron='points',
            fill='toself',
            name=f"{name} - range"
        ))
        # fig.add_trace(go.Scatter(
        #     x=data['time'],
        #     y=reformed_df[name, 'max'],
        #     hoveron='points',
        #     name=f"{name} - max"
        # ))

    fig.show()


def parameter_list(model_file):
    try:
        python_code = return_generated_python_code(model_file)
    except ModelGenerationError:
        return {}

    m = import_code(python_code, 'generated_model_python_code')

    state_info = m.STATE_INFO
    variable_info = m.VARIABLE_INFO

    return [*state_info, *variable_info]


def extract_result_for_config(model_file, config, data_directory):
    import pandas as pd

    parameters = parameter_list(model_file)

    # Auto include time.
    parameter_indices = [0]
    parameter_names = ['time']
    for c in config:
        parts = c['id'].split('.')

        parameter_index = next((index for index, x in enumerate(parameters) if x['name'] == parts[1] and x['component'] == parts[0]), None)

        parameter_index += 1
        parameter_names.append(c['id'])
        parameter_indices.append(parameter_index)

    data_files = [os.path.join(data_directory, f) for f in os.listdir(data_directory)]

    # data_files_count = len(data_files)
    data = pd.concat(_load_files(data_files, parameter_indices), axis=1)
    column_headers = [parameter_names[0]]
    fill = math.floor(math.log10(len(parameter_names[1:] * (data.shape[1] - 1)))) + 1
    headers = [f"{name} #{str(trial + 1).zfill(fill)}" for trial in range(data.shape[1] - 1) for name in parameter_names[1:]]
    # parameter_names[1:] * (data.shape[1] - 1)
    column_headers.extend(headers)
    data.columns = column_headers

    return data


def main():
    parser = process_arguments()
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    data = extract_result_for_config(args.model_file, config, args.data_directory)

    # _plot_aggs(parameter_names, epochs, data)
    if args.plot_traces:
        _plot_traces(data)


if __name__ == '__main__':
    main()
