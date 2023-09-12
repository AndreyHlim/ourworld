from http import HTTPStatus

from django.urls import reverse

import pytest
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


@pytest.mark.django_db
def test_author_can_delete_comment(news, author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.delete(url)
    news_url = reverse('news:detail', args=(news.id,))
    expected_url = f'{news_url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(news, author_client,
                                 comment, form_comment_data):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=form_comment_data)
    news_url = reverse('news:detail', args=(news.id,))
    expected_url = f'{news_url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.get(id=comment.id).text == form_comment_data['text']


def test_user_cant_delete_comment(admin_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_user_cant_edit_comment(admin_client, comment, form_comment_data):
    url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post(url, data=form_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment == comment


def test_cant_use_bad_words(admin_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news, client, form_comment_data):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_comment_data)
    assert Comment.objects.count() == 0
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)


@pytest.mark.django_db
def test_anonymous_auth_cant_create_comment(news,
                                            admin_client,
                                            form_comment_data,
                                            ):
    url = reverse('news:detail', args=(news.id,))
    response = admin_client.post(url, data=form_comment_data)
    assert Comment.objects.count() == 1
    success_url = reverse('news:detail', args=(news.id,))
    expected_url = f'{success_url}#comments'
    assertRedirects(response, expected_url)
    new_comment = Comment.objects.get()
    assert new_comment.text == form_comment_data['text']
