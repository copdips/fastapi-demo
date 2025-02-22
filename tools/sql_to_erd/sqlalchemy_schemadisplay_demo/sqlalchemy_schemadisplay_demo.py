# https://github.com/fschulze/sqlalchemy_schemadisplay
# sudo apt install graphviz
# pip install sqlalchemy_schemadisplay

from sqlalchemy import create_engine
from sqlalchemy_schemadisplay import create_schema_graph

from app.models.db import SQLModel

# create the pydot graph object by autoloading all tables via a bound metadata object
graph = create_schema_graph(
    engine=create_engine("sqlite:///db.sqlite3"),  # or your own engine
    # metadata=MetaData("sqlite:///db.sqlite3"),
    metadata=SQLModel.metadata,
    show_datatypes=False,  # The image would get nasty big if we'd show the datatypes
    show_indexes=False,  # ditto for indexes
    rankdir="LR",  # From left to right (instead of top to bottom)
    concentrate=False,  # Don't try to join the relation lines together
)
graph.write_png(
    "./tools/sql_to_erd/sqlalchemy_schemadisplay_demo/sqlalchemy_schemadisplay.png"
)  # write out the file
