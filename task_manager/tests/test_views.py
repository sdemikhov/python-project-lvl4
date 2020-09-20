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
        tm_models.Task.objects.create(
            name='creator_ivanov_aasigned_to_petrov',
            status=status,
            creator=ivanov,
            assigned_to=petrov,
        )
        tm_models.Task.objects.create(
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


class CreateTaskViewTest(TestCase):
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
        self.assertTrue(login)
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
        self.assertTrue(login)
        response = self.client.get(reverse('create_task'))
        self.assertEquals(
            response.context['task_form'].initial['creator'],
            self.alex
        )
        self.assertTrue(
            response.context['task_form'].fields['creator'].disabled
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
        self.assertTrue(login)
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


class TaskDetailsViewTest(TestCase):
    def setUp(self):
        self.andrew = User.objects.create(
            first_name='Andrew',
            last_name='Sidorov',
            username='ansidorov',
            email='ansidorov@example.com',
        )
        self.andrew.set_password('t4e3s2t1')
        self.andrew.save()
        self.nick = User.objects.create(
            first_name='Nick',
            last_name='Sidorov',
            username='nsidorov',
            email='nsidorov@example.com',
        )
        self.nick.set_password('t4e3s2t1')
        self.nick.save()

        self.status_new = tm_models.TaskStatus.objects.create(
            name='test_status_new'
        )
        self.status_done = tm_models.TaskStatus.objects.create(
            name='test_status_done'
        )

        self.tag_testing = tm_models.Tag.objects.create(
            name='testing_task_details'
        )
        self.tag_must_be_deleted = tm_models.Tag.objects.create(
            name='this_tag_must_be_deleted'
        )

        self.task = tm_models.Task.objects.create(
            name='Name before edit',
            description='Description before edit',
            status=self.status_new,
            creator=self.andrew,
            assigned_to=self.nick,
        )
        self.task.tags.set(
            (self.tag_testing, self.tag_must_be_deleted)
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse('task_details', args=[self.task.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith(reverse('login'))
        )

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(
            username='ansidorov',
            password='t4e3s2t1'
        )
        self.assertTrue(login)
        response = self.client.get(
            reverse('task_details', args=[self.task.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'task_manager/task_details.html'
        )

    def test_logged_in_uses_correct_context_initial_state(self):
        login = self.client.login(
            username='ansidorov',
            password='t4e3s2t1'
        )
        self.assertTrue(login)
        response = self.client.get(
            reverse('task_details', args=[self.task.pk])
        )
        self.assertTrue(
            isinstance(
                response.context['task_form'],
                tm_forms.TaskForm
            )
        )
        self.assertEquals(
            response.context['task_form'].instance,
            self.task
        )
        self.assertTrue(
            response.context['task_form'].fields['creator'].disabled
        )
        self.assertTrue(
            isinstance(
                response.context['tag_form'],
                tm_forms.CreateTagsForm
            )
        )
        self.assertEquals(
            response.context['tag_form'].initial['tags'],
            '|'.join([tag.name for tag in self.task.tags.all()])
        )
        self.assertEquals(
            response.context['task'],
            self.task
        )

    def test_logged_in_edit_task(self):
        login = self.client.login(
            username='ansidorov',
            password='t4e3s2t1'
        )
        self.assertTrue(login)
        response = self.client.post(
            reverse('task_details', args=[self.task.pk]),
            {
                'name': ['Name after edit'],
                'description': ['Description after edit'],
                'status': [self.status_done.pk],
                'assigned_to': [self.andrew.pk],
                'tags': ['testing_task_details|fresh_new_tag']
            }
        )
        self.assertEqual(response.status_code, 200)

        with self.assertRaises(tm_models.Task.DoesNotExist):
            tm_models.Task.objects.get(
                name='Name before edit'
            )

        updated_task = tm_models.Task.objects.get(
                name='Name after edit'
            )

        self.assertEquals(
            updated_task.description,
            'Description after edit'
        )
        self.assertEquals(
            updated_task.status,
            self.status_done
        )
        self.assertEquals(
            updated_task.assigned_to,
            self.andrew
        )
        self.assertEquals(
            updated_task.creator,
            self.andrew
        )

        with self.assertRaises(tm_models.Tag.DoesNotExist):
            tm_models.Tag.objects.get(
                name='this_tag_must_be_deleted'
            )

        new_created_tag = tm_models.Tag.objects.get(name='fresh_new_tag')
        self.assertEquals(
            set(updated_task.tags.all()),
            set([self.tag_testing, new_created_tag])
        )

        self.assertEquals(
            response.context['task'],
            updated_task
        )
        self.assertTrue(
            isinstance(
                response.context['task_form'],
                tm_forms.TaskForm
            )
        )
        self.assertEquals(
            response.context['task_form'].instance,
            updated_task
        )
        self.assertTrue(
            response.context['task_form'].fields['creator'].disabled
        )
        self.assertTrue(
            isinstance(
                response.context['tag_form'],
                tm_forms.CreateTagsForm
            )
        )
        self.assertEquals(
            response.context['tag_form']['tags'].data,
            '|'.join([tag.name for tag in updated_task.tags.all()])
        )


class DeleteTaskVIew(TestCase):
    def setUp(self):
        self.denis = User.objects.create(
            first_name='Denis',
            last_name='Sidorov',
            username='desidorov',
            email='desidorov@example.com',
        )
        self.denis.set_password('t4e3s2t1')
        self.denis.save()
        self.dmitriy = User.objects.create(
            first_name='Dmitriy',
            last_name='Petrov',
            username='dmpetrov',
            email='dmpetrov@example.com',
        )
        self.dmitriy.set_password('t4e3s2t1')
        self.dmitriy.save()

        self.status_new = tm_models.TaskStatus.objects.create(
            name='test_status_new'
        )

        self.tag_testing = tm_models.Tag.objects.create(
            name='testing_task_delete'
        )

        self.task = tm_models.Task.objects.create(
            name='Just name',
            description='Description',
            status=self.status_new,
            creator=self.denis,
            assigned_to=self.dmitriy,
        )
        self.task.tags.set(
            (self.tag_testing,)
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse('delete_task', args=[self.task.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith(reverse('login'))
        )

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(
            username='desidorov',
            password='t4e3s2t1'
        )
        self.assertTrue(login)
        response = self.client.get(
            reverse('delete_task', args=[self.task.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            'task_manager/delete_task.html'
        )
        self.assertEquals(
            response.context['task'],
            self.task
        )

    def test_not_creator_delete_task(self):
        login = self.client.login(
            username='dmpetrov',
            password='t4e3s2t1'
        )
        self.assertTrue(login)
        response = self.client.post(
            reverse('delete_task', args=[self.task.pk]),
            follow=True
        )
        self.assertEquals(response.status_code, 200)

        self.assertTrue(
            tm_models.Task.objects.get(name=self.task.name)
        )

    def test_creator_delete_task(self):
        login = self.client.login(
            username='desidorov',
            password='t4e3s2t1'
        )
        self.assertTrue(login)
        response = self.client.post(
            reverse('delete_task', args=[self.task.pk])
        )
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(tm_models.Task.DoesNotExist):
            tm_models.Task.objects.get(
                name=self.task.name
            )
