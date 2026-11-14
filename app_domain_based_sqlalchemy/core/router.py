import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
                [f"{module_finder.path}/{sub_mod_name}"]  # ty: ignore[missing-attribute]
            ):
                if sub_sub_mod_name.startswith("routes_"):
                    route_namespace_name = sub_mod_name.removeprefix("app_")
                    route_version = sub_sub_mod_name.split("_")[-1]
                    routes_mod = importlib.import_module(
                        f"app_domain_based_sqlalchemy.{sub_mod_name}.{sub_sub_mod_name}"
                    )
                    # endpoint_name lets a module opt out of the pluralized
                    # module name, e.g. app_health -> /v1/health, not /v1/healths.
                    endpoint_name = getattr(
                        routes_mod,
                        "endpoint_name",
                        f"{route_namespace_name}s",
                    )
                    app.include_router(
                        routes_mod.router,
                        prefix=f"/{route_version}/{endpoint_name}",
                        tags=[route_namespace_name],
                    )
