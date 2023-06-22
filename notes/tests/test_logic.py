from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

from pytils.translit import slugify

from notes.forms import WARNING

from django.conf import settings

from http import HTTPStatus


LOGIN_URL = settings.LOGIN_URL

User = get_user_model()


class BaseTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.add_url = reverse('notes:add')
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }
        cls.success_url = reverse('notes:success')


class TestNoteCreation(BaseTestClass):

    @classmethod
    def setUpTestData(cls):
        # cls.add_url = reverse('notes:add')
        super().setUpTestData()
        # cls.author = User.objects.create(username='author')
        # cls.form_data = {
        #     'title': 'Новый заголовок',
        #     'text': 'Новый текст',
        #     'slug': 'new-slug',
        # }

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.add_url, self.form_data)
        expected_url = f'{LOGIN_URL}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        response = self.author_client.post(self.add_url, self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.author_client.post(self.add_url, self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDelete(BaseTestClass):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        reader = User.objects.create(username='reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author,
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_not_unique_slug(self):
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(self.add_url, self.form_data)
        self.assertFormError(response, 'form', 'slug', errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(self.edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        response = self.author_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        response = self.reader_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
