# import matplotlib.pyplot as graph
import unittest
from statistics import mean, stdev

from cellsolvertools.define_parameter_uncertainties import create_model_from_config
from cellsolvertools.evaluate_sbml_model_initial_values import evaluate_parameter_initial_values, load_model

parameter_normal = {
    "dimensions.l": {"distribution": "normal", "p1": 6, "p2": 0.5},
    "dimensions.r": {"distribution": "normal", "p1": 2, "p2": 3}
}


class SamplingTestCase(unittest.TestCase):

    def test_normal(self):
        xml = create_model_from_config(parameter_normal)
        rr = load_model(xml)
        param_1 = []
        param_2 = []
        for _ in range(10000):
            initial_values = evaluate_parameter_initial_values(rr)
            param_1.append(initial_values['dimensions__l'])
            param_2.append(initial_values['dimensions__r'])
            rr.resetToOrigin()

        self.assertAlmostEqual(6, mean(param_1), 1)
        self.assertAlmostEqual(0.5, stdev(param_1), 1)
        self.assertAlmostEqual(2, mean(param_2), 1)
        self.assertAlmostEqual(3, stdev(param_2), 1)
        # graph.subplot(2, 1, 1)
        # graph.hist(param_1, 50)
        # graph.subplot(2, 1, 2)
        # graph.hist(param_2, 50)
        # graph.show()


if __name__ == '__main__':
    unittest.main()
