import ast
import os


class FlaskToQuartTransformer(ast.NodeTransformer):
    def __init__(self):
        self.async_functions = set()

    def visit_Import(self, node, parent=None):
        for alias in node.names:
            if alias.name.startswith("flask"):
                alias.name = alias.name.replace("flask", "quart")
            elif alias.name == "psycopg2":
                alias.name = "database_adapter"
        return node

    def visit_ImportFrom(self, node, parent=None):
        if node.module.startswith("flask"):
            node.module = node.module.replace("flask", "quart")
        elif node.module.startswith("psycopg2"):
            node.module = node.module.replace("psycopg2", "database_adapter")
        return node

    def visit_Attribute(self, node, parent=None):
        if isinstance(node.value, ast.Name) and node.value.id == "g":
            return ast.copy_location(
                ast.Attribute(ast.Name("g", ast.Load()), node.attr, ast.Load()),
                node,
            )
        return node

    def visit_Assign(self, node, parent=None):
        functions_to_await = {"get_hotel_db", "reservations_tables", "charge_now"}

        if isinstance(node.value, ast.Call):
            if not isinstance(node.value, ast.Await) and (
                (
                    isinstance(node.value.func, ast.Name)
                    and node.value.func.id in functions_to_await
                )
                or (
                    isinstance(node.value.func, ast.Attribute)
                    and node.value.func.attr in functions_to_await
                )
            ):
                node.value = ast.Await(value=node.value)
        return self.generic_visit(node)

    def visit_FunctionDef(self, node, parent=None):
        self.async_functions.add(node.name)
        async_func = ast.AsyncFunctionDef(  # ty: ignore[no-matching-overload]
            name=node.name,
            args=node.args,
            body=[self.visit(i, node) for i in node.body],
            decorator_list=node.decorator_list,
            returns=node.returns,
        )
        return ast.copy_location(async_func, node)

    def visit_Call(self, node, parent=None):
        functions_to_await = {
            "get_hotel_db",
            "reservations_tables",
            "charge_now",
            "close",
        }

        if isinstance(node.func, ast.Name) and node.func.id == "Flask":
            node.func.id = "Quart"
        elif (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "psycopg2"
            and node.func.attr in {"execute", "fetchall", "fetchone", "close"}
        ):
            if not isinstance(parent, ast.Await):
                return ast.copy_location(ast.Await(value=node), node)
        elif (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in self.async_functions
        ):
            if isinstance(node.func.value, ast.Call):
                node.func.value = self.visit(node.func.value, node)
            if not isinstance(parent, ast.Await):
                return ast.copy_location(ast.Await(value=node), node)
        elif (
            isinstance(node.func, ast.Name)
            and node.func.id in self.async_functions
            or (
                # if the function is called directly
                (isinstance(node.func, ast.Name) and node.func.id in functions_to_await)
                or
                # if the function is a method
                (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr in functions_to_await
                )
            )
        ):
            if not isinstance(parent, ast.Await):
                return ast.copy_location(ast.Await(value=node), node)
        return node

    def visit(self, node, parent=None):
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        if visitor in {
            self.visit_Import,
            self.visit_ImportFrom,
            self.visit_Attribute,
            self.visit_Assign,
            self.visit_FunctionDef,
            self.visit_Call,
        }:
            return visitor(node, parent)
        else:
            return visitor(node)

    def generic_visit(self, node, parent=None):
        """Called if no explicit visitor function exists for a node."""
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self.visit(value, node)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self.visit(old_value, node)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node


def convert_directory_to_quart(src_dir, dest_dir):
    transformer = FlaskToQuartTransformer()

    for root, dirs, files in os.walk(src_dir):
        if ".git" in dirs:
            dirs.remove(".git")  # don't visit .git directories

        for file in files:
            src_file = os.path.join(root, file)

            if file.endswith(".py"):
                with open(src_file) as f:
                    source_code = f.read()

                tree = ast.parse(source_code)
                new_tree = transformer.visit(tree)
                new_source_code = ast.unparse(new_tree)

                write_mode = "w"  # write as text
            else:
                with open(src_file, "rb") as f:
                    new_source_code = f.read()

                write_mode = "wb"  # write as binary

            relative_dir = os.path.relpath(root, src_dir)
            dest_file = os.path.join(dest_dir, relative_dir, file)

            os.makedirs(os.path.dirname(dest_file), exist_ok=True)

            with open(dest_file, write_mode) as f:
                f.write(new_source_code)


convert_directory_to_quart("FLASK_PROJECT_ROOT", "NEW_PROJECT_QUART_ROOT")
