import os
import sys

from invoke.collection import Collection
from invoke.tasks import task

# pyright: reportArgumentType=false


@task
def manage(c, command, options=""):
    c.run(f"./manage.py {command} {options}")


@task
def makemigrations(c, options=""):
    """
    Runs ./manage.py makemigrations with an optional "options" parameter.
    """
    manage(c, "makemigrations", options)


@task
def migrate(c, options=""):
    """
    Runs ./manage.py migrate.
    """
    manage(c, "migrate", options)


@task
def shell(c):
    """
    Runs ./manage.py shell_plus.
    """
    os.execvp(sys.executable, [sys.executable, "manage.py", "shell_plus"])


ns = Collection()

ns.add_task(manage)
ns.add_task(makemigrations)
ns.add_task(migrate)
ns.add_task(shell)
