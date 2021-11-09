"""
Encode parameter uncertainties in an SBML-distrib way.

Taking a JSON description of a distribution enocde this information
into an SBML model using the SBML distribution extension.

The JSON description is defined by a parameter name as the key for
a dictionary with keys ['distribution', 'p1', 'p2', 'p3', 'p4'].
Only the parameters required for the named distribution are required.

Example JSON description:

  {
    "dimensions.l": {"distribution": "normal", "p1": 6, "p2": 0.5},
    "dimensions.r": {"distribution": "normal", "p1": 2, "p2": 3}
  }

"""
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


def _sort_parameter_values_key(item):
    return item[0]


def add_model_parameter(model, parameter_name, parameter_values):
    modified_name = parameter_name.replace('.', '__')
    model['parameters'].append(Parameter(modified_name, value=parameter_values["p1"], unit=UNIT_KIND_DIMENSIONLESS))
    values = [(k, v) for k, v in parameter_values.items() if k.startswith('p')]
    sorted_values = sorted(values, key=_sort_parameter_values_key)
    parameters = ', '.join([str(v[1]) for v in sorted_values])
    model['assignments'].append(InitialAssignment(modified_name, f'{parameter_values["distribution"]}({parameters})'))


def process_arguments():
    parser = argparse.ArgumentParser(description="Define parameter uncertainties using SBML-distrib.")
    parser.add_argument('config', help='configuration for the parameters')

    return parser


def create_model_from_config(config):
    model = create_template_model()
    for parameter in config:
        add_model_parameter(model, parameter, config[parameter])

    core_model = CoreModel.from_dict(model_dict=model)

    return core_model.get_sbml()


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

    sbml_xml_model = create_model_from_config(config)
    print(sbml_xml_model)


if __name__ == '__main__':
    main()
