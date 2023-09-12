from http import HTTPStatus
from random import choice

from django.urls import reverse

import pytest
from news.forms import BAD_WORDS, WARNING
from news.models import Comment
from pytest_django.asserts import assertFormError, assertRedirects


@pytest.mark.django_db
def test_author_can_delete_comment(news_detail_url,
                                   author_client,
                                   comment_delete_url):
    comments_count_before = Comment.objects.count()
    response = author_client.delete(comment_delete_url)
    expected_url = f'{news_detail_url}#comments'
    assertRedirects(response, expected_url)
    assert comments_count_before - Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(news,
                                 author_client,
                                 author,
                                 comment,
                                 form_comment_data,
                                 news_detail_url,
                                 comment_edit_url):
    response = author_client.post(comment_edit_url, data=form_comment_data)
    expected_url = f'{news_detail_url}#comments'
    assertRedirects(response, expected_url)
    comment = Comment.objects.get(id=comment.id)
    assert comment.text == form_comment_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_delete_comment(admin_client, comment_delete_url):
    comments_count_before = Comment.objects.count()
    response = admin_client.delete(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_count_before == Comment.objects.count()


def test_user_cant_edit_comment(admin_client,
                                comment,
                                form_comment_data,
                                comment_edit_url):
    response = admin_client.post(comment_edit_url, data=form_comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get(id=comment.id)
    assert new_comment == comment


def test_cant_use_bad_words(admin_client, news_detail_url):
    comments_count_before = Comment.objects.count()
    bad_words_data = {'text': f'Текст, {choice(BAD_WORDS)}, еще текст'}
    response = admin_client.post(news_detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert comments_count_before == Comment.objects.count()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news_detail_url,
                                            client,
                                            form_comment_data):
    comments_count_before = Comment.objects.count()
    response = client.post(news_detail_url, data=form_comment_data)
    assert comments_count_before == Comment.objects.count()
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)


@pytest.mark.django_db
def test_anonymous_auth_cant_create_comment(admin_client,
                                            form_comment_data,
                                            news_detail_url):
    response = admin_client.post(news_detail_url, data=form_comment_data)
    assert Comment.objects.count() == 1
    expected_url = f'{news_detail_url}#comments'
    assertRedirects(response, expected_url)
    new_comment = Comment.objects.get()
    assert new_comment.text == form_comment_data['text']
