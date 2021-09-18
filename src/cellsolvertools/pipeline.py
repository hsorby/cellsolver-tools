import argparse
import json
import multiprocessing
import os
import shutil
import sys

from xml.etree import ElementTree
import zipfile

from zipfile import ZipFile

from cellsolvertools.define_parameter_uncertainties import create_model_from_config
from cellsolvertools.evaluate_sbml_model_initial_values import evaluate_model
from cellsolvertools.generate_code import generate_c_code
from cellsolvertools.simple_sundials_solver_manager import entry_point


def is_omex_file(filename):
    try:
        with ZipFile(filename) as omex_zip:
            info_list = omex_zip.infolist()
            for info in info_list:
                print(info)
    except FileNotFoundError:
        return False
    except IsADirectoryError:
        return False
    except zipfile.BadZipfile:
        return False

    return False


def is_cellml_file(filename):
    try:
        my_namespaces = dict([node for _, node in ElementTree.iterparse(filename, events=['start-ns'])])

        for ns in my_namespaces:
            if my_namespaces[ns] == 'http://www.cellml.org/cellml/2.0#':
                return True
    except IsADirectoryError:
        return False
    except ElementTree.ParseError:
        return False

    return False


def check_simulation_dir():
    if 'SIMULATION_DIR' not in os.environ:
        return False

    if not os.path.isdir(os.path.join(os.environ['SIMULATION_DIR'])):
        return False

    if not os.path.isfile(os.path.join(os.environ['SIMULATION_DIR'], 'simple-sundials-solver', 'CMakeLists.txt')):
        return False

    build_dir = os.path.join(os.environ['SIMULATION_DIR'], 'build-simple-sundials-solver', 'src')
    if os.path.isdir(build_dir):
        shutil.rmtree(os.path.join(os.environ['SIMULATION_DIR'], 'build-simple-sundials-solver'))

    os.makedirs(build_dir)

    return True


def is_valid_config(config):
    if 'uncertainties' in config and type(config['uncertainties']) != dict:
        return False

    if 'num_trials' not in config:
        return False

    if config['num_trials'] < 1:
        return False

    return True


def process_arguments():
    parser = argparse.ArgumentParser(description="Pipeline to perform an analysis of parameter sensitivity.")
    parser.add_argument('model', help='model to simulate, this can be either an OMEX archive or a CellML model file.  '
                                      'If the model parameter is a CellML model file then a config file is also required for sensitivity analysis.')
    parser.add_argument('--config',
                        help='the configuration for the model, not required if not doing sensivity analysis or the model input is an OMEX file.')
    parser.add_argument('--workers', default=multiprocessing.cpu_count(), type=int,
                        help='number of workers to use (default: CPU count)')

    return parser


def main():
    parser = process_arguments()
    args = parser.parse_args()
    print('Running pipeline ...')

    if not check_simulation_dir():
        sys.exit(1)

    try:
        with open(args.config) as f:
            config = json.load(f)

        if not is_valid_config(config):
            config = None
    except json.JSONDecodeError:
        config = None
    except TypeError:
        config = None
    except IsADirectoryError:
        config = None

    if is_omex_file(args.model):
        print('Handle OMEX archive.')
    elif is_cellml_file(args.model) and config is not None:
        print('Process CellML with config')
        code_generation_config = {}
        if 'uncertainties' in config:
            code_generation_config['external_variables'] = config['uncertainties']
        generate_c_code(args.model, os.path.join(os.environ['SIMULATION_DIR'], 'build-simple-sundials-solver', 'src'), code_generation_config)

        # Compile application
        build_dir = os.path.join(os.environ['SIMULATION_DIR'], 'build-simple-sundials-solver')
        src_dir = os.path.join(os.environ['SIMULATION_DIR'], 'simple-sundials-solver')
        config['simulation_dir'] = os.environ['SIMULATION_DIR']
        config['build_dir'] = build_dir
        config['src_dir'] = src_dir
        config['sundials_dir'] = os.environ['SIMULATION_SUNDIALS_DIR']
        config['application'] = os.path.join(build_dir, 'src', 'siss')
        config['workers'] = args.workers
        entry_point(config)
    else:
        sys.exit(2)


if __name__ == '__main__':
    main()
