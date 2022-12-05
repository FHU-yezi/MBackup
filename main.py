from datetime import date
from os import mkdir
from shutil import rmtree
from typing import List

from apscheduler.schedulers.blocking import BlockingScheduler
from pymongo import MongoClient

from db_manager import (
    backup_db,
    command_get_dir_size_in_MB,
    get_collections_count,
    get_db_names_list,
)
from store import get_auth_obj, get_bucket_obj, upload_dir
from utils.config import config
from utils.message import send_task_success_card
from utils.time_helper import cron_to_kwargs


def full_backup_job() -> None:
    collections_count: int = 0

    config.refresh()

    mkdir(config.output_dir)
    client: MongoClient = MongoClient(config.db.host, config.db.port)
    db_names: List[str] = get_db_names_list(client)
    dbs_count: int = len(db_names)
    for db_name in db_names:
        db_obj = client[db_name]
        collections_count += get_collections_count(db_obj)
        backup_db(
            host=config.db.host,
            port=config.db.port,
            db_name=db_name,
            output_dir=config.output_dir,
        )

    disk_cost: str = command_get_dir_size_in_MB(config.output_dir)

    auth = get_auth_obj(
        config.oss.access_key_id,
        config.oss.access_key_secret,
    )
    bucket = get_bucket_obj(
        auth,
        config.oss.bucket_endpoint,
        config.oss.bucket_name,
    )
    upload_dir(
        bucket,
        config.output_dir,
        config.source,
        date.today(),
    )

    send_task_success_card(
        config.source,
        "全量备份",
        dbs_count,
        collections_count,
        disk_cost,
    )

    rmtree(config.output_dir)


scheduler: BlockingScheduler = BlockingScheduler()

scheduler.add_job(
    full_backup_job,
    "cron",
    **cron_to_kwargs(config.scheduled_cron),
)

scheduler.start()
