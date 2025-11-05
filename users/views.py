from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

def register(request):
    """Register a new user"""
    if request.method !='POST':
        #Display new registration form
        new_registration_form = UserCreationForm()
    else:
        #Process complete form
        new_registration_form = UserCreationForm(request.POST)

        if new_registration_form.is_valid():
            new_user = new_registration_form.save()
            #log the user in and redirect to homepage
            login(request,new_user)
            return redirect('keep_inventory:index')
        
    #Display a blank or invalid form
    context = {'new_registration_form':new_registration_form}
    return render(request, 'registration/register.html', context)


