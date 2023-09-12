from django.conf import settings
from django.urls import reverse

import pytest

HOME_URL = reverse('news:home')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_comment_visible',
    ((pytest.lazy_fixture('admin_client'), True),
     (pytest.lazy_fixture('client'), False))
)
def test_availability_form_comment_page(
    parametrized_client, form_comment_visible, news
):
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_comment_visible


@pytest.mark.django_db
@pytest.mark.usefixtures('news_many')
class TestNews:
    def test_news_count(self, client):
        response = client.get(HOME_URL)
        news_count = len(response.context['object_list'])
        assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_order(self, client):
        response = client.get(HOME_URL)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert all_dates == sorted_dates


@pytest.mark.usefixtures('comment_many')
def test_comments_order(news, client):
    detail_url = reverse('news:detail', args=(news.id,))
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created
