import argparse
import multiprocessing
import os
import subprocess

from concurrent.futures import ProcessPoolExecutor

here = os.path.dirname(os.path.abspath(__file__))


def run_simulation(output_file_name, model, external_variables_module, config):
    subprocess.run(["cellsolver", model,
                    "--output-file", output_file_name,
                    "--config", config,
                    "--ext-var", external_variables_module])


def process_arguments():
    parser = argparse.ArgumentParser(description="Solve ODE's described by libCellML generated Python output in a multi-process way.")
    parser.add_argument('--trials', default=10, type=int,
                        help='number of trials to run (default: 10)')
    parser.add_argument('--workers', default=multiprocessing.cpu_count(), type=int,
                        help='number of workers to use (default: CPU count)')
    parser.add_argument('--cs-config',
                        help='the configuration for Cell Solver')
    parser.add_argument('--cs-ext-var',
                        help='the external variable functions module for the model')
    parser.add_argument('--cs-model',
                        help='the libCellML generated model to solve')

    return parser


def main():
    parser = process_arguments()
    args = parser.parse_args()

    output_file_names = [os.path.join(here, 'dist', f'simulation_output_{i + 1:05d}.pickle') for i in range(args.trials)]
    with ProcessPoolExecutor(max_workers=args.workers) as executor:

        for output_file_name in output_file_names:
            executor.submit(run_simulation, output_file_name, args.cs_model, args.cs_ext_var, args.cs_config)


if __name__ == '__main__':
    main()
