import argparse
import json
import os
import sys

from sbmlutils.creator import CoreModel
from sbmlutils.factory import Parameter, InitialAssignment, ModelUnits
from sbmlutils.units import UNIT_hr, UNIT_KIND_MOLE, UNIT_KIND_LITRE, UNIT_m, UNIT_m2, UNIT_KIND_DIMENSIONLESS


def create_template_model():
    model_dict = {
        'mid': 'normal',
        'packages': ['distrib'],
        'model_units':
            ModelUnits(
                time=UNIT_hr, extent=UNIT_KIND_MOLE, substance=UNIT_KIND_MOLE,
                length=UNIT_m, area=UNIT_m2, volume=UNIT_KIND_LITRE),
        'parameters': [
        ],
        'assignments': [
        ]
    }

    return model_dict


def add_model_parameter(model, parameter_name, parameter_values):
    modified_name = parameter_name.replace('.', '__')
    model['parameters'].append(Parameter(modified_name, value=parameter_values["p1"], unit=UNIT_KIND_DIMENSIONLESS))
    model['assignments'].append(InitialAssignment(modified_name, f'{parameter_values["distribution"]}({parameter_values["p1"]}, {parameter_values["p2"]})'))


def process_arguments():
    parser = argparse.ArgumentParser(description="Define parameter uncertainties using SBML-distrib.")
    parser.add_argument('config', help='configuration for the parameters')

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

    model = create_template_model()
    for parameter in config:
        add_model_parameter(model, parameter, config[parameter])

    core_model = CoreModel.from_dict(model_dict=model)

    print(core_model.get_sbml())


if __name__ == '__main__':
    main()
