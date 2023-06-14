from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from http import HTTPStatus

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='user1')
        cls.reader = User.objects.create(username='user2')
        cls.note = Note.objects.create(
            title='title1',
            text='text1',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous(self):
        urls = (
            ('notes:detail', (self.note.id, )),
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:edit', (self.note.slug, )),
            ('notes:delete', (self.note.slug, )),
        )
        for name, args in urls:
            url = reverse(name, args=args)
            login_url = reverse('users:login')
            with self.subTest(name):
                response = self.client.get(url)
                redirect_url = f'{login_url}?next={url}'
                self.assertRedirects(response, redirect_url)
