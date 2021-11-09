import os

import libcellml
from libcellml import Parser, Validator, GeneratorProfile, Generator, Analyser


class ModelGenerationError(Exception):
    pass


class ModelParseError(ModelGenerationError):
    pass


ModelValidationError = ModelParseError
ModelAnalysisError = ModelParseError


def return_generated_python_code(model_location):
    p = Parser()

    with open(model_location) as f:
        contents = f.read()

    m = p.parseModel(contents)

    if p.errorCount() > 0:
        raise ModelParseError(f'Parsed model has {p.errorCount()} error(s).')

    val = Validator()
    val.validateModel(m)

    if val.errorCount() > 0:
        raise ModelValidationError(f'Validated model has {val.errorCount()} error(s).')

    profile = GeneratorProfile(GeneratorProfile.Profile.PYTHON)

    g = Generator()
    g.setProfile(profile)

    a = Analyser()
    a.analyseModel(m)

    if a.errorCount() > 0:
        raise ModelAnalysisError(f'Model analysis came back with {a.errorCount()} error(s).')

    am = a.model()
    g.setModel(am)

    return g.implementationCode()


def generate_c_code(model_location, output_location, config=None):
    p = Parser()

    with open(model_location) as f:
        contents = f.read()

    m = p.parseModel(contents)

    if p.errorCount() > 0:
        raise ModelParseError(f'Parsed model has {p.errorCount()} error(s).')

    val = Validator()
    val.validateModel(m)

    if val.errorCount() > 0:
        raise ModelValidationError(f'Validated model has {val.errorCount()} error(s).')

    profile = GeneratorProfile(GeneratorProfile.Profile.C)
    header_filename = f'{m.name()}.h'
    profile.setInterfaceFileNameString(header_filename)

    g = Generator()
    g.setProfile(profile)

    a = Analyser()

    if config is not None and 'external_variables' in config:
        for ext_variable in config['external_variables']:
            component_name, variable_name = ext_variable.split('.')
            v = m.component(component_name).variable(variable_name)
            ev = libcellml.AnalyserExternalVariable(v)
            a.addExternalVariable(ev)
            # am.

    a.analyseModel(m)

    if a.errorCount() > 0:
        raise ModelAnalysisError(f'Model analysis came back with {a.errorCount()} error(s).')

    am = a.model()

    external_variable_info = []
    if config is not None and 'external_variables' in config:
        for ext_variable in config['external_variables']:
            component_name, variable_name = ext_variable.split('.')
            avs = am.variables()
            for av in avs:
                v = av.variable()
                if v.name() == variable_name and v.parent().name() == component_name:
                    external_variable_info.append({
                        'index': av.index(),
                        'name': variable_name,
                        'component_name': component_name
                    })

        generate_external_variable_c_code(external_variable_info, output_location)

    generate_cmake_code(m.name(), output_location, len(external_variable_info) > 0)

    g.setModel(am)

    with open(os.path.join(output_location, header_filename), 'w') as f:
        f.write(g.interfaceCode())
    with open(os.path.join(output_location, f'{m.name()}.c'), 'w') as f:
        f.write(g.implementationCode())


def generate_external_variable_c_code(external_variable_info, output_location):
    interface_code = """  
#pragma once

#include <stddef.h>

double computeExternalVariable(double voi, double *states, double *variables, size_t index);
"""
    with open(os.path.join(output_location, 'external_variables.h'), 'w') as f:
        f.write(interface_code)

    if_statement = ''
    for info in external_variable_info:
        index = info['index']
        value = f"{info['component_name']}__{info['name']}"

        if_statement += f'  if (index == {index}) return atof(getenv("{value}"));\n'

    implementation_code = f"""
#include "external_variables.h"

#include <stdlib.h>

double computeExternalVariable(double voi, double *states, double *variables, size_t index)
{{
  
{if_statement}
  return 0.0;
}}
"""
    with open(os.path.join(output_location, 'external_variables.c'), 'w') as f:
        f.write(implementation_code)


def generate_cmake_code(model_name, output_location, external_variables=False):
    external_variables_files = ''
    if external_variables:
        external_variables_files = """
  ${CMAKE_CURRENT_BINARY_DIR}/external_variables.h
  ${CMAKE_CURRENT_BINARY_DIR}/external_variables.c
"""
    model_cmake = f"""
set(HEADER_FILENAME
  {model_name}.h
)
set(MODEL_FILES
  ${{CMAKE_CURRENT_BINARY_DIR}}/{model_name}.h
  ${{CMAKE_CURRENT_BINARY_DIR}}/{model_name}.c
{external_variables_files})
"""
    with open(os.path.join(output_location, 'model_files.cmake'), 'w') as f:
        f.write(model_cmake)
