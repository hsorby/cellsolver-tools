import types

from xml.etree import ElementTree
from zipfile import ZipFile, BadZipfile

from cellsolvertools.generate_code import ModelGenerationError, return_generated_python_code


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
    except BadZipfile:
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


def import_code(code_string, name):
    # create blank module
    module = types.ModuleType(name)
    # populate the module with code
    exec(code_string, module.__dict__)
    return module


def get_parameters_from_model(model_file):
    try:
        python_code = return_generated_python_code(model_file)
    except ModelGenerationError:
        return {}

    m = import_code(python_code, 'generated_model_python_code')

    parameter_info = {}
    state_info = m.STATE_INFO
    for s in state_info:
        if s['component'] in parameter_info:
            parameter_info[s['component']][s['name']] = 'STATE'
        else:
            parameter_info[s['component']] = {s['name']: 'STATE'}

    variable_info = m.VARIABLE_INFO
    for v in variable_info:
        if v['component'] in parameter_info:
            parameter_info[v['component']][v['name']] = v['type'].name
        else:
            parameter_info[v['component']] = {v['name']: v['type'].name}

    return parameter_info
