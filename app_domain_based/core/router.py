import importlib
import pkgutil
import types

from fastapi import FastAPI


def register_domain_based_routers(app: FastAPI, app_root_module: types.ModuleType):
    """used by domain based layout.
    Iterate all app_xxx submodules in app root module,
    if found routes.py file, add it to app router.
    """
    for module_finder, sub_mod_name, _ispkg in pkgutil.iter_modules(
        app_root_module.__path__
    ):
        if sub_mod_name.startswith("app_"):
            for _module_finder, sub_sub_mod_name, _ispkg in pkgutil.iter_modules(
                [f"{module_finder.path}/{sub_mod_name}"]  # ty: ignore[unresolved-attribute]
            ):
                if sub_sub_mod_name.startswith("routes_"):
                    route_namespace_name = sub_mod_name.removeprefix("app_")
                    route_version = sub_sub_mod_name.split("_")[-1]
                    routes_mod = importlib.import_module(
                        f"app_domain_based.{sub_mod_name}.{sub_sub_mod_name}"
                    )
                    app.include_router(
                        routes_mod.router,  # ty: ignore[unresolved-attribute]
                        prefix=f"/{route_version}/{route_namespace_name}s",
                        tags=[route_namespace_name],
                    )
