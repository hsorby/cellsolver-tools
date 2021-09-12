import argparse
import json
import multiprocessing
import os
import subprocess
import sys

from concurrent.futures import ProcessPoolExecutor

here = os.path.dirname(os.path.abspath(__file__))


def run_simulation(output_file_name, model, external_variables_module, config):
    subprocess.run(["cellsolver", model,
                    "--output-file", output_file_name,
                    "--config", config,
                    "--ext-var", external_variables_module])


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
