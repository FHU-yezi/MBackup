from datetime import date

from apscheduler.schedulers.blocking import BlockingScheduler

from command import (command_backup_all, command_get_collection_count,
                     command_get_database_count, command_get_dir_size_in_MB,
                     command_remove_dir)
from config_manager import config
from message_sender import send_task_success_card
from store import get_auth_obj, get_bucket_obj, upload_dir
from utils import cron_to_kwargs


def full_backup_job() -> None:
    config.refresh()

    command_backup_all(config.db.host, config.db.port, config.output_dir)
    disk_cost: str = command_get_dir_size_in_MB(config.output_dir)
    database_count: int = command_get_database_count(config.output_dir)
    collection_count: int = command_get_collection_count(config.output_dir)

    auth = get_auth_obj(config.oss.access_key_id, config.oss.access_key_secret)
    bucket = get_bucket_obj(auth, config.oss.bucket_endpoint, config.oss.bucket_name)

    upload_dir(bucket, config.output_dir, config.source, date.today())

    send_task_success_card(config.source, "全量备份", database_count,
                           collection_count, disk_cost)

    command_remove_dir(config.output_dir)


scheduler: BlockingScheduler = BlockingScheduler()

scheduler.add_job(full_backup_job, "cron", **cron_to_kwargs(config.scheduled_cron))

scheduler.start()
