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
            # ('notes:detail', (self.note.slug,)),
            # ('notes:list', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)