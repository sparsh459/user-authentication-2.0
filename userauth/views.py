from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from user_auth import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from . tokens import generate_token
from django.utils.encoding import force_text
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

        # defining some parameter for user to follow while making account
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('home')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('home')
        
        if len(username)>20:
            messages.error(request, "Username must be under 20 charcters!!")
            return redirect('home')
        
        if password != pass2:
            messages.error(request, "Passwords didn't matched!!")
            return redirect('home')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('home')
        
        # creating user in database
        myuser = User.objects.create_user(username, email, password)
        myuser.first_name = firstname
        myuser.last_name = lastname 
        #account of user is not activated
        myuser.is_active = False
        # saving in database
        myuser.save()

        # displaying messages when account has been created in database
        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")
        
        # Welcome Email
        subject = "Welcome to Django Login!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to our Space!! \nThank you for visiting our website.\n We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\n$p@r$h\nCEO of nothing"        
        # the email we will be using to send it to teh the new user
        from_email = settings.EMAIL_HOST_USER
        # the user email
        to_list = [myuser.email]
        # fail_silently is used for the purpose that if teh email is not send, teh app should not crash 
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # email for confiramtion of the account activation
        current_site = get_current_site(request)  # it will traget the diamin of teh current site
        email_subject = "Confirm your Email @ Authentication - Django Login!!"
        # the email_confirmation.html is the template to be used for every time confimation email is sent
        # ("email_confirmation.html", {dict})
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            # getting user id
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            # generating token with help of tokens.py
            'token': generate_token.make_token(myuser)
        })
        # creating an email object
        email = EmailMessage(
        email_subject,
        message2,
        # person sending the mail
        settings.EMAIL_HOST_USER,
        # person to whom the mail is to be send
        [myuser.email],
        )
        email.fail_silently = True
        email.send()
        # now redirecting them to signin page
        return redirect('signin')


    return render(request, "auth/signup.html")

# for activating the account
def activate(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        # fetching 
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        messages.error(request, "Your Account activation failed!!")
        return redirect('signup')


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