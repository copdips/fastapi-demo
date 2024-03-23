# ! must use sqlacodegen v3+ to generate models
sqlacodegen sqlite:///testing.db
sqlacodegen sqlite:///testing.db --generator sqlmodels

. .env
sqlacodegen $SQLACODEGEN_DB_CONN_URL
sqlacodegen $SQLACODEGEN_DB_CONN_URL --generator sqlmodels
sqlacodegen $SQLACODEGEN_DB_CONN_URL --generator dataclasses --outfile sqlacodegen_dataclasses.py

# erdantic sqlacodegen_dataclasses.Tag -o diagram.png
