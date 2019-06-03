import importlib

from pymoo.configuration import Configuration


def get_functions():
    from pymoo.util.nds.fast_non_dominated_sort import fast_non_dominated_sort
    from pymoo.decomposition.util import calc_distance_to_weights

    FUNCTIONS = {
        "fast_non_dominated_sort": {
            "python": fast_non_dominated_sort, "cython": "pymoo.cython.non_dominated_sorting"
        },
        "calc_distance_to_weights": {
            "python": calc_distance_to_weights, "cython": "pymoo.cython.decomposition"
        }
    }

    return FUNCTIONS


class FunctionLoader:
    # -------------------------------------------------
    # Singleton Pattern
    # -------------------------------------------------
    __instance = None

    @staticmethod
    def get_instance():
        if FunctionLoader.__instance is None:
            FunctionLoader.__instance = FunctionLoader()
        return FunctionLoader.__instance

    # -------------------------------------------------

    def __init__(self) -> None:
        super().__init__()
        self.is_compiled = is_compiled()

        if Configuration.show_compile_hint and not self.is_compiled:
            print("\nCompiled modules for significant speedup can not be used!")
            print("https://www.egr.msu.edu/coinlab/blankjul/pymoo/installation.html#installation")
            print("Disable this warning: Configuration.show_compile_hint = False\n")

    def load(self, func_name=None, _type="auto"):

        FUNCTIONS = get_functions()

        if _type == "auto":
            _type = "cython" if self.is_compiled else "python"

        if func_name not in FUNCTIONS:
            raise Exception("Function %s not found: %s" % (func_name, FUNCTIONS.keys()))

        func = FUNCTIONS[func_name]
        if _type not in func:
            raise Exception("Module not available in %s." % _type)
        func = func[_type]

        # either provide a function or a string to the module (used for cython)
        if not callable(func):
            module = importlib.import_module(func)
            func = getattr(module, func_name)

        return func


def load_function(func_name=None, _type="auto"):
    return FunctionLoader.get_instance().load(func_name, _type=_type)


def is_compiled():
    try:
        from pymoo.cython.info import info
        if info() == "yes":
            return True
        else:
            return False
    except:
        return False