from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='title',
            text='text',
            author=cls.author
        )

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name):
                url = reverse(name, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)

    def test_notes_for_different_users(self):
        list_owners = (
            (self.author, True),
            (self.reader, False),
        )
        url = reverse('notes:list')
        for user, note_in_list in list_owners:
            with self.subTest(f'{user.username}'):
                self.client.force_login(user)
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)
