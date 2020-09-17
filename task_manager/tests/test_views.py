from django.test import TestCase
from django.urls import reverse
from django.test import Client

from task_manager import forms as tm_forms
from task_manager import views as tm_views


class CustomRegistrationViewTest(TestCase):
    def test_form_class(self):
        self.assertEquals(
            tm_views.CustomRegistrationView.form_class,
            tm_forms.CustomRegistrationForm
        )


class IndexViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        c = Client()
        response = c.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
