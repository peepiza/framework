"""Корневой conftest.py — обеспечивает импорт модулей проекта в тестах."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
