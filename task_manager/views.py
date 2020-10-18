from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django_registration.backends.one_step.views import RegistrationView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView, FormView, FormMixin
)
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy

from task_manager import forms as tm_forms
from task_manager.models import TaskStatus, Tag, Task


class CustomRegistrationView(RegistrationView):
    form_class = tm_forms.CustomRegistrationForm


def index(request):
    created_tasks_count = len(
        Task.objects.filter(creator=request.user.pk)
    )
    assigned_tasks_count = len(
        Task.objects.filter(assigned_to=request.user.pk)
    )
    return render(
        request,
        'task_manager/index.html',
        {
            'created_tasks_count': created_tasks_count,
            'assigned_tasks_count': assigned_tasks_count,
        }
    )


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'task_manager/profile.html'


class CreateTaskView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    template_name = 'task_manager/create_task.html'
    success_url = reverse_lazy('tasks')
    success_message = 'Task "%(name)s" was created successfully'
    form_class = tm_forms.TaskForm

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {
                'creator': self.request.user,
                'status': TaskStatus.objects.first()
            }
        )
        return initial

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)
        form.fields['status'].disabled = True
        return form


class TaskDetailView(LoginRequiredMixin, FormMixin, DetailView):
    model = Task
    form_class = tm_forms.TaskForm
    context_object_name = 'task'

    def get_success_url(self):
        return reverse_lazy('task_details', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class DeleteTaskView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'task_manager/delete_task.html'
    success_url = reverse_lazy('tasks')

    def delete(self, request, *args, **kwargs):
        task = self.get_object()
        if task.creator.pk == request.user.pk:
            messages.success(
                request,
                'Task "{}" was deleted successfully'.format(task.name)
            )
            return super().delete(request, *args, **kwargs)
        message = (
            'Only creator "{}" can delete this task.'.format(
                task.creator.get_full_name()
            )
        )
        messages.error(request, message)
        return redirect('task_details', pk=task.pk)


class TasksView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'task_manager/tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        self.filter_form = tm_forms.FilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            filters = {
                k: v for k, v in self.filter_form.cleaned_data.items()
                if v
            }

            if filters.get('my_tasks'):
                filters['assigned_to'] = self.request.user.pk
                del filters['my_tasks']

            tasks = Task.objects.filter(**filters).distinct()
        else:
            tasks = Task.objects.all()
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = self.filter_form
        return context


class StatusesView(LoginRequiredMixin, ListView):
    model = TaskStatus
    template_name = 'task_manager/statuses.html'
    context_object_name = 'statuses'


class CreateStatusView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = TaskStatus
    template_name = 'task_manager/create_status.html'
    success_url = reverse_lazy('statuses')
    success_message = 'Status "%(name)s" was created successfully'
    fields = ['name']


class UpdateStatusView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TaskStatus
    template_name = 'task_manager/edit_status.html'
    success_url = reverse_lazy('statuses')
    success_message = 'Status "%(name)s" was edited successfully'
    fields = ['name']


class DeleteStatusView(LoginRequiredMixin, DeleteView):
    model = TaskStatus
    template_name = 'task_manager/delete_status.html'
    success_url = reverse_lazy('statuses')

    def delete(self, request, *args, **kwargs):
        status = self.get_object()
        bounded_tasks = status.bounded_tasks.all()
        if bounded_tasks:
            message = (
                'Status "{}" has bounded tasks, you can not delete it!'.format(
                    status.name
                )
            )
            messages.error(request, message)
            return redirect('statuses')
        messages.success(
            request,
            'Status "{}" was deleted successfully'.format(status.name)
        )
        return super().delete(request, *args, **kwargs)
