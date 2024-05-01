from django.shortcuts import render, redirect
from .models import Photo
from .forms import PhotoForm


def photo_list(request):
    photos = Photo.objects.all()
    return render(request, 'photo_list.html', {'photos': photos})

def upload_photo(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('photo_list')
    else:
        form = PhotoForm()
    return render(request, 'upload_photo.html', {'form': form})

