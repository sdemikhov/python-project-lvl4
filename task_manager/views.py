from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django_registration.backends.one_step.views import RegistrationView

from task_manager.forms import CustomRegistrationForm


def index(request):
    return render(request, 'task_manager/index.html')


@login_required
def profile(request):
    return render(request, 'task_manager/profile.html')


class CustomRegistrationView(RegistrationView):
    form_class = CustomRegistrationForm
