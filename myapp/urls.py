from django.urls import path
from . import views
urlpatterns = [
    path('', views.code_generator,name='code_generator'),
]
