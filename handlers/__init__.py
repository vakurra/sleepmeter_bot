import importlib
import pkgutil

from aiogram import Router


def get_routers(package_name=__name__):
    routers = []

    package = importlib.import_module(package_name)

    for module_info in pkgutil.walk_packages(
        package.__path__,
        package.__name__ + ".",
    ):
        module = importlib.import_module(module_info.name)

        for obj in vars(module).values():
            if isinstance(obj, Router):
                routers.append(obj)

    return routers