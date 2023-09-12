from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст заметки.',
            author=cls.author,
            slug='Notes'
        )
        cls.add_url = reverse('notes:add', args=None)
        cls.edit_erl = reverse('notes:edit', args=(cls.note.slug,))
        cls.notes_list_url = reverse('notes:list')

    def test_authorized_client_has_form(self):
        for name in (self.edit_erl, self.add_url):
            with self.subTest(name=name):
                response = self.author_client.get(name)
                self.assertIn('form', response.context)

    def test_notes_list_for_different_users(self):
        for client_user, args in ((self.author_client, True),
                                  (self.reader_client, False)):
            with self.subTest(name=client_user):
                response = client_user.get(self.notes_list_url)
                self.assertIn('object_list', response.context)
                object_list = response.context['object_list']
                assert (self.note in object_list) is args
