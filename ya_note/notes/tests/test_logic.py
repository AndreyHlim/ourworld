from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note
from pytest_django.asserts import assertRedirects
from pytils.translit import slugify

User = get_user_model()


class TestNote(TestCase):
    NOTE_TITLE = 'Название заметки'
    NOTE_TEXT = 'Текст заметки'
    NEW_TEXT = 'Обновлённая заметка'
    NEW_TITLE = 'Новое название'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.user,
            slug='note-slug')
        cls.reader = User.objects.create(username='Другой пользователь')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.add_url = reverse('notes:add', args=None)
        cls.success_url = reverse('notes:success', args=None)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {'text': cls.NOTE_TEXT,
                         'title': cls.NOTE_TITLE,
                         'slug': 'slug'}
        cls.new_fdata = {'text': cls.NEW_TEXT, 'title': cls.NEW_TITLE}

    def test_anonymous_user_cant_create_note(self):
        self.client.post(self.add_url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_authuser_can_create_note(self):
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        note = Note.objects.get(id=2)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.author, self.user)

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.new_fdata)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_TEXT)
        self.assertEqual(self.note.title, self.NEW_TITLE)

    def test_user_cant_delete_note_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_cant_edit_note_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.new_fdata)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.title, self.NOTE_TITLE)

    def test_not_unique_slug(self):
        form_data = {
            'title': self.note.title,
            'text': self.note.text,
            'slug': self.note.slug,
            'author': self.user
        }
        response = self.author_client.post(self.add_url, data=form_data)
        self.assertIn('form', response.context)
        self.assertFormError(response,
                             'form',
                             'slug',
                             errors=(self.note.slug + WARNING))
        self.note.refresh_from_db()
        assert Note.objects.count() == 1

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_url, data=self.form_data)
        assertRedirects(response, self.success_url)
        assert Note.objects.count() == 2
        new_note = Note.objects.get(id=2)
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
