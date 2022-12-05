from typing import Dict

from httpx import post as httpx_post

from utils.config import config
from utils.time_helper import get_now_without_mileseconds


def get_feishu_token() -> str:
    """获取飞书 Token

    Raises:
        ValueError: 获取 Token 失败

    Returns:
        str: 飞书 Token
    """
    headers = {"Content-Type": "application/json; charset=utf-8"}
    data = {
        "app_id": config.message_sender.app_id,
        "app_secret": config.message_sender.app_secret,
    }
    response = httpx_post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        headers=headers,
        json=data,
    )

    if response.json()["code"] == 0:
        return "Bearer " + response.json()["tenant_access_token"]
    else:
        raise ValueError(
            "获取 Token 时发生错误，"
            f"错误码：{response.json()['code']}，"
            f"错误信息：{response.json()['msg']}"
        )


def send_feishu_card(card: Dict) -> None:
    """发送飞书卡片

    Args:
        card (Dict): 飞书卡片

    Raises:
        ValueError: 发送飞书卡片失败
    """
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": get_feishu_token(),
    }
    data = {
        "email": config.message_sender.email,
        "msg_type": "interactive",
        "card": card,
    }
    response = httpx_post(
        "https://open.feishu.cn/open-apis/message/v4/send/",
        headers=headers,
        json=data,
    )

    if response.json()["code"] != 0:
        raise ValueError(
            "发送消息卡片时发生错误，"
            f"错误码：{response.json()['code']}，"
            f"错误信息：{response.json()['msg']}"
        )


def send_task_success_card(
    source: str, task_name: str, db_count: int, collection_count: int, disk_cost: str
) -> None:
    """发送任务成功卡片"""
    time = get_now_without_mileseconds()

    card = {
        "header": {
            "template": "green",
            "title": {
                "content": "自动备份成功",
                "tag": "plain_text",
            },
        },
        "elements": [
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "content": f"**时间**\n{time}",
                            "tag": "lark_md",
                        },
                    },
                    {
                        "is_short": True,
                        "text": {
                            "content": f"**任务源 / 任务名称**\n{source} / {task_name}",
                            "tag": "lark_md",
                        },
                    },
                    {
                        "is_short": False,
                        "text": {
                            "content": "\n",
                            "tag": "plain_text",
                        },
                    },
                    {
                        "is_short": True,
                        "text": {
                            "content": f"**数据库 / 集合数量**\n{db_count} / {collection_count}",
                            "tag": "lark_md",
                        },
                    },
                    {
                        "is_short": True,
                        "text": {
                            "content": f"**占用空间**\n{disk_cost}",
                            "tag": "lark_md",
                        },
                    },
                ],
            }
        ],
    }

    send_feishu_card(card)
