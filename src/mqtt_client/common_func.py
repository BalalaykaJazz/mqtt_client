"""Общие функции"""
import os


def get_full_path(file_name: str) -> str:
    """Возвращает полный путь к файлу."""

    return os.path.join(os.path.dirname(__file__), file_name)
