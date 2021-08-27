
Cell Solver Tools
=================

A collection of tools that work with Cell Solver.

Install
-------

Use 'pip' to install from the repository::

 pip install git+https://github.com/hsorby/cellsolver-tools.git@main

This will install the latest version available on the 'main' branch.

Usage
-----

Cell Solver Tools is a collection of scripts each with its own purpose.
Below are the usage instructions for each tool.

multi_processing_script
.......................

::

 usage: multi_processing_script.py [-h] [--trials TRIALS] [--workers WORKERS] [--cs-config CS_CONFIG] [--cs-ext-var CS_EXT_VAR] [--cs-model CS_MODEL]

 Solve ODE's described by libCellML generated Python output in a multi-process way.

 optional arguments:
   -h, --help            show this help message and exit
   --trials TRIALS       number of trials to run (default: 10)
   --workers WORKERS     number of workers to use (default: CPU count)
   --cs-config CS_CONFIG
                         the configuration for Cell Solver
   --cs-ext-var CS_EXT_VAR
                         the external variable functions module for the model
   --cs-model CS_MODEL   the libCellML generated model to solve

multi_trial_plot
................

::

 usage: multi_trial_plot.py [-h] --data-directory DATA_DIRECTORY [--config CONFIG] [--solution-index SOLUTION_INDEX] [--list-solutions]

 Solve ODE's described by libCellML generated Python output in a multi-threaded way.

 optional arguments:
   -h, --help            show this help message and exit
   --data-directory DATA_DIRECTORY
                         directory containing the output files
   --config CONFIG       the JSON configuration file
   --solution-index SOLUTION_INDEX
                         the index of the solution to use in the plot
   --list-solutions      instead of plotting list the available solutions
