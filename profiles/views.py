from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
from .models import UserProfile
from PIL import Image

@login_required
def profile_detail(request):
    """
    View for displaying the user's profile details.
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if created:
        user_profile.save()

    return render(request, 'profiles/profile_detail.html', {'user_profile': user_profile})

@login_required
def profile_update(request):
    """
    View for updating the user's profile information.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            user_profile = form.save(commit=False)

            # Resize the profile image if it's updated
            desired_size = (150, 150)
            if 'profile_image' in request.FILES:
                img = Image.open(user_profile.profile_image)
                img.thumbnail(desired_size, Image.LANCZOS)
                img.save(user_profile.profile_image.path)

            user_profile.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile_detail')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'profiles/profile_update.html', {'form': form})
