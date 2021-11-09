import argparse
import json
import multiprocessing
import os
import subprocess
import sys

from concurrent.futures import ProcessPoolExecutor

from cellsolvertools.common import construct_application_config
from cellsolvertools.define_parameter_uncertainties import create_model_from_config
from cellsolvertools.evaluate_sbml_model_initial_values import evaluate_model

here = os.path.dirname(os.path.abspath(__file__))


def run_simulation(application, solver_config_file, simulation_config_file, output_file_name, initial_values):
    stringed_initial_values = {}
    for initial_value in initial_values:
        stringed_initial_values[initial_value] = str(initial_values[initial_value])
    env = {
        **os.environ,
        **stringed_initial_values
    }

    subprocess.run([application, solver_config_file, simulation_config_file, output_file_name], env=env)


def build_simulation_code(build_dir, src_dir, sundials_dir, external_variables):
    subprocess.run(['cmake', f'-DSUNDIALS_DIR={sundials_dir}', '-DSTORE_FILE=TRUE', f'-DEXTERNAL_VARIABLES={"TRUE" if external_variables else "FALSE"}', src_dir],
                   cwd=build_dir)
    subprocess.run(['make', '-j'], cwd=build_dir)


def entry_point(config):
    have_external_variables = 'uncertainties' in config
    application_config = config['application']

    build_simulation_code(application_config['build_dir'], application_config['src_dir'], application_config['sundials_dir'], have_external_variables)
    simulation_dir = application_config['simulation_dir']
    output_file_names = [os.path.join(simulation_dir, 'output', f'simulation_output_{i + 1:05d}.csv') for i in range(config['num_trials'])]
    sbml = None
    if have_external_variables:
        sbml = create_model_from_config(config['uncertainties'])

    if 'solver' not in config:
        config['solver'] = {
            "MaximumNumberOfSteps": 500,
            "RelativeTolerance": 1e-07,
            "AbsoluteTolerance": 1e-07,
            "IntegrationMethod": "BDF",
            "IterationType": "Newton",
            "InterpolateSolution": True,
            "LinearSolver": "Dense",
            "MaximumStep": 0.1
        }
    if 'simulation' not in config:
        config['simulation'] = {
            "StartingPoint": 0.0,
            "EndingPoint": 10000.0,
            "PointInterval": 1.0,
        }

    solver_config_file = os.path.join(simulation_dir, 'solver-config.json')
    with open(solver_config_file, 'w') as f:
        f.write(json.dumps(config['solver']))
    simulation_config_file = os.path.join(simulation_dir, 'simulation-config.json')
    with open(simulation_config_file, 'w') as f:
        f.write(json.dumps(config['simulation']))

    initial_values = {}
    with ProcessPoolExecutor(max_workers=config['workers']) as executor:

        for output_file_name in output_file_names:
            if have_external_variables:
                initial_values = evaluate_model(sbml)
            executor.submit(run_simulation, application_config['executable'], solver_config_file, simulation_config_file, output_file_name, initial_values)


def _do_not_have(arg):
    args = sys.argv[:]
    command_line = '_'.join(args)
    return arg not in command_line


def process_arguments():
    parser = argparse.ArgumentParser(description="Solve ODE's described by libCellML generated C++ output in a multi-process way.")
    parser.add_argument('--trials', default=10, type=int,
                        help='number of trials to run (default: 10)')
    parser.add_argument('--workers', default=multiprocessing.cpu_count(), type=int,
                        help='number of workers to use (default: CPU count)')
    parser.add_argument('--solver-config', required=_do_not_have('--simulation-config'),
                        help='configuration for the solver')
    parser.add_argument('--simulation-config', required=_do_not_have('--solver-config'),
                        help='configuration for the whole simulation')

    return parser


def _load_config(config_file):
    try:
        with open(config_file) as f:
            config = json.load(f)
    except json.JSONDecodeError:
        sys.exit(1)

    return config


def main():
    parser = process_arguments()
    args = parser.parse_args()

    if args.solver_config:
        config = _load_config(args.solver_config)
        config['application'] = construct_application_config(os.environ['SIMULATION_DIR'], os.environ['SIMULATION_SUNDIALS_DIR'])
        config['num_trials'] = args.trials
        config['worker'] = args.workers
    else:
        config = _load_config(args.simulation_config)

    entry_point(config)


if __name__ == '__main__':
    main()
