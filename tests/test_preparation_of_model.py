import os
import unittest

from cellsolvertools.generate_code import generate_c_code


class PreparationTestCase(unittest.TestCase):

    def test_model(self):
        base_directory = os.environ['SIMULATION_DIR']
        model_location = os.path.join(base_directory, 'models/ohara_rudy_cipa/ohara_rudy_cipa_v2_2017.cellml')
        output_location = os.path.join(base_directory, 'build-simple-sundials-solver-debug/src')
        generate_c_code(model_location, output_location=output_location)

        self.assertTrue(os.path.isfile(os.path.join(output_location, 'ohara_rudy_cipa_v1_2017.h')))
        self.assertTrue(os.path.isfile(os.path.join(output_location, 'ohara_rudy_cipa_v1_2017.c')))


if __name__ == '__main__':
    unittest.main()
