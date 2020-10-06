from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django_registration.backends.one_step.views import RegistrationView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy

from task_manager import forms as tm_forms
from task_manager.models import TaskStatus, Tag, Task


FILTER = 'filter_'


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


@login_required
def create_task(request):
    default_fields = {
        'creator': request.user,
        'status': TaskStatus.objects.first()
    }
    task_form = tm_forms.TaskForm(
        request.POST or None,
        initial=default_fields,
    )
    task_form.fields['creator'].disabled = True
    task_form.fields['status'].disabled = True

    tag_form = tm_forms.CreateTagsForm(request.POST or None)
    if request.method == 'POST':
        if task_form.is_valid() and tag_form.is_valid():
            task = task_form.save()
            user_inputed_tags = tag_form.cleaned_data['tags']
            if user_inputed_tags:
                tags = set()
                for user_inputed_tag in user_inputed_tags.split('|'):
                    tag, _ = Tag.objects.get_or_create(
                        name=user_inputed_tag.strip()
                    )
                    tags.add(tag)
                task.tags.add(*tags)
                task.save()
            return redirect('tasks')
    return render(
        request,
        'task_manager/create_task.html',
        context={
            'task_form': task_form,
            'tag_form': tag_form,
        }
    )


@login_required
def task_details(request, pk):
    task = get_object_or_404(Task, pk=pk)

    task_form = tm_forms.TaskForm(instance=task)
    task_form.fields['creator'].disabled = True

    tags = task.tags.all()
    formatted = '|'.join([tag.name for tag in tags])
    tag_form = tm_forms.CreateTagsForm(initial={'tags': formatted})
    if request.method == 'POST':
        task_form = tm_forms.TaskForm(request.POST, instance=task)
        task_form.fields['creator'].disabled = True
        tag_form = tm_forms.CreateTagsForm(request.POST)
        if task_form.is_valid() and tag_form.is_valid():
            task = task_form.save(commit=False)
            user_inputed_tags = tag_form.cleaned_data['tags']
            new_set_of_tags = set()
            for user_inputed_tag in user_inputed_tags.split('|'):
                new_tag_name = user_inputed_tag.strip()
                if new_tag_name:
                    tag, _ = Tag.objects.get_or_create(
                        name=new_tag_name
                    )
                    new_set_of_tags.add(tag)
            previous_set_of_tags = set(tags)
            deleted_tags = previous_set_of_tags - new_set_of_tags
            for deleted_tag in deleted_tags:
                task.tags.remove(deleted_tag)
                bounded_tasks = deleted_tag.task_set.all()
                if not bounded_tasks:
                    deleted_tag.delete()
            task.tags.add(*new_set_of_tags)
            task.save()
    return render(
        request,
        'task_manager/task_details.html',
        context={
            'task_form': task_form,
            'tag_form': tag_form,
            'task': task,
        }
    )


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


@login_required
def tasks(request):
    filter_type_form = tm_forms.FilterTypeForm(request.GET or None)
    filter_by_my_tasks = tm_forms.FilterByMyTasksForm(
    )
    filter_by_tags_form = tm_forms.FilterByTagsForm()
    filter_by_status_form = tm_forms.FilterByStatusForm()
    filter_by_assigned_to_form = tm_forms.FilterByAssignedToForm()

    filter_ = request.GET.get(FILTER)
    tasks = []

    if filter_ == tm_forms.MY_TASKS:
        tasks = Task.objects.filter(
            assigned_to=request.user.pk
        )
    elif filter_ == tm_forms.TAGS:
        filter_by_tags_form = tm_forms.FilterByTagsForm(request.GET)
        if filter_by_tags_form.is_valid():
            user_inputed_tags = filter_by_tags_form.cleaned_data[
                tm_forms.TAGS
            ]
            tasks = Task.objects.filter(
                tags__in=user_inputed_tags
            ).distinct()
    elif filter_ == tm_forms.STATUS:
        filter_by_status_form = tm_forms.FilterByStatusForm(request.GET)
        if filter_by_status_form.is_valid():
            tasks = Task.objects.filter(
                status=filter_by_status_form.cleaned_data[
                    tm_forms.STATUS
                ]
            )
    elif filter_ == tm_forms.ASSIGNED_TO:
        filter_by_assigned_to_form = tm_forms.FilterByAssignedToForm(
            request.GET
        )
        if filter_by_assigned_to_form.is_valid():
            tasks = Task.objects.filter(
                assigned_to=filter_by_assigned_to_form.cleaned_data[
                    tm_forms.ASSIGNED_TO
                ]
            )
    return render(
        request,
        'task_manager/tasks.html',
        context={
            'filter_type_form': filter_type_form,
            'filter_by_my_tasks': filter_by_my_tasks,
            'filter_by_tags_form': filter_by_tags_form,
            'filter_by_status_form': filter_by_status_form,
            'filter_by_assigned_to_form': filter_by_assigned_to_form,
            'tasks': tasks,
        }
    )


class TasksView(LoginRequiredMixin, ListView):
    pass


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
