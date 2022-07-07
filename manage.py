#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from socket import socket


def init():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProxyPool.settings')
    try:
        from django.core.management import execute_from_command_line
        return execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc


def main():
    """Run administrative tasks."""
    execute_from_command_line = init()
    execute_from_command_line(sys.argv)


def run():
    is_conflict = check_port_conflict(5000)
    if not is_conflict:
        execute_from_command_line = init()
        execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:5000', '--noreload'])


def check_port_conflict(port, host="127.0.0.1"):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((host, int(port)))
        return True
    except socket.error as why:
        print(why)
    finally:
        sock and sock.close()
        return False


if __name__ == '__main__':
    main()
