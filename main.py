from datetime import date
from typing import List

from apscheduler.schedulers.blocking import BlockingScheduler
from pymongo import MongoClient

from utils.config import config
from db_manager import (
    backup_collection,
    command_get_dir_size_in_MB,
    command_remove_dir,
    get_collection_names_list,
    get_db_names_list,
)
from utils.message import send_task_success_card
from store import get_auth_obj, get_bucket_obj, upload_dir
from utils.time_helper import cron_to_kwargs


def full_backup_job() -> None:
    collections_count: int = 0

    config.refresh()

    client: MongoClient = MongoClient(config.db.host, config.db.port)
    db_names: List[str] = get_db_names_list(client)
    databases_count: int = len(db_names)
    for db_name in db_names:
        db_obj = client[db_name]
        collection_names = get_collection_names_list(db_obj)
        collections_count += len(collection_names)
        for collection_name in collection_names:
            backup_collection(
                config.db.host,
                config.db.port,
                config.output_dir,
                db_name,
                collection_name,
            )

    disk_cost: str = command_get_dir_size_in_MB(config.output_dir)

    auth = get_auth_obj(config.oss.access_key_id, config.oss.access_key_secret)
    bucket = get_bucket_obj(auth, config.oss.bucket_endpoint, config.oss.bucket_name)
    upload_dir(bucket, config.output_dir, config.source, date.today())

    send_task_success_card(
        config.source,
        "全量备份",
        databases_count,
        collections_count,
        disk_cost,
    )

    command_remove_dir(config.output_dir)


scheduler: BlockingScheduler = BlockingScheduler()

scheduler.add_job(full_backup_job, "cron", **cron_to_kwargs(config.scheduled_cron))

scheduler.start()
