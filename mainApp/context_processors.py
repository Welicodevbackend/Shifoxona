
# context_processors.py
from .models import ContactMessage

def unread_messages(request):
    if request.user.is_authenticated:
        # Faqat is_read=False bo'lgan xabarlar sonini hisoblaymiz
        count = ContactMessage.objects.filter(is_read=False).count()
        return {'unread_count': count}
    return {'unread_count': 0}

from .models import OnlineAppointment

def online_appointments_count(request):
    if request.user.is_authenticated:
        # is_confirmed=False bo'lgan yangi navbatlarni sanaymiz
        count = OnlineAppointment.objects.filter(is_confirmed=False).count()
        return {'new_appointments_count': count}
    return {'new_appointments_count': 0}


from .models import Appointment, OnlineAppointment
from django.utils import timezone


def doctor_appointments_count(request):
    if request.user.is_authenticated and hasattr(request.user, 'staff_profile'):
        staff = request.user.staff_profile
        if staff.role == 'doctor':
            today = timezone.now().date()
            # Bugungi va kelajakdagi yangi navbatlar
            c1 = Appointment.objects.filter(doctor=staff, date__gte=today, status='waiting').count()
            c2 = OnlineAppointment.objects.filter(doctor=staff, date__gte=today, is_confirmed=False).count()

            return {
                'today_my_apps_count': c1 + c2  # SHU NOM TO'G'RI BO'LISHI SHART
            }
    return {'today_my_apps_count': 0}