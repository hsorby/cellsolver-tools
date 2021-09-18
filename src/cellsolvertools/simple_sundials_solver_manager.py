import argparse
import json
import multiprocessing
import os
import subprocess
import sys

from concurrent.futures import ProcessPoolExecutor

from cellsolvertools.define_parameter_uncertainties import create_model_from_config
from cellsolvertools.evaluate_sbml_model_initial_values import evaluate_model

here = os.path.dirname(os.path.abspath(__file__))


def run_simulation(application, solver_config_file, output_file_name, initial_values):
    stringed_initial_values = {}
    for initial_value in initial_values:
        stringed_initial_values[initial_value] = str(initial_values[initial_value])
    env = {
        **os.environ,
        **stringed_initial_values
    }
    subprocess.run([application, solver_config_file, output_file_name], env=env)


def build_simulation_code(build_dir, src_dir, sundials_dir, external_variables):

    subprocess.run(['cmake', f'-DSUNDIALS_DIR={sundials_dir}', '-DSTORE_FILE=TRUE', f'-DEXTERNAL_VARIABLES={"TRUE" if external_variables else "FALSE"}', src_dir],
                   cwd=build_dir)
    subprocess.run(['make', '-j'], cwd=build_dir)


def entry_point(config):

    have_external_variables = 'uncertainties' in config
    application = config['application']

    build_simulation_code(config['build_dir'], config['src_dir'], config['sundials_dir'], have_external_variables)
    simulation_dir = config['simulation_dir']
    output_file_names = [os.path.join(simulation_dir, 'output', f'simulation_output_{i + 1:05d}.csv') for i in range(config['num_trials'])]
    sbml = None
    if have_external_variables:
        sbml = create_model_from_config(config['uncertainties'])
    solver_config = {
        "MaximumNumberOfSteps": 500,
        "RelativeTolerance": 1e-07,
        "AbsoluteTolerance": 1e-07,
        "IntegrationMethod": "BDF",
        "IterationType": "Newton",
        "InterpolateSolution": True,
        "LinearSolver": "Dense",
        "MaximumStep": 0.1
    }

    solver_config_file = os.path.join(simulation_dir, 'solver-config.json')
    if not os.path.isfile(solver_config_file):
        with open(solver_config_file, 'w') as f:
            f.write(json.dumps(solver_config))
    # external_variables = list(initial_values.keys())

    initial_values = {}
    with ProcessPoolExecutor(max_workers=config['workers']) as executor:

        for output_file_name in output_file_names:
            if have_external_variables:
                initial_values = evaluate_model(sbml)
            executor.submit(run_simulation, application, solver_config_file, output_file_name, initial_values)


def process_arguments():
    parser = argparse.ArgumentParser(description="Solve ODE's described by libCellML generated C++ output in a multi-process way.")
    parser.add_argument('--trials', default=10, type=int,
                        help='number of trials to run (default: 10)')
    parser.add_argument('--workers', default=multiprocessing.cpu_count(), type=int,
                        help='number of workers to use (default: CPU count)')
    parser.add_argument('--config', required=True,
                        help='configuration for the solver')

    return parser


def main():
    parser = process_arguments()
    args = parser.parse_args()

    if not os.path.isfile(args.config):
        sys.exit(1)

    try:
        with open(args.config) as f:
            config = json.load(f)
    except json.JSONDecodeError:
        sys.exit(2)

    print(config)

    # output_file_names = [os.path.join(here, 'dist', f'simulation_output_{i + 1:05d}.pickle') for i in range(args.trials)]
    # with ProcessPoolExecutor(max_workers=args.workers) as executor:
    #
    #     for output_file_name in output_file_names:
    #         executor.submit(run_simulation, output_file_name, args.cs_model, args.cs_ext_var, args.cs_config)


if __name__ == '__main__':
    main()
