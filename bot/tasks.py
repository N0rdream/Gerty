import os
import redis
from celery import shared_task
from .models import Hashtag, History
from celery.exceptions import Ignore
from .parsers import parse_redis_data
from .vk_helpers import send_execute_request, get_code_for_execute


@shared_task(ignore_result=True)
def handle_message_without_hashtag(message_type, vk_timestamp, user_id, message):
    History.save_message(message_type, vk_timestamp, user_id, message)

@shared_task
def handle_message_with_hashtag(message_type, vk_timestamp, user_id, message, hashtag):
    hashtag_obj = Hashtag.objects.select_related().filter(name=hashtag).first()
    if hashtag_obj is None:
        History.save_message(message_type, vk_timestamp, user_id, message)
        raise Ignore
    if History.has_hashtag(
        hashtag, user_id, vk_timestamp, os.environ['VK_ANSWER_TIMEOUT']
    ):
        History.save_message(
            message_type, vk_timestamp, user_id, message, hashtag_obj
        )
        raise Ignore
    History.save_message(
        message_type, vk_timestamp, user_id, message, hashtag_obj, answered=True
    )
    return {
        'user_id': user_id, 
        'vk_timestamp': vk_timestamp,
        'message': hashtag_obj.message,
        'vk_attachment_id': hashtag_obj.vk_attachment_id
    }

@shared_task(ignore_result=True)
def send_hashtag_data():
    host = os.environ['CELERY_REDIS_HOST']
    port = os.environ['CELERY_REDIS_PORT']
    db = os.environ['CELERY_REDIS_DB']
    access_token = os.environ['VK_GROUP_ACCESS_TOKEN']
    api_version = os.environ['VK_API_VERSION']
    redis_db = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
    parsed_data = parse_redis_data(redis_db)
    if parsed_data is None:
        raise Ignore
    data = parsed_data['data']
    if data:
        code = get_code_for_execute(data, access_token, api_version)
        send_execute_request(code, access_token, api_version)
    for k in parsed_data['checked_keys']:
        redis_db.delete(k)






