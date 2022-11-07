from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .forms import TaskForm
from .models import Task

# Create your views here.
def home(request):
    #return HttpResponse("Hello, world. You're at the tasks index.")
    return render(request, 'home.html')

def signup(request):

    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm()
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save() # Save the user to the database
                login(request, user) #es para que el usuario se logee automaticamente.
                return redirect('tasks') # Redirect to the tasks page
        
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': 'That username has already been taken.'
                })


                
        return render(request, 'signup.html', {
            'form': UserCreationForm(),
            'error': 'Passwords do not match'
        })

@login_required
def tasks(request):

    #tasks = Task.objects.all() #esto es para que muestre todas las tareas de todos los usuarios.
    #filtrar tasks por usuario
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull=True) #datecompleted__isnull=True para que muestre solo las tareas que no estén completadas.

    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def task_completed(request):
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull=False).order_by('-dateCompleted')
    return render(request, 'tasks.html', {
        'task': tasks
    })

@login_required
def create_task(request): 

    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm()
        })
    else:
        try:
            #print(request.POST)
            form = TaskForm(request.POST)
            new_task = form.save(commit=False) #commit=False para que no guarde el formulario en la base de datos.
            new_task.user = request.user #para que el usuario que crea la tarea sea el que está logeado.
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm(),
                'error': 'Please provide a valid title and description'
            })

@login_required
def task_detail(request, task_id): 

    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {
            'task': task,
            'form': form
        })

    else: 
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {
                'task': task,
                'form': form,
                'error': 'Please provide a valid title and description'
            })

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.dateCompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


#vista que va a manejar el logout, para cerrar la sesión. 

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request): 
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm()
        })
    else:
        user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if user is None: #si el usuario no existe, entonces se va a mostrar el mensaje de error.
            return render(request, 'signin.html', {
                'form': AuthenticationForm(),
                'error': 'Username and password is incorrect'
            })
        else:
            login(request, user)
            return redirect('tasks')        

