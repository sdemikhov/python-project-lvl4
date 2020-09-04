"""task_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.contrib import admin

from task_manager import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tasks/search', views.tasks, name='tasks'),
    path('tasks/create', views.create_task, name='create_task'),
    path('statuses/', views.statuses, name='statuses'),
    path(
        'statuses/edit/<int:status_id>',
        views.edit_status,
        name='edit_status'
    ),
    path(
        'statuses/delete/<int:status_id>',
        views.delete_status,
        name='delete_status'
    ),
    path('accounts/profile/', views.profile, name='profile'),
    path(
        'accounts/register/',
        views.CustomRegistrationView.as_view(),
        name='django_registration_register'
    ),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]
