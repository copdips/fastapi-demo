import importlib
import pkgutil
import types

from fastapi import APIRouter, FastAPI


def register_domain_based_routers(app: FastAPI, app_root_module: types.ModuleType):
    """used by domain based layout.
    Iterate all app_xxx submodules in app root module,
    if found routes.py file, add it to app router.
    """
    for file_finder, sub_mod_name, _ in pkgutil.iter_modules(app_root_module.__path__):
        if sub_mod_name.startswith("app_"):
            for _, sub_sub_mod_name, _ in pkgutil.iter_modules(
                [f"{file_finder.path}/{sub_mod_name}"]
            ):
                if sub_sub_mod_name.startswith("routes_"):
                    route_namespace_name = sub_mod_name.removeprefix("app_")
                    route_version = sub_sub_mod_name.split("_")[-1]
                    routes_mod = importlib.import_module(
                        f"app_domain_based.{sub_mod_name}.{sub_sub_mod_name}"
                    )
                    app.include_router(
                        routes_mod.router,  # type: ignore
                        prefix=f"/{route_version}/{route_namespace_name}s",
                        tags=[route_namespace_name],
                    )
