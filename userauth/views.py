from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def home(request):
    return render(request, "auth/index.html")

def signup(request):
    if request.method == 'POST':
        # take all field entered by user so we cam work with them on backend

        # username = request.POST.get('username')
        username = request.POST['username']
        firstname = request.POST['fname']
        lastname = request.POST['lname']
        email = request.POST['email']
        password = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        # creating user in database
        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = firstname
        myuser.last_name = lastname 

        # saving in database
        myuser.save()

        # displaying messages when account has been created in database
        messages.success(request, "Your account has been successfully created.")

        # now redirecting them to signin page
        return redirect('signin')


    return render(request, "auth/signup.html")

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            # messages.success(request, "Logged In Sucessfully!!")
            return render(request, "auth/index.html",{"fname":fname})
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')

        
    return render(request, "auth/login.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')