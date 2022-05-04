from django.shortcuts import render
from .forms import UploadFileForm
from django.http import HttpResponseRedirect
from viewland.utils import create_graph
from pathlib import Path

# Create your views here.
def index(request):
    return render(request, 'app/index.html')

def handle_uploaded_file(f, name):
    Path('/code/data/').mkdir(parents=True, exist_ok = True)
    with open('/code/data/{}'.format(name), 'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return

def upload_min_data(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], 'min.data')
            return HttpResponseRedirect('/app/')
    else:
        form = UploadFileForm()
    return render(request, 'app/upload.html', {'form': form})

def upload_ts_data(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], 'ts.data')
            return HttpResponseRedirect('/app/')
    else:
        form = UploadFileForm()
    return render(request, 'app/upload.html', {'form': form})

def upload_colour(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], 'colour')
            return HttpResponseRedirect('/app/')
    else:
        form = UploadFileForm()
    return render(request, 'app/upload.html', {'form': form})

def upload_config(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], 'config')
            return HttpResponseRedirect('/app/')
    else:
        form = UploadFileForm()
    return render(request, 'app/upload.html', {'form': form})

def display(request):
    create_graph('/code/data/min.data', '/code/data/ts.data',
            '/code/data/config','/code/data/colour',
            '/code/app/static/app/images/out.png')
    return render(request, 'app/display.html')
