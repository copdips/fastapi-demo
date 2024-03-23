import importlib
import pkgutil
import types

from fastapi import APIRouter, FastAPI


def add_child_router(parent_router: APIRouter, child_router_module: types.ModuleType):
    parent_router.include_router(
        child_router_module.router,
        prefix=f"/{child_router_module.endpoint_name}",
        tags=[child_router_module.endpoint_name],
    )


def list_submodules(package):
    submodules = []
    for _, name, ispkg in pkgutil.iter_modules(
        package.__path__,
        package.__name__ + ".",
    ):
        if not ispkg:
            module = importlib.import_module(name)
            submodules.append(module)
    return submodules


def register_routers(app: FastAPI, routers_parent_module: types.ModuleType):
    routers_module = list_submodules(routers_parent_module)
    [
        add_child_router(routers_parent_module.router, router)
        for router in routers_module
    ]
    app.include_router(
        routers_parent_module.router,
        prefix=routers_parent_module.VERSION_PREFIX,
    )
