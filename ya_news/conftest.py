from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

import pytest
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
        date=datetime.today()
    )
    return news


@pytest.fixture
def news_many():
    today = datetime.today()
    News.objects.bulk_create(
        News(title=f'Новость {index}', text='Просто текст.',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )
    return news_many


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
        created=datetime.now()
    )
    return comment


@pytest.fixture
def comment_many(author, news):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now - timedelta(hours=index)
        comment.save()
    return comment_many


@pytest.fixture
def news_pk_for_args(news):
    return news.id,


@pytest.fixture
def form_comment_data():
    return {'text': 'Новый текст комментария'}
