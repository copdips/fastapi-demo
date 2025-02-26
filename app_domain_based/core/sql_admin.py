from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncEngine

# from app_domain_based.models.db import Tag, Task, Team, User
from app_domain_based.app_tag.models import Tag
from app_domain_based.app_task.models import Task
from app_domain_based.app_team.models import Team
from app_domain_based.app_user.models import User


class TagAdmin(ModelView, model=Tag):
    column_list = [c_attr.key for c_attr in User.__mapper__.column_attrs]
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True


class TaskAdmin(ModelView, model=Task):
    column_list = [c_attr.key for c_attr in User.__mapper__.column_attrs]


class TeamAdmin(ModelView, model=Team):
    column_list = [c_attr.key for c_attr in User.__mapper__.column_attrs]


class UserAdmin(ModelView, model=User):
    column_list = [c_attr.key for c_attr in User.__mapper__.column_attrs]


def init_sqladmin(app: FastAPI, engine: AsyncEngine):
    admin = Admin(app, engine)

    admin.add_view(TagAdmin)
    admin.add_view(TeamAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(UserAdmin)
