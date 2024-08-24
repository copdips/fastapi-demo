# https://github.com/maurerle/eralchemy2
# pip install eralchemy2
# sudo apt install graphviz libgraphviz-dev

eralchemy2 -i sqlite:///db.sqlite3 -o ./tools/sql_to_erd/eralchemy2_demo/eralchemy2.pdf
eralchemy2 -i sqlite:///db.sqlite3 -o ./tools/sql_to_erd/eralchemy2_demo/eralchemy2.png
eralchemy2 -i sqlite:///db.sqlite3 -o ./tools/sql_to_erd/eralchemy2_demo/eralchemy2.svg
eralchemy2 -i sqlite:///db.sqlite3 -o ./tools/sql_to_erd/eralchemy2_demo/eralchemy2.md
