import os
from django.shortcuts import render
from django.utils import timezone


def map_field_type(field_type):
    # Map custom field types to Django model field types
    field_mapping = {
        'int': 'IntegerField',
        'text': 'CharField',
        'date': 'DateField',
        # Add more mappings as needed
    }
    return field_mapping.get(field_type, 'CharField')


def generate_build_txt(project_name, app_name):
    return f"mkdir {project_name}-{timezone.now().strftime('%Y%m%d')}\n" \
           f"cd {project_name}-{timezone.now().strftime('%Y%m%d')}\n" \
           f"python3 -m venv venv\n" \
           f". venv/bin/activate\n" \
           f"pip install django\n" \
           f"django-admin startproject {project_name} .\n" \
           f"python manage.py startapp {app_name}\n"


def generate_model_content(database_model, fields):
    model_content = f"from django.db import models\n\n"
    model_content += f"class {database_model}(models.Model):\n"

    # Parse fields and generate model fields with proper Django types
    for field in fields.split(','):
        field_name, field_type = field.split(':')
        django_field_type = map_field_type(field_type)
        if django_field_type == 'CharField':
            model_content += f"    {field_name} = models.{django_field_type}(max_length=200, blank=True, null=True)\n"
        else:
            model_content += f"    {field_name} = models.{django_field_type}(blank=True, null=True)\n"

    return model_content


def generate_forms_content(database_model):
    forms_content = f"from django import forms\nfrom .models import {database_model}\n\n"
    forms_content += f"class {database_model}Form(forms.ModelForm):\n"
    forms_content += f"    class Meta:\n"
    forms_content += f"        model = {database_model}\n"
    forms_content += f"        fields = '__all__'\n"

    # Add Bootstrap classes to form fields
    forms_content += f"    def __init__(self, *args, **kwargs):\n"
    forms_content += f"        super().__init__(*args, **kwargs)\n"
    forms_content += f"        for field in self.fields:\n"
    forms_content += f"            self.fields[field].widget.attrs['class'] = 'form-control'\n"

    return forms_content


def generate_views_content(app_name, database_model):
    views_content = f"from django.shortcuts import render, get_object_or_404, redirect\n"
    views_content += f"from .models import {database_model}\n"
    views_content += f"from .forms import {database_model}Form\n\n"

    # List view
    views_content += f"def {database_model.lower()}_list(request):\n"
    views_content += f"    {database_model.lower()}s = {database_model}.objects.all()\n"
    views_content += f"    return render(request, '{app_name}/{database_model.lower()}_list.html', {{'{database_model.lower()}s': {database_model.lower()}s}})\n\n"

    # Detail view
    views_content += f"def {database_model.lower()}_detail(request, pk):\n"
    views_content += f"    {database_model.lower()} = get_object_or_404({database_model}, pk=pk)\n"
    views_content += f"    return render(request, '{app_name}/{database_model.lower()}_detail.html', {{'{database_model.lower()}': {database_model.lower()}}})\n\n"

    # Create view
    views_content += f"def {database_model.lower()}_create(request):\n"
    views_content += f"    if request.method == 'POST':\n"
    views_content += f"        form = {database_model}Form(request.POST)\n"
    views_content += f"        if form.is_valid():\n"
    views_content += f"            {database_model.lower()} = form.save(commit=False)\n"
    views_content += f"            {database_model.lower()}save()\n"
    views_content += f"            return redirect('{database_model.lower()}_list')\n"
    views_content += f"    else:\n"
    views_content += f"        form = {database_model}Form()\n"
    views_content += f"    return render(request, '{app_name}/{database_model.lower()}_form.html', {{'form': form}})\n\n"

    # Update view
    views_content += f"def {database_model.lower()}_update(request, pk):\n"
    views_content += f"    {database_model.lower()} = get_object_or_404({database_model}, pk=pk)\n"
    views_content += f"    if request.method == 'POST':\n"
    views_content += f"        form = {database_model}Form(request.POST, instance={database_model.lower()})\n"
    views_content += f"        if form.is_valid():\n"
    views_content += f"            {database_model.lower()} = form.save(commit=False)\n"
    views_content += f"            {database_model.lower()}save()\n"
    views_content += f"            return redirect('{database_model.lower()}_list')\n"
    views_content += f"    else:\n"
    views_content += f"        form = {database_model}Form(instance={database_model.lower()})\n"
    views_content += f"    return render(request, '{app_name}/{database_model.lower()}_form.html', {{'form': form}})\n\n"

    # Delete view
    views_content += f"def {database_model.lower()}_delete(request, pk):\n"
    views_content += f"    {database_model.lower()} = get_object_or_404({database_model}, pk=pk)\n"
    views_content += f"    {database_model.lower()}.delete()\n"
    views_content += f"    return redirect('{database_model.lower()}_list')\n\n"

    return views_content


def generate_urls_content(app_name, database_model):
    urls_content = f"from django.urls import path\nfrom . import views\n\n"
    urls_content += f"app_name = '{app_name}'\n\n"

    # URL patterns for CRUD operations
    urls_content += f"urlpatterns = [\n"
    urls_content += f"    path('{database_model.lower()}/', views.{database_model.lower()}_list, name='{database_model.lower()}_list'),\n"
    urls_content += f"    path('{database_model.lower()}/<int:pk>/', views.{database_model.lower()}_detail, name='{database_model.lower()}_detail'),\n"
    urls_content += f"    path('{database_model.lower()}/create/', views.{database_model.lower()}_create, name='{database_model.lower()}_create'),\n"
    urls_content += f"    path('{database_model.lower()}/<int:pk>/update/', views.{database_model.lower()}_update, name='{database_model.lower()}_update'),\n"
    urls_content += f"    path('{database_model.lower()}/<int:pk>/delete/', views.{database_model.lower()}_delete, name='{database_model.lower()}_delete'),\n"
    urls_content += f"]\n"

    return urls_content


def code_generator(request):
    if request.method == 'POST':
        app_name = request.POST.get('app_name')
        project_name = request.POST.get('project_name')
        database_model = request.POST.get('database_model')
        fields = request.POST.get('fields')

        # Create OUTPUT directory if not exists
        output_dir = "OUTPUT"
        os.makedirs(output_dir, exist_ok=True)

        # Create building_app directory inside OUTPUT
        building_app_dir = os.path.join(output_dir, "building_app")
        os.makedirs(building_app_dir, exist_ok=True)

        # Create APP_Files directory inside OUTPUT
        app_files_dir = os.path.join(output_dir, "APP_Files", app_name)
        os.makedirs(app_files_dir, exist_ok=True)

        # Generate build.txt content and save
        build_content = generate_build_txt(project_name, app_name)
        with open(os.path.join(building_app_dir, "build.txt"), "w") as build_file:
            build_file.write(build_content)

        # Generate model content and save
        model_content = generate_model_content(database_model, fields)
        with open(os.path.join(app_files_dir, "models.py"), "w") as model_file:
            model_file.write(model_content)

        # Generate forms content and save
        forms_content = generate_forms_content(database_model)
        with open(os.path.join(app_files_dir, "forms.py"), "w") as forms_file:
            forms_file.write(forms_content)

        # Generate views content and save
        views_content = generate_views_content(app_name, database_model)
        with open(os.path.join(app_files_dir, "views.py"), "w") as views_file:
            views_file.write(views_content)

        # Generate urls content and save
        urls_content = generate_urls_content(app_name, database_model)
        with open(os.path.join(app_files_dir, "urls.py"), "w") as urls_file:
            urls_file.write(urls_content)

    return render(request, 'codegenerator/index.html')
