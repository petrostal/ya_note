from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='username')
        Note.objects.create(
            title='1',
            text='text',
            author=cls.author
        )

    def test_notes_on_list_page(self):
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        objects_list = response.context['object_list']
        self.assertEqual(len(objects_list), 1)
