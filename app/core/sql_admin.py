from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncEngine

from app.models.db import Tag, Task, Team, User


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
