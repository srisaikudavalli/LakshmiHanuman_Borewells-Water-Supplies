"""
URL configuration for borewell_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings            # <-- NEW IMPORT
from django.conf.urls.static import static  # <-- NEW IMPORT
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ROOT URL points directly to the Website now
    path('', views.home, name='home'),
    
    path('book/', views.book_service, name='book'),
    path('success/', views.success, name='success'),
    path('review/', views.add_review, name='add_review'),
    path('workers/', views.worker_dashboard, name='worker_dashboard'),
    
    # We can keep these for Admin login purposes if you want, 
    # or you can just use /admin/ path. 
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
]

# This tells Django: "If DEBUG mode is on, serve media files from MEDIA_ROOT"
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)