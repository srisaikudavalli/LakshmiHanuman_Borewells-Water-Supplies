import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Service(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='services/', blank=True, null=True) 

    def __str__(self):
        return self.title

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
    ]
    
    customer_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=200)
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"{self.customer_name} - {self.phone_number}"

# This is the new part causing the error!
class Review(models.Model):
    customer_name = models.CharField(max_length=100)
    comment = models.TextField()
    rating = models.IntegerField(default=5, help_text="1 to 5 stars")
    
    def __str__(self):
        return f"{self.customer_name} ({self.rating} stars)"
    # Add this at the bottom
class GalleryItem(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='gallery/') # Can be image OR video
    
    def __str__(self):
        return self.title

    # This logic checks if the file is a video
    def is_video(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower() in ['.mp4', '.mov', '.avi', '.kv']
    # --- WORKER MANAGEMENT MODELS ---

class Worker(models.Model):
    ROLE_CHOICES = [
        ('Driller', 'Driller'),
        ('Helper', 'Helper'),
        ('Driver', 'Driver'),
        ('Manager', 'Manager'),
    ]
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    daily_wage = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in Rupees")
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.name} ({self.role})"

class Attendance(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateField() # Removed 'auto_now_add' so we can choose dates manually
    status = models.CharField(max_length=10, default='Present')
    
    class Meta:
        # This is the MAGIC LINE. It prevents duplicate entries for the same worker on the same day.
        unique_together = ('worker', 'date')

    def __str__(self):
        return f"{self.worker.name} - {self.date}"
    
class Advance(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=200, blank=True, help_text="Optional reason")

    def __str__(self):
        return f"{self.worker.name} - ₹{self.amount} on {self.date}"
    
# --- USER PROFILE EXTENSION ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to automatically create/save profile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()