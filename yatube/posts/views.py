from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.urls import reverse
from .utils.paginate import paginate
from .models import Group, Post, Follow
from .forms import PostForm, CommentForm

User = get_user_model()


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    page_obj = paginate(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginate(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = User.objects.get(username=username)
    posts = Post.objects.filter(author=author)
    page_obj = paginate(request, posts)
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': False
    }
    if request.user.is_authenticated:
        context['following'] = Follow.objects.filter(
            user=request.user).filter(author=author).exists()
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    template = 'posts/create_post.html'
    if not form.is_valid():
        return render(request, template, {'form': form})
    else:
        user = get_object_or_404(User, username=request.user.username)
        post = form.save(commit=False)
        post.text = form.cleaned_data['text']
        post.author = user
        post.group = form.cleaned_data['group']
        post.save()
        return redirect('posts:profile', username=user.username)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = get_object_or_404(User, id=request.user.id)
    authors = user.follower.all()
    posts = Post.objects.filter(author__following__in=authors)
    page_obj = paginate(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author)
    return redirect(reverse('posts:profile',
                            kwargs={'username': username}))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    get_object_or_404(Follow,
                      user=request.user,
                      author=author).delete()
    return redirect(reverse('posts:profile',
                            kwargs={'username': username}))
