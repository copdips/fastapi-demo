# https://github.com/Dicklesworthstone/sqlalchemy_data_model_visualizer/tree/main
# sudo apt install graphviz xdg-utils
# pip install sqlalchemy-data-model-visualizer

from sqlalchemy_data_model_visualizer import (
    add_web_font_and_interactivity,
    generate_data_model_diagram,
)

from app.models.db import Email, Tag, TagTeamLink, Task, Team, User

models = [Email, Tag, TagTeamLink, Task, Team, User]
output_file_name = "./tools/sql_to_erd/sqlalchemy_data_model_visualizer_demo/sqlalchemy_data_model_visualizer"
generate_data_model_diagram(models, output_file_name)
add_web_font_and_interactivity(
    "./tools/sql_to_erd/sqlalchemy_data_model_visualizer_demo/sqlalchemy_data_model_visualizer.svg",
    "./tools/sql_to_erd/sqlalchemy_data_model_visualizer_demo/sqlalchemy_data_model_visualizer_interactive.svg",
)
