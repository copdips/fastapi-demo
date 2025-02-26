from app_domain_based.app_common.models import BaseSQLModel
from app_domain_based.app_email.schemas import EmailBase


class Email(BaseSQLModel, EmailBase, table=True): ...
