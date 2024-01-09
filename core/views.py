from django.shortcuts import render, redirect
# from django.http import HttpResponse, Http404
from django.contrib.auth.models import User, auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from .models import Profile, Post, Like_Post

@login_required(login_url='signin')
def index(request):
    user = request.user
    user_profile = Profile.objects.get(user=user)
    posts = Post.objects.all()

    return render(request, 'index.html', {'user_profile': user_profile, 'posts': posts})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email is taken')
                return redirect('signup')
            
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username taken')
                return redirect('signup')
            
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log user in and direct to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                # create a profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user = user_model, id_user = user_model.id)
                new_profile.save()

                return redirect('settings')

        else: 
            messages.info(request, "passwords don't match")
            return redirect('signup')
        
    else:
        return render(request, 'signup.html')

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username = username, password = password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        
        else:
            messages.info(request, 'Credentials invalid')
            return redirect('signin')

    else:
        return render(request, 'signin.html')

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin') 
def settings(request):

    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        bio = request.POST['bio']
        location = request.POST['location']
        image = None 

        if request.FILES.get('image') == None:
            image = user_profile.profileimg 
        else:
            image = request.FILES.get('image')

        user_profile.profileimg = image
        user_profile.bio = bio 
        user_profile.location = location
        user_profile.save()

        return redirect('settings')

    else:
        return render(request, 'settings.html', {'user_profile': user_profile})

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image, caption=caption)

        new_post.save()

        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='signin')
def like_post(request):
    username=request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id) 

    like_filter = Like_Post.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = Like_Post.objects.create(post_id=post_id, username=username)
        new_like.save()

        post.no_of_likes = post.no_of_likes + 1
        post.save()

        return redirect('/')

    else:
        like_filter.delete()
        post.no_of_likes -= 1
        post.save()
        return redirect('/')
    
@login_required
def profile(request, pk):
    user_object = User.objects.filter(username=pk).first()
    if user_object is None:
        return redirect('/')
    user_profile = Profile.objects.get(user=user_object)

    user_posts = Post.objects.filter(user=pk)
    user_posts_length = len(Post.objects.filter(user=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_posts_length': user_posts_length,
    }

    return render(request, 'profile.html', context)