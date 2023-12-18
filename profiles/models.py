from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    A user profile model for maintaining user information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    street_address1 = models.CharField(max_length=80, null=True, blank=True)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    country = CountryField(blank_label='Country', null=True, blank=True)

    def __str__(self):
        return self.user.username

    def get_full_address(self):
        """
        Get the user's full address as a formatted string.
        """
        address_parts = [
            self.street_address1,
            self.street_address2,
            self.town_or_city,
            self.county,
            self.postcode,
            str(self.country),
        ]
        return ', '.join(filter(None, address_parts))

    def get_profile_image_url(self):
        """
        Get the URL for the user's profile image, or a default image if not set.
        """
        if self.profile_image:
            return self.profile_image.url
        else:
            return 'https://gearupp.s3.eu-west-1.amazonaws.com/media/profile_images/default_profile_image.jpg'

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile.
    """
    if created:
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile
    instance.userprofile.save()
