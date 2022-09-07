from os import system as run_command
from subprocess import check_output as run_command_with_output
from typing import List


def command_backup_all(host: str, port: int, output_dir: str) -> int:
    return run_command(" ".join([
        "mongodump",
        f"--host={host}",
        f"--port={port}",
        f"--out={output_dir}",
        "--gzip",
        "--quiet"
    ]))


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


def command_remove_dir(dir: str) -> int:
    return run_command(" ".join([
        "rm",
        "-rf",
        dir
    ]))


def command_get_database_count(dir: str) -> int:
    return len(run_command_with_output([
        "ls",
        dir
    ]).decode("utf-8").split())


def command_get_collection_count(dir: str) -> int:
    return len(run_command_with_output([
        "find",
        dir,
        "-name",
        "*.bson.gz"  # 数据库备份文件的后缀
    ]).decode("utf-8").split())
