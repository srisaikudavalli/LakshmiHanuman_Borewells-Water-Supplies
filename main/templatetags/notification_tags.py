import json
from django import template
from django.db.models import Count
from django.db.models.functions import TruncDay
from main.models import Booking

register = template.Library()

@register.simple_tag
def count_pending_orders():
    return Booking.objects.filter(status='PENDING').count()

@register.simple_tag
def get_service_data():
    # Count bookings for each service (For Pie Chart)
    # Returns: [{'service__title': '6.5 Inch', 'count': 5}, ...]
    data = Booking.objects.values('service__title').annotate(count=Count('id'))
    
    # Convert to simple lists for Javascript
    labels = [item['service__title'] for item in data]
    counts = [item['count'] for item in data]
    
    return json.dumps({'labels': labels, 'counts': counts})

@register.simple_tag
def get_daily_bookings():
    # Count bookings per day (For Bar Chart)
    data = Booking.objects.annotate(day=TruncDay('date_ordered')).values('day').annotate(count=Count('id')).order_by('day')
    
    labels = [item['day'].strftime('%Y-%m-%d') for item in data]
    counts = [item['count'] for item in data]
    
    return json.dumps({'labels': labels, 'counts': counts})