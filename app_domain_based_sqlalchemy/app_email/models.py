from app_domain_based_sqlalchemy.app_common.models import BaseSQLModel
from app_domain_based_sqlalchemy.app_email.schemas import EmailBase


class Email(BaseSQLModel, EmailBase, table=True): ...
