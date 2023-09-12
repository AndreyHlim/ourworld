from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст заметки.',
            author=cls.author,
            slug='Notes'
        )
        cls.add_url = reverse('notes:add', args=None)
        cls.edit_erl = reverse('notes:edit', args=(cls.note.slug,))

    def test_authorized_client_has_form(self):
        for name in (self.edit_erl, self.add_url):
            with self.subTest(name=name):
                self.client.force_login(self.author)
                response = self.client.get(name)
                self.assertIn('form', response.context)

    def test_notes_list_for_different_users(self):
        for name, args in ((self.author, True),
                           (self.reader, False)):
            with self.subTest(name=name):
                url = reverse('notes:list')
                self.client.force_login(name)
                response = self.client.get(url)
                self.assertIn('object_list', response.context)
                object_list = response.context['object_list']
                assert (self.note in object_list) is args
