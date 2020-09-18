from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from task_manager import forms as tm_forms
from task_manager import views as tm_views
from task_manager import models as tm_models


class CustomRegistrationViewTest(TestCase):
    def test_form_class(self):
        self.assertEquals(
            tm_views.CustomRegistrationView.form_class,
            tm_forms.CustomRegistrationForm
        )


class IndexViewTest(TestCase):
    def setUp(self):
        ivanov = User.objects.create(
            username='pivanov',
        )
        ivanov.set_password('q1w2e3r4t5')
        ivanov.save()
        petrov = User.objects.create(
            username='ipetrov',
        )
        status = tm_models.TaskStatus.objects.create(
            name='task_status_model_test'
        )
        task_by_ivanov = tm_models.Task.objects.create(
            name='creator_ivanov_aasigned_to_petrov',
            status=status,
            creator=ivanov,
            assigned_to=petrov,
        )
        task_by_petrov = tm_models.Task.objects.create(
            name='creator_petrov_aasigned_to_ivanov',
            status=status,
            creator=petrov,
            assigned_to=ivanov,
        )

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'task_manager/index.html'
        )

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(
            username='pivanov',
            password='q1w2e3r4t5'
        )
        self.assertTrue(login)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            response.context.get('created_tasks_count'),
            1
        )
        self.assertTrue(
            response.context.get('assigned_tasks_count'),
            1
        )


class ProfileViewTest(TestCase):
    def setUp(self):
        user = User.objects.create(
            first_name='Petr',
            last_name='Sidorov',
            username='psidorov',
            email='psidorov@example.com',
        )
        user.set_password('t4e3s2t1')
        user.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith(reverse('login'))
        )

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(
            username='psidorov',
            password='t4e3s2t1'
        )
        self.assertTrue(login)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'task_manager/profile.html'
        )


class CreateTaskTest(TestCase):
    def setUp(self):
        self.alex = User.objects.create(
            first_name='Alex',
            last_name='Sidorov',
            username='asidorov',
            email='asidorov@example.com',
        )
        self.alex.set_password('t4e3s2t1')
        self.alex.save()
        self.phil = User.objects.create(
            first_name='Phil',
            last_name='Sidorov',
            username='phsidorov',
            email='phsidorov@example.com',
        )
        self.phil.set_password('t4e3s2t1')
        self.phil.save()

        self.status_new = tm_models.TaskStatus.objects.create(
            name='test_status_new'
        )
        self.status_done = tm_models.TaskStatus.objects.create(
            name='test_status_done'
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('create_task'))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith(reverse('login'))
        )

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(
            username='asidorov',
            password='t4e3s2t1'
        )
        self.assertTrue(login)
        response = self.client.get(reverse('create_task'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'task_manager/create_task.html'
        )

    def test_logged_in_uses_correct_forms(self):
        login = self.client.login(
            username='asidorov',
            password='t4e3s2t1'
        )
        response = self.client.get(reverse('create_task'))
        self.assertTrue(
            isinstance(
                response.context['task_form'],
                tm_forms.TaskForm
            )
        )
        self.assertTrue(
            isinstance(
                response.context['tag_form'],
                tm_forms.CreateTagsForm
            )
        )

    def test_logged_in_initial_form_state(self):
        login = self.client.login(
            username='asidorov',
            password='t4e3s2t1'
        )
        response = self.client.get(reverse('create_task'))
        self.assertEquals(
            response.context['task_form'].initial['creator'],
            self.alex
        )
        self.assertTrue(
            response.context['task_form'].fields['creator'].disabled,
            self.alex
        )
        self.assertEquals(
            response.context['task_form'].initial['status'],
            self.status_new
        )
        self.assertTrue(
            response.context['task_form'].fields['status'].disabled,
            self.status_new
        )

    def test_logged_in_create_new_task(self):
        login = self.client.login(
            username='asidorov',
            password='t4e3s2t1'
        )
        
        response = self.client.post(
            reverse('create_task'),
            {
                'name': ['test_task_creation'],
                'description': ['description for test_task_creation'],
                'assigned_to': [self.phil.pk],
                'tags': ['test|task|creation']
            },
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('tasks')
        )
        task = tm_models.Task.objects.get(name='test_task_creation')
        self.assertEquals(
            task.description,
            'description for test_task_creation'
        )
        self.assertEquals(
            task.creator,
            self.alex
        )
        self.assertEquals(
            task.assigned_to,
            self.phil
        )
        self.assertEquals(
            task.tags.get(name='test'),
            tm_models.Tag.objects.get(name='test')
        )
        self.assertEquals(
            task.tags.get(name='task'),
            tm_models.Tag.objects.get(name='task')
        )
        self.assertEquals(
            task.tags.get(name='creation'),
            tm_models.Tag.objects.get(name='creation')
        )

