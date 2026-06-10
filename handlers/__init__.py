import importlib
import pkgutil

from aiogram import Router

# Получение всех роутеров
def get_routers():

    routers = []

    for module_info in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f"{__name__}.{module_info.name}")

        for obj in vars(module).values():
            if isinstance(obj, Router):
                routers.append(obj)

    return routers