from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django_registration.backends.one_step.views import RegistrationView
from django.contrib import messages

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


@login_required
def profile(request):
    return render(request, 'task_manager/profile.html')


@login_required
def create_task(request):
    default_fields = {
        'creator': request.user.pk,
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
def task_details(request, task_id):
    task = get_object_or_404(Task, pk=task_id)

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


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    if request.method == 'POST':
        if task.creator.pk == request.user.pk:
            task.delete()
            return redirect('tasks')
        else:
            messages.add_message(
                request,
                messages.WARNING,
                'Only creator can delete this task.'
            )
            return redirect('task_details', task_id)
    return render(
        request,
        'task_manager/delete_task.html',
        context={
            'task': task,
        }
    )


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


@login_required
def statuses(request):
    form = tm_forms.StatusForm()
    statuses = TaskStatus.objects.all()
    if request.method == 'POST':
        form = tm_forms.StatusForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('statuses')
    return render(
        request,
        'task_manager/statuses.html',
        context={
            'form': form,
            'statuses': statuses,
        }
    )


@login_required
def edit_status(request, status_id):
    status = get_object_or_404(TaskStatus, pk=status_id)
    form = tm_forms.StatusForm(instance=status)
    if request.method == 'POST':
        form = tm_forms.StatusForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            return redirect('statuses')
    return render(
        request,
        'task_manager/edit_status.html',
        context={
            'form': form,
            'status': status,
        }
    )


@login_required
def delete_status(request, status_id):
    status = get_object_or_404(TaskStatus, pk=status_id)
    if request.method == 'POST':
        bounded_tasks = status.bounded_tasks.all()
        if not bounded_tasks:
            status.delete()
        else:
            messages.add_message(
                request,
                messages.WARNING,
                "This status has bounded tasks, you can not delete it."
            )
            return redirect('statuses')
    return render(
        request,
        'task_manager/delete_status.html',
        context={
            'status': status,
        }
    )
