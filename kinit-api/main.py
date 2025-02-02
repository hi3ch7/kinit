# -*- coding: utf-8 -*-
# @version        : 1.0
# @Creaet Time    : 2021/10/19 15:47
# @File           : main.py
# @IDE            : PyCharm
# @desc           : 主程序入口

"""
FastApi 更新文档：https://github.com/tiangolo/fastapi/releases
FastApi Github：https://github.com/tiangolo/fastapi
Typer 官方文档：https://typer.tiangolo.com/
"""

from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from application import settings
from application import urls
from starlette.staticfiles import StaticFiles  # 依赖安装：pip install aiofiles
from core.exception import register_exception
import typer
from scripts.initialize.initialize import InitializeData, Environment
import asyncio
from scripts.create_app.main import CreateApp
from core.event import lifespan
from utils.tools import import_modules


shell_app = typer.Typer()


def create_app():
    """
    启动项目

    docs_url：配置交互文档的路由地址，如果禁用则为None，默认为 /docs
    redoc_url： 配置 Redoc 文档的路由地址，如果禁用则为None，默认为 /redoc
    openapi_url：配置接口文件json数据文件路由地址，如果禁用则为None，默认为/openapi.json
    """
    app = FastAPI(
        title="Kinit",
        description="本项目基于Fastapi与Vue3+Typescript+Vite4+element-plus的基础项目 前端基于vue-element-plus-admin框架开发",
        version=settings.VERSION,
        lifespan=lifespan
    )
    import_modules(settings.MIDDLEWARES, "中间件", app=app)
    # 全局异常捕捉处理
    register_exception(app)
    # 跨域解决
    if settings.CORS_ORIGIN_ENABLE:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.ALLOW_ORIGINS,
            allow_credentials=settings.ALLOW_CREDENTIALS,
            allow_methods=settings.ALLOW_METHODS,
            allow_headers=settings.ALLOW_HEADERS
        )
    # 挂在静态目录
    if settings.STATIC_ENABLE:
        app.mount(settings.STATIC_URL, app=StaticFiles(directory=settings.STATIC_ROOT))
    if settings.TEMP_ENABLE:
        app.mount(settings.TEMP_URL, app=StaticFiles(directory=settings.TEMP_DIR))
    # 引入应用中的路由
    for url in urls.urlpatterns:
        app.include_router(url["ApiRouter"], prefix=url["prefix"], tags=url["tags"])
    return app


@shell_app.command()
def run():
    """
    启动项目

    factory: 在使用 uvicorn.run() 启动 ASGI 应用程序时，可以通过设置 factory 参数来指定应用程序工厂。
    应用程序工厂是一个返回 ASGI 应用程序实例的可调用对象，它可以在启动时动态创建应用程序实例。
    """
    uvicorn.run(app='main:create_app', host="0.0.0.0", port=9000, lifespan="on", factory=True)


@shell_app.command()
def init(env: Environment = Environment.pro):
    """
    初始化数据

    :params name: 数据库环境
    """
    print("开始初始化数据")
    data = InitializeData()
    asyncio.run(data.run(env))


@shell_app.command()
def migrate(env: Environment = Environment.pro):
    """
    将模型迁移到数据库，更新数据库表结构

    :params name: 数据库环境
    """
    print("开始更新数据库表")
    InitializeData.migrate_model(env)


@shell_app.command()
def init_app(path: str):
    """
    自动创建初始化 APP 结构

    :params path: app 路径，根目录为apps，填写apps后面路径即可，例子：vadmin/auth
    """
    print(f"开始创建并初始化 {path} APP")
    app = CreateApp(path)
    app.run()


if __name__ == '__main__':
    shell_app()
