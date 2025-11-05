from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

def register(request):
    """Register a new user"""
    if request.method !='POST':
        #Display new registration form
        form = UserCreationForm()
    else:
        #Process complete form
        form = UserCreationForm(data=request.POST)

        if form.is_valid():
            new_user = form.save()
            #log the user in and redirect to homepage
            login(request,new_user)
            return redirect('keep_inventory:index')
        
    #Display a blank or invalid form
    context = {'form': form}
    return render(request, 'registration/register.html', context)


