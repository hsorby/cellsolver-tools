"""
Using libroadrunner evaluate the initial values of an SBML model.

Prints out a JSON description of all the given models parameter
initial values.
"""
import argparse
import json
import roadrunner
import os
import sys


def process_arguments():
    parser = argparse.ArgumentParser(description="Simulate an SBML model using roadrunner.")
    parser.add_argument('model', help='model to simulate')

    return parser


def evaluate_parameter_initial_values(rr):

    executable_model = rr.getModel()
    parameter_values = executable_model.getGlobalParameterValues()
    initial_values = {}
    for p in range(executable_model.getNumGlobalParameters()):
        initial_values[executable_model.getGlobalParameterId(p)] = parameter_values[p]

    return initial_values


def load_model(sbml_model):
    return roadrunner.RoadRunner(sbml_model)


def evaluate_model(sbml_model):

    rr = load_model(sbml_model)
    return evaluate_parameter_initial_values(rr)


def main():
    parser = process_arguments()
    args = parser.parse_args()

    if not os.path.isfile(args.model):
        sys.exit(1)

    initial_values = evaluate_model(args.model)
    print(json.dumps(initial_values))


if __name__ == '__main__':
    main()
