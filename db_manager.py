from os import system as run_command
from subprocess import check_output as run_command_with_output
from typing import List

from pymongo import MongoClient
from pymongo.database import Database


def backup_collection(host: str, port: int, output_dir: str,
                      db: str, collection: str) -> None:
    run_command(" ".join([
        "mongodump",
        f"--host={host}",
        f"--port={port}",
        f"--out={output_dir}",
        f"--db={db}",
        f"--collection={collection}",
        "--gzip",
        "--quiet"
    ]))


def get_db_names_list(client: MongoClient) -> List[str]:
    return [
        x
        for x in client.list_database_names()
        if x not in ("local",)
    ]


def get_collection_names_list(db: Database) -> List[str]:
    return db.list_collection_names()


def command_get_dir_size_in_MB(dir: str) -> str:
    file_size_in_bytes: int = int(run_command_with_output([
        "du",
        "-sh",  # 显示总和
        "-b",  # 单位为字节
        dir
    ]).decode("utf-8").split()[0])

    return str(round(file_size_in_bytes / 1024 / 1024, 2)) + "MB"


def command_get_files_in_dir(dir: str) -> List[str]:
    return run_command_with_output([
        "find",
        dir,
        "-name",
        "*.*"  # 所有文件
    ]).decode("utf-8").split()


def command_remove_dir(dir: str) -> None:
    run_command(" ".join([
        "rm",
        "-rf",
        dir
    ]))
