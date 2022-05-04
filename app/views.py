from django.shortcuts import render
from .forms import UploadFileForm
from django.http import HttpResponseRedirect

# Create your views here.
def index(request):
    return render(request, 'app/index.html')

def handle_uploaded_file(f, name):
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

    return render(request, 'app/display.html')
