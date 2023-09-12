from http import HTTPStatus

from django.urls import reverse

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news_pk_for_args'))
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    )
)
@pytest.mark.parametrize(
    'name_url',
    (
        pytest.lazy_fixture('comment_edit_url'),
        pytest.lazy_fixture('comment_delete_url')
    )
)
def test_pages_availability_for_different_users(
        parametrized_client, name_url, expected_status
):
    response = parametrized_client.get(name_url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name_url',
    (
        pytest.lazy_fixture('comment_edit_url'),
        pytest.lazy_fixture('comment_delete_url')
    )
)
def test_redirects(client, name_url):
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={name_url}'
    response = client.get(name_url)
    assertRedirects(response, expected_url)
