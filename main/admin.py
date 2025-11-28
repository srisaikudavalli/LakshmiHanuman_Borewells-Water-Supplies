from django.contrib import admin
from .models import Service, Booking, Review, GalleryItem  # <-- Changed Video to GalleryItem
# Add Advance to the import list
from .models import Service, Booking, Review, GalleryItem, Worker, Attendance, Advance 

admin.site.register(Worker)
admin.site.register(Attendance)
admin.site.register(Advance) # <--- New Line

admin.site.register(Service)
admin.site.register(Review)
admin.site.register(GalleryItem)  # <-- Register the new name

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    # ... (keep your existing code here) ...
    pass