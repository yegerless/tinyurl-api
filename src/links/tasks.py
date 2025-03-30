import requests
from datetime import datetime, timedelta

from celery import Celery
from sqlalchemy import select, delete

from config import REDIS_PASSWORD, HOST_PORT
from database import get_session
from auth.models import User
from .models import Link


celery = Celery('tasks', broker=f"redis://:@redis:5370/1",
                broker_connection_retry_on_startup = True)

# celery.autodiscover_tasks()


@celery.task(name='tasks.delete_expired_links', default_retry_delay=10, max_retries=3)
def delete_expired_links():
    '''
        Функция delete_expired_links раз в 1 минуту проходится по БД
            и удаляет сслыки, у которых истекло время существования.
    '''

    # Получение сессии соединения с БД
    session = get_session()

    # Получение из БД данных о ссылках с истекшим временем существования
    query = select(Link).filter(Link.expires_at <= datetime.now())
    result = session.execute(query)
    result = result.scalars().all()

    links_to_delete = []
    if result:
        # Получение списка id ссылок для удаления
        for link in result:
            links_to_delete.append(link.id)

        # Удаление ссылок, у которых истекло время существования
        query = delete(Link).filter(Link.id.in_(links_to_delete))
        session.execute(query)
        session.commit()

        return f'Links with id {links_to_delete} has been deleted.'

    return 'No links to delete'


# Регистрация таски в расписании
celery.conf.beat_schedule = {
    'delete-expired-links-every-minute': {
        'task': "tasks.delete_expired_links",
        "schedule": 60.0
    },
}
