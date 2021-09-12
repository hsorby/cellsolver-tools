import argparse
import roadrunner
import os
import sys


def process_arguments():
    parser = argparse.ArgumentParser(description="Simulate an SBML model using roadrunner.")
    parser.add_argument('model', help='model to simulate')

    return parser


def main():
    parser = process_arguments()
    args = parser.parse_args()

    if not os.path.isfile(args.model):
        sys.exit(1)

    rr = roadrunner.RoadRunner(args.model)

    result = rr.simulate(0, 10, 2)

    print(result)


if __name__ == '__main__':
    main()
