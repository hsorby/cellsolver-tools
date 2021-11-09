import os


def construct_application_config(simulation_dir, sundials_cmake_config_dir):
    build_dir = os.path.join(simulation_dir, 'build-simple-sundials-solver')
    src_dir = os.path.join(simulation_dir, 'simple-sundials-solver')

    return {'simulation_dir': simulation_dir, 'build_dir': build_dir, 'src_dir': src_dir, 'sundials_dir': sundials_cmake_config_dir,
            'executable': os.path.join(build_dir, 'src', 'siss')}
