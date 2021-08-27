import argparse
import os
import pickle
import sys

from cellsolver.main import apply_config
from cellsolver.plot import plot_solution, plot_sensitivity

from cellsolver.utilities import load_config


def process_arguments():
    parser = argparse.ArgumentParser(description="Solve ODE's described by libCellML generated Python output in a multi-threaded way.")
    parser.add_argument('--data-directory', required=True,
                        help='directory containing the output files')
    parser.add_argument('--config', default=None,
                        help='the JSON configuration file')
    parser.add_argument('--solution-index', default=None, type=int,
                        help='the index of the solution to use in the plot')
    parser.add_argument('--list-solutions', action='store_true',
                        help='instead of plotting list the available solutions')

    return parser


def main():
    parser = process_arguments()
    args = parser.parse_args()

    config = {}
    if args.config is not None:
        config.update(load_config(args.config))

    data_files = []
    for path, folders, files in os.walk(args.data_directory):
        for file in files:
            data_files.append(os.path.join(path, file))

    if len(data_files) == 0:
        sys.exit(-1)

    data_file = data_files[0]
    with open(data_file, 'rb') as fb:
        data = pickle.load(fb)

    available_solutions = []
    for entry in data['y_n_info']:
        available_solutions.append(f"{entry['component']}.{entry['name']}")

    if args.list_solutions:

        print('index  reference')
        print('-----  ---------')
        for index, entry in enumerate(available_solutions):
            print(f"{index:5d}  {entry}")
        return

    if args.solution_index is not None:
        active_config = {'plot_includes': [available_solutions[args.solution_index]]}
    else:
        active_config = config

    y_n_combined = []
    y_n_info = None
    x = None
    x_info = None
    title = None
    # if x is None:
    #     data_file = data_files[0]
    for data_file in data_files:
        with open(data_file, 'rb') as fb:
            data = pickle.load(fb)

        y_n_wanted, y_info_wanted = apply_config(active_config, data['y_n'], data['y_n_info'])
        y_n_combined.extend(y_n_wanted)
        if x is None:
            x = data['x']
        if x_info is None:
            x_info = data['x_info']
        if y_n_info is None:
            y_n_info = y_info_wanted[0]
        if title is None:
            title = data['title']

    # plot_solution(x, y_n_combined, x_info, y_n_info, 'bob')
    plot_sensitivity(x, y_n_combined, x_info, y_n_info, f'{title} - {y_n_info["component"]}.{y_n_info["name"]}')


if __name__ == '__main__':
    main()
