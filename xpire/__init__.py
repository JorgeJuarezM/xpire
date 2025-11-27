import os


def resolve_path(path: str) -> str:
    dirname = os.path.dirname(__file__)
    return os.path.join(dirname, "../", path)
