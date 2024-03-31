import os
import unittest

from main import CellularAutomata


class OnStepTestCase(unittest.TestCase):
    """ Test case for on_step method. """

    def test_invalid_state_2(self):
        """ Attempt to update CA state which has invalid value types """

        ca = CellularAutomata()
        ca.field = [
            ["h", "e", "l"],
            ["l", "o", "!"],
            ["!", "!", "!"]
        ]
        with self.assertRaises(TypeError):
            ca.on_step()

    def test_field_5_by_5(self):
        """ Test state update on 5x5 field """

        ca = CellularAutomata()
        ca.params = CellularAutomata.Params(field_size=5)
        ca.field = [
            [False, False, False, False, False],
            [False, False, True, False, False],
            [False, False, False, True, False],
            [False, True, True, True, False],
            [False, False, False, False, False]
        ]
        ca.on_step()
        assert ca.field == [
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, True, False, True, False],
            [False, False, True, True, False],
            [False, False, True, False, False]
        ]


class SetParamsTestCase(unittest.TestCase):
    """ Test case for set_params method. """

    def test_invalid_params_1(self):
        """ Attempt to update set parameters with negative values """

        ca = CellularAutomata()
        with self.assertRaises(ValueError):
            ca.set_params(-1, [-1, -2], [-3, -4])

    def test_invalid_params_2(self):
        """ Attempt to update set parameters with values of inappropriate type """

        ca = CellularAutomata()
        with self.assertRaises(TypeError):
            ca.set_params("size", "param", "param")

    def test_set_params(self):
        """ Test set params """

        grid_size = 10
        birth_param = [3, 4]
        survive_param = [5, 6, 7]

        ca = CellularAutomata()
        ca.set_params(grid_size, birth_param, survive_param)

        assert grid_size == ca.params.field_size
        assert birth_param == ca.params.birth_param
        assert survive_param == ca.params.survive_param


class OnSaveTestCase(unittest.TestCase):
    """ Test case for on_save method. """

    @classmethod
    def tearDownClass(cls):
        """ TearDown for created state file """

        path = './test_resources/saved_state.txt'
        if os.path.exists(path):
            os.remove(path)

    def test_invalid_path(self):
        """ Attempt to save file to non-existing folder """

        ca = CellularAutomata()
        with self.assertRaises(FileNotFoundError):
            ca.on_save("./non-existing-folder/state.txt")

    def test_on_save(self):
        """ Test saving state to file """

        path = './test_resources/saved_state.txt'
        ca = CellularAutomata()
        ca.on_save(path)

        assert os.path.exists(path)


class OnLoadTestCase(unittest.TestCase):
    """ Test case for on_load method. """

    def test_invalid_path(self):
        """ Attempt to save file to non-existing folder """

        ca = CellularAutomata()
        with self.assertRaises(FileNotFoundError):
            ca.on_load("./non-existing-state.txt")

    def test_on_load(self):
        """ Test saving state to file """

        path = './test_resources/state_to_load.txt'
        ca = CellularAutomata()
        ca.on_load(path)
        assert ca.field == [
            [1, 0, 0, 0, 1],
            [0, 1, 1, 1, 0],
            [0, 1, 0, 1, 0],
            [0, 1, 1, 1, 0],
            [1, 0, 0, 0, 1]
        ]

class OnResetTestCase(unittest.TestCase):
    """ Test case for on_reset method. """

    def test_on_reset(self):
        """ Test resetting state to default """

        ca = CellularAutomata()
        ca.params = CellularAutomata.Params(field_size=5)
        ca.field = [
            [False, False, False, False, False],
            [False, False, True, False, False],
            [False, False, False, True, False],
            [False, True, True, True, False],
            [False, False, False, False, False]
        ]
        ca.on_reset()
        assert ca.field == [
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False],
            [False, False, False, False, False]
        ]

class OnSwitchModeTestCase(unittest.TestCase):
    """ Test case for on_switch_mode method. """

    def test_switch_to_auto(self):
        """ Test switching evolution mode from manual to auto """

        ca = CellularAutomata()
        ca.moving = False
        ca.on_switch_mode()
        assert ca.moving

    def test_switch_to_manual(self):
        """ Test switching evolution mode from auto to manual """

        ca = CellularAutomata()
        ca.moving = True
        ca.on_switch_mode()
        assert not ca.moving


class OnFasterTestCase(unittest.TestCase):
    """ Test case for on_faster method. """

    def test_on_faster(self):
        """ Test incrementing speed of evolution """
        eps = 10e-3

        ca = CellularAutomata()
        assert abs(ca.update_rate - 0.5) < eps
        ca.on_faster()
        assert abs(ca.update_rate - 0.45) < eps

    def test_on_faster_bound(self):
        """ Test incrementing speed of evolution limit """

        eps = 10e-3

        ca = CellularAutomata()
        assert abs(ca.update_rate - 0.5) < eps

        for _ in range(100):
            ca.on_faster()
        assert abs(ca.update_rate - 0.05) < eps


class OnSlowerTestCase(unittest.TestCase):
    """ Test case for on_slower method. """

    def test_on_slower(self):
        """ Test decrementing speed of evolution """
        eps = 10e-3

        ca = CellularAutomata()
        assert abs(ca.update_rate - 0.5) < eps
        ca.on_slower()
        assert abs(ca.update_rate - 0.55) < eps

    def test_on_faster_bound(self):
        """ Test decrementing speed of evolution limit """

        eps = 10e-3

        ca = CellularAutomata()
        assert abs(ca.update_rate - 0.5) < eps

        for _ in range(100):
            ca.on_slower()
        assert abs(ca.update_rate - 1) < eps


if __name__ == '__main__':
    unittest.main()