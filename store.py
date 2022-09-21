from datetime import date

from oss2 import Auth, Bucket

from db_manager import command_get_files_in_dir


def get_auth_obj(access_key_id: str, access_key_secret: str) -> Auth:
    return Auth(access_key_id, access_key_secret)


def get_bucket_obj(auth_obj: Auth, endpoint: str, bucket_name: str) -> Bucket:
    return Bucket(auth_obj, endpoint, bucket_name)


def get_target_bucket_dir(local_dir: str, source: str, date: date) -> str:
    return f"{source}/{date}/" + "/".join(local_dir.split("/")[1:])


def upload_file(bucket_obj: Bucket, local_dir: str, bucket_dir: str) -> None:
    bucket_obj.put_object_from_file(bucket_dir, local_dir)


def upload_dir(bucket_obj: Bucket, base_dir: str, source: str, date: date) -> None:
    for file in command_get_files_in_dir(base_dir):
        upload_file(bucket_obj, file, get_target_bucket_dir(file, source, date))
