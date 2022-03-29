import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from backend.app.db.session import Base
from backend.app.models.celery_task import CeleryTask  # noqa
from backend.app.models.data_collect_history import DataCollectHistory  # noqa
from backend.app.models.data_collect_history_event import DataCollectHistoryEvent  # noqa
from backend.app.models.data_collect_history_gateway import DataCollectHistoryGateway  # noqa
from backend.app.models.data_collect_history_handler import DataCollectHistoryHandler  # noqa
from backend.app.models.data_collect_history_sensor import DataCollectHistorySensor  # noqa
from backend.app.models.gateway import Gateway  # noqa
from backend.app.models.handler import Handler  # noqa
from backend.app.models.machine import Machine  # noqa
from backend.app.models.machine_type import MachineType  # noqa
from backend.app.models.sensor import Sensor  # noqa
from backend.app.models.sensor_type import SensorType  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # url = config.get_main_option("sqlalchemy.url")
    url = os.environ["SQLALCHEMY_DATABASE_URI"]

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = os.environ["SQLALCHEMY_DATABASE_URI"]

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
