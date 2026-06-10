from django.shortcuts import render,redirect
from mainApp.models import *
import random
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.contrib import messages
import datetime
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q,F
from django.contrib.auth import authenticate, update_session_auth_hash
# from google import genai

from django.http import JsonResponse
from .models import Department
import traceback
# from google import genai
import requests
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy






from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .models import *  # Barcha modellar
from django.contrib.auth import logout
from django.template.loader import render_to_string
from django.db.models import Sum
from .forms import *
from django.core.mail import send_mail

from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate, login


def doctor_dashboard_login(request):
    # 1. Agar foydalanuvchi allaqachon login qilgan bo'lsa
    if request.user.is_authenticated:
        staff = getattr(request.user, 'staff_profile', None)

        # Agar u shifokor bo'lsa, to'g'ri dashboardga yuboramiz
        if staff and staff.role == 'doctor':
            return redirect('doctor_dashboard')

        # Agar u boshqa rol bo'lsa (masalan, reception), uni logout qilib
        # shifokor sifatida qayta kirishiga imkon beramiz
        else:
            logout(request)
            messages.info(request, "Siz shifokor emassiz. Iltimos, shifokor profili bilan kiring.")
            return redirect('doctor_dashboard_login')

    # 2. POST so'rovi kelganda (Forma to'ldirilganda)
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')

        user = authenticate(username=u, password=p)

        if user is not None:
            staff_profile = getattr(user, 'staff_profile', None)

            # Faqat shifokor roliga ega xodimlarni o'tkazamiz
            if staff_profile and staff_profile.role == 'doctor':
                login(request, user)
                return redirect('doctor_dashboard')
            else:
                messages.error(request, "Kirish taqiqlandi! Bu panel faqat shifokorlar uchun.")
                return redirect('doctor_dashboard_login')
        else:
            messages.error(request, "Login yoki parol xato!")

    return render(request, 'registration/doctor_login.html')


def doctor_dashboard_index(request):
    """Shifokorning asosiy ishchi muhiti"""
    staff_profile = getattr(request.user, 'staff_profile', None)

    # Xavfsizlik: Agar shifokor bo'lmasa, login sahifasiga qaytarish
    if not (staff_profile and staff_profile.role == 'doctor'):
        messages.warning(request, "Iltimos, avval tizimga kiring.")
        return redirect('doctor_dashboard_login')

    # Statistik ma'lumotlar (Sidebar uchun)
    today = timezone.now().date()

    # Bugungi navbatlarni hisoblash
    today_my_apps_count = Appointment.objects.filter(
        doctor=staff_profile,
        date=today
    ).count() + OnlineAppointment.objects.filter(
        doctor=staff_profile,
        date=today
    ).count()

    context = {
        'staff_user': staff_profile,
        'today_my_apps_count': today_my_apps_count,
    }
    return render(request, 'admin_panel/doctor_dashboard.html', context)





















@login_required
def reception_admin_dashboard(request):
    staff_profile = getattr(request.user, 'staff_profile', None)
    if not (staff_profile and staff_profile.role in ['reception', 'admin']):
        return redirect('home')

    today = timezone.now().date()

    # 1. KPI ma'lumotlari
    online_count = OnlineAppointment.objects.filter(date=today).count()
    offline_count = Appointment.objects.filter(date=today).count()
    today_revenue = Payment.objects.filter(created_at__date=today, is_paid=True).aggregate(total=Sum('amount'))[
                        'total'] or 0

    # 2. Grafiklar: Haftalik tendentsiya
    last_7_days, daily_counts = [], []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        last_7_days.append(day.strftime('%d-%b'))
        c = (Appointment.objects.filter(date=day).count() + OnlineAppointment.objects.filter(date=day).count())
        daily_counts.append(c)
    payment_stats = Payment.objects.filter(created_at__date=today, is_paid=True).values('payment_type').annotate(
        count=Count('id'))

    # 4. Grafik: Bo'limlar bandligi (Top 5)
    dept_stats = Department.objects.annotate(
        app_count=Count('appointment', filter=Q(appointment__date=today))
    ).order_by('-app_count')[:5]

    # 5. Grafik: Kunlik bandlik soatlari (Peak Hours)
    # 08:00 dan 18:00 gacha bo'lgan vaqt oralig'i
    hours = [f"{h:02d}:00" for h in range(8, 19)]
    hourly_data = [Appointment.objects.filter(date=today, time_slot__hour=h).count() for h in range(8, 19)]

    context = {
        'today_apps_count': online_count + offline_count,
        'patients_count': Patient.objects.count(),
        'today_revenue': today_revenue,
        'chart_labels': last_7_days,
        'chart_data': daily_counts,
        'dept_labels': [d.name for d in dept_stats] if dept_stats else ["Ma'lumot yo'q"],
        'dept_data': [d.app_count for d in dept_stats] if dept_stats else [0],
        'payment_labels': [p['payment_type'].capitalize() for p in payment_stats] or ["Hali yo'q"],
        'payment_values': [p['count'] for p in payment_stats] or [0],
        'hour_labels': hours,
        'hour_data': hourly_data,
        'unread_count': ContactMessage.objects.filter(is_read=False).count(),
        'new_appointments_count': OnlineAppointment.objects.filter(is_confirmed=False).count(),
    }

    colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796']

    context.update({
        'chart_colors': colors,
        # Bo'limlar statistikasi agar 0 bo'lsa, foydalanuvchiga "Ma'lumot mavjud emas" deb chiroyli ko'rsatamiz
        'has_dept_data': any(d > 0 for d in context['dept_data']),
    })
    return render(request, 'admin_panel/dashboard_index.html', context)





@login_required
def change_password_verify(request):
    if request.method == 'POST':
        password = request.POST.get('current_password')
        user = authenticate(username=request.user.username, password=password)

        if user is not None:
            request.session['verified_for_action'] = True  # Vaqtinchalik ruxsat
            return redirect('actual_change_password')
        else:
            messages.error(request, "Eski parol noto'g'ri!")

    return render(request, 'admin_panel/verify_action.html', {'title': 'Parolni o\'zgartirishni tasdiqlang'})


@login_required
def profile_verify(request):
    # Agar foydalanuvchi allaqachon tekshiruvdan o'tgan bo'lsa, to'g'ri tahrirlashga yuboramiz
    if request.session.get('verified_for_profile'):
        return redirect('profile_edit')

    if request.method == 'POST':
        password = request.POST.get('current_password')

        # Foydalanuvchini paroli orqali qayta tekshiramiz
        user = authenticate(username=request.user.username, password=password)

        if user is not None:
            # Sessiyaga vaqtinchalik ruxsatnoma yozamiz
            request.session['verified_for_profile'] = True
            # Profilni tahrirlash sahifasiga yuboramiz
            return redirect('profile_edit')
        else:
            messages.error(request, "Kiritilgan parol noto'g'ri! Iltimos, qaytadan urinib ko'ring.")

    # Xuddi o'sha verify_action.html sahifasini ishlatamiz, faqat sarlavha o'zgaradi
    return render(request, 'admin_panel/verify_action.html', {
        'title': 'Profilga kirishni tasdiqlang'
    })
# 2. Haqiqiy parol o'zgartirish viewsi
@login_required
def actual_change_password(request):
    if not request.session.get('verified_for_action'):
        return redirect('change_password_verify')

    if request.method == 'POST':
        new_pass = request.POST.get('new_password')
        request.user.set_password(new_pass)
        request.user.save()
        update_session_auth_hash(request, request.user)  # Session o'chib ketmasligi uchun
        del request.session['verified_for_action']
        messages.success(request, "Parol muvaffaqiyatli yangilandi!")
        return redirect('reception_dash')

    return render(request, 'admin_panel/change_password.html')


# 3. Profil tahrirlash viewsi
@login_required
def profile_edit(request):
    if not request.session.get('verified_for_profile'):
        return redirect('profile_verify')

    # Foydalanuvchiga tegishli Staff profilini olamiz
    staff_profile = getattr(request.user, 'staff_profile', None)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        # HTML formadagi name="image" orqali rasmni olamiz
        new_image = request.FILES.get('image')

        if staff_profile:
            # Ismni yangilash
            staff_profile.full_name = full_name

            # AGAR yangi rasm yuklangan bo'lsa, uni photo maydoniga saqlash
            if new_image:
                staff_profile.photo = new_image  # Modeldagi maydon nomi 'photo'

            staff_profile.save()  # Bazaga saqlash

            del request.session['verified_for_profile']
            messages.success(request, "Profil ma'lumotlari muvaffaqiyatli yangilandi!")
            return redirect('reception_dash')

    return render(request, 'admin_panel/profile_edit.html', {
        'profile': staff_profile
    })


from django.core.exceptions import PermissionDenied

@login_required(login_url='doctor_dashboard_login')
def doctor_departments_list(request):
    staff = getattr(request.user, 'staff_profile', None)
    if not staff or staff.role != 'doctor':
        messages.error(request, "Ushbu sahifaga kirish uchun shifokor ruxsati kerak!")
        return redirect('/doctor_admin/login/')
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-created_at')

    departments = Department.objects.all()

    if search_query:
        departments = departments.filter(name__icontains=search_query)

    departments = departments.order_by(sort_by)

    # Agar so'rov AJAX (Fetch) orqali kelayotgan bo'lsa
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/doctor_department_table.html', {
            'departments': departments
        })

    return render(request, 'admin_panel/doctor_departments.html', {
        'departments': departments,
        'search_query': search_query,
        'sort_by': sort_by
    })




@login_required(login_url='doctor_dashboard_login')
def doctor_department_detail(request, pk):
    # ID bo'yicha bitta bo'limni o'zini ko'rish (Detail view)
    department = get_object_or_404(Department, pk=pk)
    return render(request, 'admin_panel/doctor_department_detail.html', {
        'department': department
    })

@login_required(login_url='doctor_dashboard_login')
def doctor_services_list(request):
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-created_at')

    services = Service.objects.all()

    # Nomi yoki Bo'lim nomi bo'yicha qidirish
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

    services = services.order_by(sort_by)

    # AJAX so'rov bo'lsa, faqat jadval qismini qaytarish
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/service_table.html', {
            'services': services
        })

    return render(request, 'admin_panel/doctor_services.html', {
        'services': services,
        'search_query': search_query,
        'sort_by': sort_by
    })

@login_required(login_url='doctor_dashboard_login')
def doctor_service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'admin_panel/doctor_service_detail.html', {
        'service': service
    })

@login_required(login_url='doctor_dashboard_login')
def doctor_lab_tests_list_dashboard(request):
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-created_at')

    lab_tests = LabTest.objects.all()

    if search_query:
        lab_tests = lab_tests.filter(name__icontains=search_query)

    lab_tests = lab_tests.order_by(sort_by)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/doctor_lab_test_table.html', {
            'lab_tests': lab_tests
        })

    return render(request, 'admin_panel/doctor_lab_tests.html', {
        'lab_tests': lab_tests,
        'search_query': search_query,
        'sort_by': sort_by
    })



@login_required(login_url='doctor_dashboard_login')
def doctor_lab_test_detail_dashboard(request, pk):
    lab_test = get_object_or_404(LabTest, pk=pk)
    return render(request, 'admin_panel/doctor_lab_test_detail.html', {
        'lab_test': lab_test
    })


@login_required(login_url='doctor_dashboard_login')
def doctor_medical_records_list(request):
    staff = getattr(request.user, 'staff_profile', None)
    if not staff or staff.role != 'doctor':
        messages.error(request, "Ushbu sahifaga kirish uchun shifokor ruxsati kerak!")
        return redirect('/doctor_admin/login/')

    query = request.GET.get('q', '')
    # Shifokor faqat o'ziga tegishli bemorlar tarixini ko'radi
    records = MedicalRecord.objects.filter(doctor=staff).select_related('patient')

    if query:
        records = records.filter(
            Q(patient__full_name__icontains=query) |
            Q(diagnosis__icontains=query)
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/doctor_medical_records_table.html', {'records': records})

    return render(request, 'admin_panel/doctor_medical_records.html', {
        'records': records,
        'query': query
    })


# 2. Yangi karta yaratish
@login_required(login_url='doctor_dashboard_login')
def doctor_medical_record_create(request):
    staff = getattr(request.user, 'staff_profile', None)
    if not staff or staff.role != 'doctor':
        messages.error(request, "Ushbu sahifaga kirish uchun shifokor ruxsati kerak!")
        return redirect('/doctor_admin/login/')

    if request.method == 'POST':
        patient_id = request.POST.get('patient')
        diagnosis = request.POST.get('diagnosis')
        prescription = request.POST.get('prescription')

        patient = get_object_or_404(Patient, id=patient_id)

        MedicalRecord.objects.create(
            patient=patient,
            doctor=staff,
            diagnosis=diagnosis,
            prescription=prescription
        )
        messages.success(request, "Tibbiy karta muvaffaqiyatli saqlandi!")
        return redirect('doctor_medical_records_list')

    patients = Patient.objects.all()
    return render(request, 'admin_panel/doctor_medical_record_form.html', {'patients': patients})


# 3. Kartani tahrirlash
@login_required(login_url='doctor_dashboard_login')
def doctor_medical_record_edit(request, pk):
    staff = getattr(request.user, 'staff_profile', None)
    record = get_object_or_404(MedicalRecord, pk=pk)

    if record.doctor != staff:
        messages.warning(request, "Ushbu sahifaga kirish uchun shifokor sifatida kiring.")
        return redirect('doctor_dashboard_login')

    if request.method == 'POST':
        record.diagnosis = request.POST.get('diagnosis')
        record.prescription = request.POST.get('prescription')
        record.save()
        messages.success(request, "Ma'lumotlar yangilandi.")
        return redirect('doctor_medical_records_list')

    return render(request, 'admin_panel/doctor_medical_record_form.html', {'record': record})


# 4. Kartani o'chirish
@login_required(login_url='doctor_dashboard_login')
def doctor_medical_record_delete(request, pk):
    staff = getattr(request.user, 'staff_profile', None)
    record = get_object_or_404(MedicalRecord, pk=pk)

    if record.doctor != staff:
        messages.warning(request, "Ushbu sahifaga kirish uchun shifokor sifatida kiring.")
        return redirect('doctor_dashboard_login')

    if request.method == 'POST':
        record.delete()
        messages.success(request, "Karta o'chirildi.")

    return redirect('doctor_medical_records_list')










@login_required(login_url='doctor_dashboard_login')
def doctor_patients_list_dashboard(request):
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-created_at') # Default: yangi qo'shilganlar

    patients = Patient.objects.all().order_by(sort_by)

    if search_query:
        patients = patients.filter(
            Q(full_name__icontains=search_query) | Q(phone__icontains=search_query)
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/doctor_patient_table.html', {'patients': patients})

    return render(request, 'admin_panel/doctor_patients.html', {
        'patients': patients,
        'form': PatientForm() # Bemor qo'shish uchun form
    })


@login_required(login_url='doctor_dashboard_login')
def doctor_patient_create_dashboard(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"{patient.full_name} muvaffaqiyatli qo'shildi!")
            return redirect('doctor_patients_list_dashboard') # Ismni tekshiring (URL-dagi name)
        else:
            # Formada xato bo'lsa, xabarlarni chiqarish
            for error in form.errors.values():
                messages.error(request, error)
    return redirect('doctor_patients_list_dashboard')


@login_required(login_url='doctor_dashboard_login')
def doctor_patient_edit_dashboard(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f"{patient.full_name} muvaffaqiyatli o'zgartirildi!")
            return redirect('patients_list_dashboard')
    else:
        form = PatientForm(instance=patient)

    # Agar AJAX so'rovi bo'lsa, faqat formni qaytaramiz
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/doctor_patient_edit_form.html', {'form': form, 'patient': patient})

    return render(request, 'admin_panel/doctor_patient_edit.html', {'form': form, 'patient': patient})


@login_required(login_url='doctor_dashboard_login')
def doctor_patient_delete_dashboard(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':  # <--- Shu qatorni tekshiring
        name = patient.full_name
        patient.delete()
        messages.error(request, f"{name} bazadan o'chirildi!")
        return redirect('patients_list_dashboard') # <--- Redirect borligini tekshiring
    return redirect('patients_list_dashboard')


@login_required(login_url='doctor_dashboard_login')
def doctor_patient_detail_dashboard(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'admin_panel/doctor_patient_detail.html', {'patient': patient})







from operator import attrgetter
from itertools import chain


@login_required(login_url='doctor_dashboard_login')
def doctor_my_appointments(request):
    # 1. Xavfsizlik: Profilni tekshirish
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, "Profil topilmadi!")
        return redirect('doctor_dashboard_login')

    staff = request.user.staff_profile

    # 2. Rolni tekshirish (Katta-kichik harfga chidamli variant)
    if str(staff.role).lower().strip() != 'doctor':
        return redirect('doctor_dashboard')

    today = timezone.now().date()

    try:
        # 3. 'patient'ni select_related'dan olib tashladik, chunki u ForeignKey emas
        apps = Appointment.objects.filter(
            doctor=staff,
            date__gte=today
        ).select_related('service', 'department')

        # 4. Online navbatlarni olish
        online_apps = OnlineAppointment.objects.filter(
            doctor=staff,
            date__gte=today
        )

        # 5. Birlashtirish va saralash
        combined_appointments = sorted(
            chain(apps, online_apps),
            key=attrgetter('date', 'time_slot')
        )

        # 6. Bugungi navbatlar soni
        today_my_apps_count = apps.filter(date=today).count() + online_apps.filter(date=today).count()

        context = {
            'appointments': combined_appointments,
            'today': today,
            'today_my_apps_count': today_my_apps_count,
            'staff_user': staff,
        }

        return render(request, 'admin_panel/doctor_appointments.html', context)

    except Exception as e:
        messages.error(request, f"Xatolik yuz berdi: {str(e)}")
        return redirect('doctor_dashboard')




# @login_required(login_url='doctor_dashboard_login')
# def doctor_my_appointments(request):
#     """
#     Shifokorga tegishli barcha (klinika va online) navbatlarni
#     birlashtirib, vaqti bo'yicha ko'rsatuvchi asosiy sahifa.
#     """
#
#     # 1. Xavfsizlik: Foydalanuvchida staff_profile borligini tekshiramiz
#     # Bu superuser yoki profil biriktirilmagan foydalanuvchilar kirsa xato bermasligi uchun
#     if not hasattr(request.user, 'staff_profile'):
#         messages.error(request, "Sizning foydalanuvchi hisobingizga xodim profili biriktirilmagan!")
#         return redirect('doctor_dashboard_login')
#
#     staff = request.user.staff_profile
#
#     # 2. Rolni tekshirish: Faqat shifokorlar kira olishini ta'minlaymiz
#     if staff.role != 'doctor':
#         messages.warning(request, "Ushbu sahifa faqat shifokorlar uchun mo'ljallangan!")
#         return redirect('home')
#
#     today = timezone.now().date()
#
#     try:
#         # 3. Oddiy klinik navbatlarni olish (faqat shu shifokorga tegishli va bugundan keyingi)
#         apps = Appointment.objects.filter(
#             doctor=staff,
#             date__gte=today
#         ).select_related('patient', 'service')  # Performance uchun select_related qo'shildi
#
#         # 4. Online navbatlarni olish
#         online_apps = OnlineAppointment.objects.filter(
#             doctor=staff,
#             date__gte=today
#         )
#
#         # 5. Ikkala ro'yxatni birlashtirish va vaqti hamda sanasi bo'yicha saralash
#         combined_appointments = sorted(
#             chain(apps, online_apps),
#             key=attrgetter('date', 'time_slot')
#         )
#
#         # 6. Sidebar uchun bugungi navbatlar sonini hisoblash
#         today_my_apps_count = apps.filter(date=today).count() + online_apps.filter(date=today).count()
#
#         context = {
#             'appointments': combined_appointments,
#             'today': today,
#             'today_my_apps_count': today_my_apps_count,
#             'staff_user': staff,
#         }
#
#         return render(request, 'admin_panel/doctor_appointments.html', context)
#
#     except Exception as e:
#         # Kutilmagan xatolar yuz bersa (masalan bazada muammo)
#         messages.error(request, f"Ma'lumotlarni yuklashda xatolik yuz berdi: {str(e)}")
#         return redirect('doctor_dashboard_login')


@login_required(login_url='doctor_dashboard_login')
def check_new_appointments(request):
    """
    Sidebar uchun: Har 10 soniyada yangi navbatlar sonini
    hisoblab qaytaruvchi API view.
    """
    if not hasattr(request.user, 'staff_profile'):
        return JsonResponse({'count': 0})

    staff = request.user.staff_profile
    today = timezone.now().date()

    # Klinika navbatlari (faqat kutilayotganlari)
    count_app = Appointment.objects.filter(
        doctor=staff,
        date=today,
        status='waiting'
    ).count()

    # Online navbatlar (faqat tasdiqlanmaganlari)
    count_online = OnlineAppointment.objects.filter(
        doctor=staff,
        date=today,
        is_confirmed=False
    ).count()

    return JsonResponse({'count': count_app + count_online})


@login_required(login_url='doctor_dashboard_login')
def mark_as_received(request, app_id, app_type):
    if app_type == 'clinic':
        appointment = get_object_or_404(Appointment, id=app_id, doctor__user=request.user)
        appointment.status = 'received'
        appointment.save()
    else:  # online
        appointment = get_object_or_404(OnlineAppointment, id=app_id, doctor__user=request.user)
        appointment.is_confirmed = True
        appointment.save()

    return JsonResponse({'status': 'success'})


@login_required(login_url='doctor_dashboard_login')
def doctor_admin_dashboard(request):
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, "Sizning hisobingizda shifokor profili topilmadi. Iltimos, admin bilan bog'laning.")
        return redirect('home')  # Yoki boshqa xavfsiz sahifaga

    staff = request.user.staff_profile
    today = timezone.now().date()

    # 1. Umumiy ko'rsatkichlar (Kichik kartalar uchun)
    total_patients = Appointment.objects.filter(doctor=staff).count() + \
                     OnlineAppointment.objects.filter(doctor=staff).count()

    today_apps = Appointment.objects.filter(doctor=staff, date=today).count() + \
                 OnlineAppointment.objects.filter(doctor=staff, date=today).count()

    # 2. Haftalik statistika (Grafik uchun)
    last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    labels = [day.strftime('%d-%b') for day in last_7_days]

    data_values = []
    for day in last_7_days:
        count = Appointment.objects.filter(doctor=staff, date=day).count() + \
                OnlineAppointment.objects.filter(doctor=staff, date=day).count()
        data_values.append(count)

    # 3. Manba bo'yicha taqsimot (Pirog grafik uchun)
    clinic_count = Appointment.objects.filter(doctor=staff).count()
    online_count = OnlineAppointment.objects.filter(doctor=staff).count()

    context = {
        'total_patients': total_patients,
        'today_apps': today_apps,
        'labels': labels,
        'data_values': data_values,
        'clinic_count': clinic_count,
        'online_count': online_count,
    }
    return render(request, 'admin_panel/doctor_admin_dashboard.html', context)

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required


@login_required(login_url='doctor_dashboard_login')
def doctor_admin_profile_edit(request):
    # Modelda Staff deb nomlangan, shuning uchun hasattr tekshiruvi:
    if not hasattr(request.user, 'staff_profile'):
        messages.error(request, "Sizda shifokor profili mavjud emas!")
        return redirect('home')

    staff = request.user.staff_profile

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_input = request.POST.get('phone')  # HTML formadan kelayotgan qiymat

        if full_name and phone_input:
            staff.full_name = full_name
            # MODELINGIZDA maydon nomi 'phone', shuning uchun:
            staff.phone = phone_input
            staff.save()

            # Muvaffaqiyatli xabari
            messages.success(request, "Profilingiz muvaffaqiyatli yangilandi!")
            # Faqat dashboard sahifasiga qaytaramiz
            return redirect('doctor_admin_dashboard')
        else:
            messages.error(request, "Iltimos, barcha maydonlarni to'ldiring!")

    return render(request, 'admin_panel/doctor_admin_profile_edit.html', {'staff': staff})


@login_required(login_url='doctor_dashboard_login')
def doctor_admin_security_edit(request):
    """Xavfsizlik (Parol o'zgartirish)"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Parol muvaffaqiyatli o'zgartirildi!")
            return redirect('doctor_admin_dashboard')
        else:
            messages.error(request, "Xatolikni tekshiring.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'admin_panel/doctor_admin_security_edit.html', {'form': form})





























































def home_view_admin(request):
    return render(request, 'reseption/admin_index.html')


class MyLoginView(LoginView):
    template_name = 'registration/login.html'
    def get_success_url(self):
        user = self.request.user
        if user.is_superuser: return '/admin/'
        if hasattr(user, 'staff_profile'):
            role = user.staff_profile.role
            return reverse_lazy('reception_dash') if role in ['reception', 'admin'] else reverse_lazy('doctor_dash')
        return reverse_lazy('home')

@login_required
def reception_dashboard(request):
    # Faqat admin va reception kirishi uchun
    staff_profile = getattr(request.user, 'staff_profile', None)

    if request.user.is_superuser or not (staff_profile and staff_profile.role == 'reception'):
        return redirect('home')

    today = timezone.now().date()
    query = request.GET.get('q', '')
    selected_date = request.GET.get('date', today)

    # Online Navbatlar (is_confirmed False bo'lganlar birinchi chiqadi)
    online_appointments = OnlineAppointment.objects.select_related('doctor', 'department').order_by('is_confirmed', 'time_slot')

    if query:
        online_appointments = online_appointments.filter(Q(patient_name__icontains=query) | Q(patient_phone__icontains=query))
    else:
        online_appointments = online_appointments.filter(date=selected_date)

    context = {
        'staff_user': staff_profile,
        'online_appointments': online_appointments,
        'departments_count': Department.objects.count(),
        'patients_count': Patient.objects.count(),
        'today_apps_count': online_appointments.filter(date=today).count(),
        'selected_date': selected_date,
        'query': query,
    }
    return render(request, 'admin_panel/base.html', context)


@login_required
def departments_list(request):
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-created_at')

    departments = Department.objects.all()

    if search_query:
        departments = departments.filter(name__icontains=search_query)

    departments = departments.order_by(sort_by)

    # Agar so'rov AJAX (Fetch) orqali kelayotgan bo'lsa
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/department_table.html', {
            'departments': departments
        })

    return render(request, 'admin_panel/departments.html', {
        'departments': departments,
        'search_query': search_query,
        'sort_by': sort_by
    })


@login_required
def department_detail(request, pk):
    # ID bo'yicha bitta bo'limni o'zini ko'rish (Detail view)
    department = get_object_or_404(Department, pk=pk)
    return render(request, 'admin_panel/department_detail.html', {
        'department': department
    })

@login_required
def services_list(request):
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-created_at')

    services = Service.objects.all()

    # Nomi yoki Bo'lim nomi bo'yicha qidirish
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

    services = services.order_by(sort_by)

    # AJAX so'rov bo'lsa, faqat jadval qismini qaytarish
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/service_table.html', {
            'services': services
        })

    return render(request, 'admin_panel/services.html', {
        'services': services,
        'search_query': search_query,
        'sort_by': sort_by
    })

@login_required
def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'admin_panel/service_detail.html', {
        'service': service
    })

@login_required
def doctors_list_dashboard(request):
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'full_name')

    # Faqat shifokorlarni saralab olamiz
    doctors = Staff.objects.filter(role='doctor')

    # Real-vaqtda qidirish (Ism, Mutaxassislik yoki Bo'lim nomi bo'yicha)
    if search_query:
        doctors = doctors.filter(
            Q(full_name__icontains=search_query) |
            Q(doctor_details__specialization__icontains=search_query) |
            Q(department__name__icontains=search_query)
        )

    doctors = doctors.order_by(sort_by)

    # AJAX so'rov bo'lsa, faqat jadval qismini qaytaramiz
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/doctor_table.html', {
            'doctors': doctors
        })

    return render(request, 'admin_panel/doctors.html', {
        'doctors': doctors,
        'search_query': search_query,
        'sort_by': sort_by
    })

@login_required
def doctor_detail_dashboard(request, pk):
    # Faqat 'doctor' rolidagilarini ID bo'yicha qidiramiz
    doctor = get_object_or_404(Staff, pk=pk, role='doctor')
    return render(request, 'admin_panel/doctor_detail.html', {
        'doctor': doctor
    })


@login_required
def lab_tests_list_dashboard(request):
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-created_at')

    lab_tests = LabTest.objects.all()

    if search_query:
        lab_tests = lab_tests.filter(name__icontains=search_query)

    lab_tests = lab_tests.order_by(sort_by)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/lab_test_table.html', {
            'lab_tests': lab_tests
        })

    return render(request, 'admin_panel/lab_tests.html', {
        'lab_tests': lab_tests,
        'search_query': search_query,
        'sort_by': sort_by
    })

@login_required
def lab_test_detail_dashboard(request, pk):
    lab_test = get_object_or_404(LabTest, pk=pk)
    return render(request, 'admin_panel/lab_test_detail.html', {
        'lab_test': lab_test
    })


@login_required
def patients_list_dashboard(request):
    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '-created_at') # Default: yangi qo'shilganlar

    patients = Patient.objects.all().order_by(sort_by)

    if search_query:
        patients = patients.filter(
            Q(full_name__icontains=search_query) | Q(phone__icontains=search_query)
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/patient_table.html', {'patients': patients})

    return render(request, 'admin_panel/patients.html', {
        'patients': patients,
        'form': PatientForm() # Bemor qo'shish uchun form
    })


@login_required
def patient_create_dashboard(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"{patient.full_name} muvaffaqiyatli qo'shildi!")
            return redirect('patients_list_dashboard')
    return redirect('patients_list_dashboard')


@login_required
def patient_edit_dashboard(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f"{patient.full_name} muvaffaqiyatli o'zgartirildi!")
            return redirect('patients_list_dashboard')
    else:
        form = PatientForm(instance=patient)

    # Agar AJAX so'rovi bo'lsa, faqat formni qaytaramiz
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/patient_edit_form.html', {'form': form, 'patient': patient})

    return render(request, 'admin_panel/patient_edit.html', {'form': form, 'patient': patient})


@login_required
def patient_delete_dashboard(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':  # <--- Shu qatorni tekshiring
        name = patient.full_name
        patient.delete()
        messages.error(request, f"{name} bazadan o'chirildi!")
        return redirect('patients_list_dashboard') # <--- Redirect borligini tekshiring
    return redirect('patients_list_dashboard')


@login_required
def patient_detail_dashboard(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    return render(request, 'admin_panel/patient_detail.html', {'patient': patient})


@login_required
def contact_messages_list(request):
    messages_list = ContactMessage.objects.all().order_by('-created_at')

    # 1. Qidiruv (Ism yoki Mavzu)
    q = request.GET.get('q', '')
    if q:
        messages_list = messages_list.filter(name__icontains=q) | messages_list.filter(subject__icontains=q)

    # 2. Holat bo'yicha filtr (O'qilgan/O'qilmagan)
    status = request.GET.get('status', '')
    if status == 'read':
        messages_list = messages_list.filter(is_read=True)
    elif status == 'unread':
        messages_list = messages_list.filter(is_read=False)

    # 3. Vaqt bo'yicha saralash
    sort = request.GET.get('sort', '-created_at') # Standart: Yangilari tepada
    messages_list = messages_list.order_by(sort)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/contact_table.html', {'contact_messages': messages_list})

    return render(request, 'admin_panel/contacts.html', {'contact_messages': messages_list})

@login_required
def contact_message_detail(request, pk):
    message_item = get_object_or_404(ContactMessage, pk=pk)
    # Avtomatik o'qildi qilish olib tashlandi
    return render(request, 'admin_panel/partials/contact_view_modal.html', {'msg': message_item})


@login_required
def contact_message_delete(request, pk):
    if request.method == 'POST':
        message_item = get_object_or_404(ContactMessage, pk=pk)
        message_item.delete()
        messages.error(request, "Xabar muvaffaqiyatli o'chirildi!")
    return redirect('contact_messages_list')

@login_required
def mark_read_view(request, pk):
    # Xabarni o'qildi qilish
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()

    # Yangi hisobni olish
    new_count = ContactMessage.objects.filter(is_read=False).count()

    return JsonResponse({
        'status': 'success',
        'unread_count': new_count
    })


@login_required
def appointment_list_dashboard(request):
    search_query = request.GET.get('q', '')

    # Bugungi sanani olamiz
    today = timezone.now().date()

    # FAQAT bugungi va kelajakdagi navbatlarni olamiz (date__gte=today)
    appointments = Appointment.objects.filter(date__gte=today).order_by('date', 'time_slot')

    # Qidiruv bo'lsa, o'sha kelajakdagi navbatlar ichidan qidiradi
    if search_query:
        appointments = appointments.filter(
            Q(patient_name__icontains=search_query) |
            Q(patient_phone__icontains=search_query)
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/appointment_table.html', {'appointments': appointments})

    return render(request, 'admin_panel/appointments.html', {
        'appointments': appointments,
        'departments': Department.objects.all(),
        'services': Service.objects.all(),
        'labs': LabTest.objects.all(),
        'today': today  # Modal ichidagi 'min' sasa uchun kerak
    })

@login_required
def change_status(request, pk, status):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = status
    appointment.save()
    messages.success(request, f"Navbat statusi '{appointment.get_status_display()}' holatiga o'tkazildi!")
    return redirect('appointments_list')


@login_required
def book_appointment_dashboard(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date_str = request.POST.get('date')
        time_slot = request.POST.get('time_slot')

        # IKKALA MODELDA HAM TEKSHIRAMIZ
        exists_offline = Appointment.objects.filter(doctor_id=doctor_id, date=date_str, time_slot=time_slot).exists()
        exists_online = OnlineAppointment.objects.filter(doctor_id=doctor_id, date=date_str,
                                                         time_slot=time_slot).exists()

        if exists_offline or exists_online:
            messages.error(request, "XATO|Bu vaqt allaqachon band qilingan (Online yoki Offline).")
            return redirect('appointments_list')

        try:
            Appointment.objects.create(
                department_id=request.POST.get('department'),
                doctor_id=doctor_id,
                patient_name=request.POST.get('patient_name'),
                patient_phone=request.POST.get('patient_phone'),
                date=date_str,
                time_slot=time_slot,
                service_id=request.POST.get('service') or None,
                lab_test_id=request.POST.get('lab_test') or None,
                is_consultation=request.POST.get('is_consultation') == 'on'
            )
            messages.success(request, "Yangi navbat muvaffaqiyatli saqlandi!")
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")

    return redirect('appointments_list')


@login_required
def appointment_edit_dashboard(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.patient_name = request.POST.get('patient_name')
        appointment.patient_phone = request.POST.get('patient_phone')
        appointment.date = request.POST.get('date')
        appointment.time_slot = request.POST.get('time_slot')
        appointment.status = request.POST.get('status')
        appointment.save()
        messages.success(request, "Navbat o'zgartirildi!")
        return redirect('appointments_list')

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'admin_panel/partials/appointment_edit_form.html', {'appointment': appointment})
    return render(request, 'admin_panel/appointment_edit.html', {'appointment': appointment})


@login_required
def appointment_delete_dashboard(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        messages.error(request, "Navbat o'chirildi!")
    return redirect('appointments_list')


@login_required
def appointment_detail_dashboard(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    return render(request, 'admin_panel/appointment_detail.html', {'appointment': appointment})


# --- API VIEWS ---

@login_required
def get_doctors_by_department(request):
    dept_id = request.GET.get('department_id')
    doctors = Staff.objects.filter(department_id=dept_id, role='doctor').values('id', 'full_name')
    return JsonResponse({'doctors': list(doctors)})


from django.db.models import Q, Case, When, Value, IntegerField


@login_required
def online_appointments_list(request):
    search_query = request.GET.get('q', '')
    year = request.GET.get('year')
    month = request.GET.get('month')
    sort_by = request.GET.get('sort', 'priority')

    # Bugungi sanani olamiz
    today = timezone.now().date()

    # 1. Asosiy queryset (Faqat bugun va kelajakdagi navbatlar)
    appointments = OnlineAppointment.objects.filter(
        date__gte=today  # 27-aprel va undan keyingilar
    ).annotate(
        status_priority=Case(
            When(is_confirmed=False, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        )
    )

    # 2. Qidiruv va Filtrlar
    if search_query:
        appointments = appointments.filter(patient_name__icontains=search_query)

    # Yil va Oy filtri faqat kelajakdagi ma'lumotlar ichidan qidiradi
    if year:
        appointments = appointments.filter(date__year=year)
    if month:
        appointments = appointments.filter(date__month=month)

    # 3. Dinamik Saralash
    if sort_by == 'oldest':
        appointments = appointments.order_by('date', 'time_slot')
    elif sort_by == 'newest':
        appointments = appointments.order_by('-date', '-time_slot')
    elif sort_by == 'doctor':
        appointments = appointments.order_by('doctor__full_name')
    else:  # priority (Tasdiqlanmaganlar tepada, keyin sana bo'yicha)
        appointments = appointments.order_by('status_priority', 'date', 'time_slot')

    # 4. Filtr uchun ma'lumotlar (Faqat mavjud kelajakdagi sanalar bo'yicha)
    years = OnlineAppointment.objects.filter(date__gte=today).dates('date', 'year', order='DESC')

    months = None
    if year:
        months = OnlineAppointment.objects.filter(
            date__year=year,
            date__gte=today
        ).dates('date', 'month')

    return render(request, 'admin_panel/online_appointments.html', {
        'appointments': appointments,
        'search_query': search_query,
        'years': years,
        'months': months,
        'current_year': year,
        'current_month': month,
        'current_sort': sort_by,
        'today': today
    })
# def online_appointments_list(request):
#     search_query = request.GET.get('q', '')
#     year = request.GET.get('year')
#     month = request.GET.get('month')
#     sort_by = request.GET.get('sort', 'priority')  # Default saralash
#
#     # 1. Asosiy queryset (Priority mantiqi bilan)
#     appointments = OnlineAppointment.objects.annotate(
#         status_priority=Case(
#             When(is_confirmed=False, then=Value(0)),
#             default=Value(1),
#             output_field=IntegerField(),
#         )
#     )
#
#     # 2. Filtrlar
#     if search_query:
#         appointments = appointments.filter(patient_name__icontains=search_query)
#     if year:
#         appointments = appointments.filter(date__year=year)
#     if month:
#         appointments = appointments.filter(date__month=month)
#
#     # 3. Dinamik Saralash
#     if sort_by == 'oldest':
#         appointments = appointments.order_by('date', 'time_slot')
#     elif sort_by == 'newest':
#         appointments = appointments.order_by('-date', '-time_slot')
#     elif sort_by == 'doctor':
#         appointments = appointments.order_by('doctor__full_name')
#     else:  # priority (Kutilayotganlar tepada)
#         appointments = appointments.order_by('status_priority', '-date', '-time_slot')
#
#     # 4. Filtr uchun ma'lumotlar
#     years = OnlineAppointment.objects.dates('date', 'year', order='DESC')
#
#     # Oylar ro'yxati (Agar yil tanlangan bo'lsa)
#     months = None
#     if year:
#         months = OnlineAppointment.objects.filter(date__year=year).dates('date', 'month')
#
#     return render(request, 'admin_panel/online_appointments.html', {
#         'appointments': appointments,
#         'search_query': search_query,
#         'years': years,
#         'months': months,
#         'current_year': year,
#         'current_month': month,
#         'current_sort': sort_by
#     })


# 2. Tasdiqlash (Statusini o'zgartirish)
# 2. Tasdiqlash (Statusini o'zgartirish)

@login_required
def confirm_online_appointment(request, pk):
    appointment = get_object_or_404(OnlineAppointment, pk=pk)
    appointment.is_confirmed = True
    appointment.save()

    # extra_tags qo'shildi: bu xabar faqat admin panel uchun
    messages.success(request, f"{appointment.patient_name} navbati tasdiqlandi.", extra_tags='admin_panel')
    return redirect('dashboard_online_appointments_list')


# 3. O'chirish
from django.urls import reverse
def delete_online_appointment(request, pk):
    appointment = get_object_or_404(OnlineAppointment, pk=pk)
    # Ismni xabarda chiqarish shart bo'lmasa, 'name' o'zgaruvchisi shart emas
    appointment.delete()

    # URL manzilini olamiz: /dashboard/online-appointments/
    base_url = reverse('dashboard_online_appointments_list')

    # URL-ga ?msg=deleted qo'shib redirect qilamiz
    return redirect(f"{base_url}?msg=deleted")
#
#
# @login_required
# def delete_online_appointment(request, pk):
#     appointment = get_object_or_404(OnlineAppointment, pk=pk)
#     name = appointment.patient_name
#     appointment.delete()
#
#     # Tegni aniqroq qilamiz
#     messages.success(request, f"{name} navbati o'chirildi.", extra_tags='online_only')
#     return redirect('dashboard_online_appointments_list')


# 4. Tahrirlash (Modal uchun ma'lumotlarni yuborish)



# 5. Tahrirlashni saqlash

@login_required
def update_online_appointment(request, pk):
    appointment = get_object_or_404(OnlineAppointment, pk=pk)
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date_str = request.POST.get('date')
        time_slot = request.POST.get('time_slot')

        # O'zidan boshqa hamma navbatlarni tekshirish (poyga holati bo'lmasligi uchun)
        exists_off = Appointment.objects.filter(doctor_id=doctor_id, date=date_str, time_slot=time_slot).exists()
        exists_on = OnlineAppointment.objects.filter(doctor_id=doctor_id, date=date_str, time_slot=time_slot).exclude(
            pk=pk).exists()

        if exists_off or exists_on:
            messages.error(request, "XATO|Bu vaqt allaqachon band!")
        else:
            appointment.department_id = request.POST.get('department')
            appointment.doctor_id = doctor_id
            appointment.patient_name = request.POST.get('patient_name')
            appointment.patient_phone = request.POST.get('patient_phone')
            appointment.date = date_str
            appointment.time_slot = time_slot
            appointment.notes = request.POST.get('notes')
            appointment.save()
            messages.success(request, f"SUCCESS|{appointment.patient_name} ma'lumotlari yangilandi.")

    return redirect('dashboard_online_appointments_list')


@login_required
def view_online_appointment_json(request, pk):
    app = get_object_or_404(OnlineAppointment, pk=pk)
    data = {
        'name': app.patient_name,
        'phone': app.patient_phone,
        'department': app.department.name,
        'doctor': app.doctor.full_name,
        'date': app.date.strftime('%d.%m.%Y'),
        'time': app.time_slot.strftime('%H:%M'),
        'notes': app.notes if app.notes else "Izoh qoldirilmagan",
        'status': "Tasdiqlangan" if app.is_confirmed else "Kutilmoqda"
    }
    return JsonResponse(data)


@login_required
# 2. Tahrirlash Modali uchun (HTML qaytaradi)
def edit_online_appointment_modal(request, pk):
    app = get_object_or_404(OnlineAppointment, pk=pk)
    departments = Department.objects.all()
    # Faqat tanlangan bo'limdagi shifokorlarni chiqaramiz
    doctors = Staff.objects.filter(department=app.department, role='doctor')

    context = {
        'app': app,
        'departments': departments,
        'doctors': doctors,
    }

    # Bu yerda partials papkangdagi html fayling bo'lishi kerak
    html = render_to_string('admin_panel/partials/edit_online_modal.html', context, request=request)
    return JsonResponse({'html': html})


@login_required
def check_new_appointments(request):
    # Faqat tasdiqlanmagan (is_confirmed=False) navbatlar sonini qaytaramiz
    unread_count = OnlineAppointment.objects.filter(is_confirmed=False).count()
    return JsonResponse({'unread_count': unread_count})


@login_required
def medical_records_list(request):
    query = request.GET.get('q', '')
    doctor_query = request.GET.get('doctor_name', '') # ID emas, ism qabul qilamiz

    records = MedicalRecord.objects.select_related('patient', 'doctor').all()

    # 1. Bemor ismi yoki Tashxis bo'yicha qidiruv
    if query:
        records = records.filter(
            Q(patient__full_name__icontains=query) |
            Q(diagnosis__icontains=query)
        )

    # 2. Shifokor ismi bo'yicha qidiruv (MUHIM QISM)
    if doctor_query:
        records = records.filter(doctor__full_name__icontains=doctor_query)

    # --- AJAX QISMI ---
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('admin_panel/medical_records_table_partial.html', {'records': records})
        return HttpResponse(html)

    # Shifokorlar ro'yxati (doctors) endi renderga shart emas, chunki dropdown ishlatmaymiz
    return render(request, 'admin_panel/medical_records.html', {
        'records': records,
        'query': query,
        'doctor_query': doctor_query
    })


@login_required
def view_medical_record_json(request, pk):
    try:
        record = get_object_or_404(MedicalRecord, pk=pk)
        data = {
            'patient': record.patient.full_name,
            'doctor': record.doctor.full_name if record.doctor else "Noma'lum",
            'diagnosis': record.diagnosis,
            'prescription': record.prescription,
            # created_at modelingizda borligiga ishonch hosil qiling
            'date': record.created_at.strftime('%d.%m.%Y %H:%M') if hasattr(record, 'created_at') else "Sana yo'q"
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@login_required
def export_medical_record_pdf(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)

    # PDF sarlavhasi
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, f"Tibbiy Karta #{record.id}")

    p.setFont("Helvetica", 12)

    # DIQQAT: Agar modelingda first_name bo'lmasa, uni full_name yoki name ga almashtir
    # Taxminimcha, senda full_name ishlatilgan
    patient_name = getattr(record.patient, 'full_name', str(record.patient))

    p.drawString(100, 770, f"Bemor: {patient_name}")
    p.drawString(100, 750, f"Shifokor: {record.doctor.full_name if record.doctor else 'Noma-lum'}")
    p.drawString(100, 730, f"Sana: {record.created_at.strftime('%d.%m.%Y')}")

    p.line(100, 710, 500, 710)

    # Tashxis
    p.drawString(100, 690, "Tashxis:")
    p.drawString(120, 670, record.diagnosis)

    # Retsept
    p.drawString(100, 640, "Retsept:")
    text_object = p.beginText(120, 620)
    text_object.textLines(record.prescription)
    p.drawText(text_object)

    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf',
                        headers={'Content-Disposition': f'attachment; filename="record_{record.id}.pdf"'})



@login_required
# 1. Ro'yxat va Qidiruv
def payments_list(request):
    q = request.GET.get('q', '')
    status = request.GET.get('status', '')
    today = timezone.now().date()

    payments = Payment.objects.select_related(
        'appointment',
        'online_appointment',
        'service'
    ).all()

    # Real vaqtda qidiruv mantiqi
    if q:
        # Qidiruv bo'lganda barcha vaqtdagi bemorlarni qidirish
        payments = payments.filter(
            Q(appointment__patient_name__icontains=q) |
            Q(online_appointment__patient_name__icontains=q)
        )
    else:
        # Qidiruv bo'lmasa, faqat bugungi to'lovlarni ko'rsatish
        payments = payments.filter(created_at__date=today)

    if status:
        payments = payments.filter(is_paid=(status == 'paid'))

    payments = payments.order_by('-created_at')

    # Agar so'rov AJAX bo'lsa, butun sahifani emas, faqat kerakli qismini qaytarish ham mumkin
    # Lekin yuqoridagi JS kodi butun HTMLdan faqat jadvalni ajratib oladi.

    return render(request, 'admin_panel/payments/list.html', {
        'payments': payments,
        'q': q,
        'status': status
    })


# 2. Yangi to'lov qo'shish


@login_required
def payment_create(request):
    today = timezone.now().date()

    # --- AJAX QIDIRUV QISMI ---
    # Agar so'rov AJAX bo'lsa (Select2 dan kelsa), JSON qaytaramiz
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        query = request.GET.get('q', '')
        type_ = request.GET.get('type', 'offline')

        results = []
        if type_ == 'offline':
            data = Appointment.objects.filter(
                Q(patient_name__icontains=query),
                date__gte=today,
                payment__isnull=True
            )[:15]
        else:
            data = OnlineAppointment.objects.filter(
                Q(patient_name__icontains=query),
                date__gte=today,
                payment__isnull=True
            )[:15]

        for item in data:
            results.append({
                'id': item.id,
                'text': f"{item.patient_name} ({item.date})"
            })
        return JsonResponse({'results': results})

    # --- POST (SAQLASH) QISMI ---
    if request.method == 'POST':
        navbat_turi = request.POST.get('type_selector')

        payment = Payment(
            payment_type=request.POST.get('payment_type'),
            is_paid=request.POST.get('is_paid') == 'on'
        )

        # Tanlangan turga qarab faqat bitta ID ni biriktiramiz
        if navbat_turi == 'offline':
            payment.appointment_id = request.POST.get('appointment')
            payment.online_appointment_id = None
        elif navbat_turi == 'online':
            payment.online_appointment_id = request.POST.get('online_appointment')
            payment.appointment_id = None

        payment.save()
        return redirect('dashboard_payments_list')

    # --- ODDIY SAHIFA YUKLANISHI ---
    # Sahifa birinchi marta ochilganda oxirgi 10 ta navbatni ko'rsatib turish uchun
    appointments = Appointment.objects.filter(date__gte=today, payment__isnull=True).order_by('date')[:10]
    online_appointments = OnlineAppointment.objects.filter(date__gte=today, payment__isnull=True).order_by('date')[:10]

    context = {
        'appointments': appointments,
        'online_appointments': online_appointments,
    }
    return render(request, 'admin_panel/payments/form.html', context)
# @login_required
# def payment_create(request):
#     # Bugungi sanani olamiz (soatni hisobga olmagan holda)
#     today = timezone.now().date()
#
#     if request.method == 'POST':
#         # ... (POST qismi o'zgarishsiz qoladi)
#         app_id = request.POST.get('appointment')
#         online_app_id = request.POST.get('online_appointment')
#         payment = Payment(
#             payment_type=request.POST.get('payment_type'),
#             is_paid=request.POST.get('is_paid') == 'on'
#         )
#         if app_id: payment.appointment_id = app_id
#         if online_app_id: payment.online_appointment_id = online_app_id
#         payment.save()
#         return redirect('dashboard_payments_list')
#
#     # --- FILTRLASH QISMI ---
#
#     # Bugungi va bugundan keyingi (gte: greater than or equal) navbatlarni olamiz
#     # Faqat to'lovi qilinmagan (payment__isnull=True) navbatlar chiqadi
#
#     appointments = Appointment.objects.filter(
#         date__gte=today,
#         payment__isnull=True
#     ).order_by('date', 'time_slot')
#
#     online_appointments = OnlineAppointment.objects.filter(
#         date__gte=today,
#         payment__isnull=True
#     ).order_by('date', 'time_slot')
#
#     context = {
#         'appointments': appointments,
#         'online_appointments': online_appointments,
#     }
#     return render(request, 'admin_panel/payments/form.html', context)


# 3. Tahrirlash

@login_required
def payment_update(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == 'POST':
        payment.payment_type = request.POST.get('payment_type')
        payment.is_paid = request.POST.get('is_paid') == 'on'
        payment.save()
        messages.success(request, "To'lov ma'lumotlari yangilandi.")
        return redirect('dashboard_payments_list')

    return render(request, 'admin_panel/payments/form.html', {'payment': payment})


# 4. O'chirish

@login_required
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    payment.delete()
    messages.warning(request, "To'lov o'chirib tashlandi.")
    return redirect('dashboard_payments_list')


# 5. Batafsil ko'rish (ID bo'yicha)

@login_required
def payment_detail_json(request, pk):
    p = get_object_or_404(Payment, pk=pk)
    patient_name = f"{p.appointment.patient.first_name} {p.appointment.patient.last_name}" if p.appointment else p.online_appointment.patient_name
    data = {
        'patient': patient_name,
        'amount': p.amount,
        'type': p.get_payment_type_display(),
        'status': "To'langan" if p.is_paid else "To'lanmagan",
        'date': p.created_at.strftime('%d.%m.%Y %H:%M'),
        'item': p.service.name if p.service else (p.lab_test.name if p.lab_test else "Ko'rik")
    }
    return JsonResponse(data)


@login_required
def payment_view_json(request, pk):
    p = get_object_or_404(Payment, pk=pk)

    if p.appointment:
        # Bemor ismi Appointment modelida patient_name maydonida turibdi
        patient_name = p.appointment.patient_name

        # Xizmat nomini aniqlash
        if p.appointment.service:
            service_name = p.appointment.service.name
        elif p.appointment.lab_test:
            service_name = p.appointment.lab_test.name
        elif p.appointment.is_consultation:
            service_name = "Shifokor ko'rigi"
        else:
            service_name = "Xizmat ko'rsatilmadi"

    elif p.online_appointment:
        patient_name = p.online_appointment.patient_name
        service_name = "Online Navbat"
    else:
        patient_name = "Noma'lum"
        service_name = "Aniqlanmagan"

    data = {
        'patient': patient_name,
        'amount': f"{p.amount:,.0f} so'm".replace(',', ' '),
        'type': p.get_payment_type_display(),
        'item': service_name,
        'status': "To'langan" if p.is_paid else "To'lanmagan",
        'date': p.created_at.strftime('%d.%m.%Y %H:%M'),
    }

    return JsonResponse(data)


















# def custom_logout(request):
#     logout(request)
#     return redirect('login')






















#
# @login_required
# def profile_view(request):
#     # Foydalanuvchining o'z profiliga kirishini ta'minlaydi
#     return render(request, 'reseption/profile.html', {
#         'staff': getattr(request.user, 'staff_profile', None)
#     })



# class MyLoginView(LoginView):
#     template_name = 'registration/login.html'
#
#     def get_success_url(self):
#         user = self.request.user
#
#         # 1. Agar foydalanuvchi /admin/ ga o'tmoqchi bo'lib login qilgan bo'lsa
#         next_url = self.request.GET.get('next') or self.request.POST.get('next')
#         if next_url:
#             return next_url
#
#         # 2. Agar superuser bo'lsa va shunchaki /login/ orqali kirsa
#         if user.is_superuser:
#             return '/admin/'
#
#         # 3. Agar xodim bo'lsa, roli bo'yicha yuborish
#         if hasattr(user, 'staff_profile'):
#             role = user.staff_profile.role
#             if role in ['reception', 'admin']:
#                 return reverse_lazy('reception_dash')
#             elif role == 'doctor':
#                 return reverse_lazy('doctor_dash')
#
#         return reverse_lazy('home')
#
#
# @login_required
# def reception_dashboard(request):
#     # 1. Huquqni tekshirish
#     is_staff_admin = hasattr(request.user, 'staff_profile') and request.user.staff_profile.role in ['reception',
#                                                                                                     'admin']
#
#     if not (request.user.is_superuser or is_staff_admin):
#         return redirect('home')
#
#     # 2. Ma'lumotlarni yig'ish
#     context = {
#         'departments': Department.objects.all(),
#         'services': Service.objects.all(),
#         'staffs': Staff.objects.all(),
#         'patients': Patient.objects.all(),
#         'online_appointments': OnlineAppointment.objects.order_by('-created_at'),
#         'appointments': Appointment.objects.order_by('-date', '-time_slot'),
#         'lab_tests': LabTest.objects.all(),
#         'lab_referrals': LabReferral.objects.order_by('-created_at'),
#         'payments': Payment.objects.order_by('-created_at'),
#         'medical_records': MedicalRecord.objects.all(),
#         'news': News.objects.all(),
#         'messages': ContactMessage.objects.filter(is_read=False),
#         'staff_user': request.user.staff_profile if hasattr(request.user, 'staff_profile') else None
#     }
#     return render(request, 'reseption/dashboard.html', context)
#
#
# # DIQQAT: Bu funksiya hech qanday klass ichida bo'lmasligi kerak (mustaqil funksiya)
# def custom_logout(request):
#     logout(request)
#     return redirect('login')
#
# def profile_view(request):
#     staff = getattr(request.user, 'staff_profile', None)
#
#     if request.method == 'POST':
#         new_email = request.POST.get('email')
#         new_phone = request.POST.get('phone')
#         new_photo = request.FILES.get('photo')  # Yangi rasmni olish
#
#         # User modelini yangilash
#         request.user.email = new_email
#         request.user.save()
#
#         # Staff modelini yangilash
#         if staff:
#             staff.phone = new_phone # Modelda 'phone' deb yozilgan ekan
#             if new_photo:
#                 staff.photo = new_photo
#             staff.save()
#
#         messages.success(request, "Ma'lumotlaringiz muvaffaqiyatli yangilandi!")
#         return redirect('profile_view')
#
#     return render(request, 'reseption/profile.html', {
#         'staff': staff,
#         'user': request.user
#     })













def home_view(request):
    now = timezone.now()
    today = now.date()
    current_time = now.time()

    # --- 1. QIDIRUV PARAMETRLARI ---
    doctor_name = request.GET.get('doctor_name', '')
    specialty_id = request.GET.get('specialty', '')

    # --- 2. FAQAT DOCTORLARNI FILTRLASH ---
    doctors_query = Staff.objects.filter(role='doctor').select_related('doctor_details', 'department')

    if doctor_name:
        doctors_query = doctors_query.filter(full_name__icontains=doctor_name)

    if specialty_id:
        doctors_query = doctors_query.filter(department_id=specialty_id)

    doctors = doctors_query[:6]

    # --- AJAX SO'ROVINI TEKSHIRISH ---
    # Agar so'rov JavaScript (AJAX) orqali kelsa, faqat shifokorlar ro'yxatini qaytaramiz
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'includes/doctor_list_results.html', {'doctors': doctors})

    # --- 3. NAVBATLARNI TOPISH (Sening koding) ---
    next_appointment = Appointment.objects.filter(
        Q(date__gt=today) | Q(date=today, time_slot__gte=current_time)
    ).order_by('date', 'time_slot').first()

    next_online = OnlineAppointment.objects.filter(
        Q(date__gt=today) | Q(date=today, time_slot__gte=current_time)
    ).order_by('date', 'time_slot').first()

    closest_app = None
    if next_appointment and next_online:
        if (next_appointment.date < next_online.date) or \
                (next_appointment.date == next_online.date and next_appointment.time_slot < next_online.time_slot):
            closest_app = next_appointment
        else:
            closest_app = next_online
    else:
        closest_app = next_appointment or next_online

    # Select-box uchun bo'limlar
    departments = Department.objects.all()

    context = {
        'next_app': closest_app,
        'today': today,
        'doctors': doctors,
        'departments': departments,
    }
    return render(request, 'index.html', context)


def departments_view(request):
    all_depts = Department.objects.all()
    # Bu yerda ham xuddi shunday 6 ta tasodifiy shifokor
    all_doctors = list(Staff.objects.filter(role='doctor'))
    random_doctors = random.sample(all_doctors, min(len(all_doctors), 6))

    return render(request, 'departments.html', {
        'departments': all_depts,
        'random_doctors': random_doctors
    })
# def departments_view(request):
#     all_depts = Department.objects.all()
#     # Tasodifiy 6 ta bo'lim (agar bo'limlar 6 tadan kam bo'lsa, borini oladi)
#     random_6 = random.sample(list(all_depts), min(len(all_depts), 6))
#
#     return render(request, 'departments.html', {
#         'departments': all_depts,
#         'random_depts': random_6
#     })


# def department_detail(request, pk):
#     # Hamma bo'limlarni sidebar uchun olamiz
#     departments = Department.objects.all()
#     # Tanlangan bo'limni id orqali topamiz
#     selected_dept = get_object_or_404(Department, pk=pk)
#
#     context = {
#         'departments': departments,
#         'selected_dept': selected_dept,
#     }
#     return render(request, 'departments.html', context)

# views.py
def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message_text
        )

        # Muvaffaqiyatli xabarni .info orqali yuboring (ko'k rang uchun)
        # messages.info(request, "Xabaringiz muvaffaqiyatli yuborildi! Tez orada siz bilan bog'lanamiz.")
        # Contact formasi muvaffaqiyatli yuborilganda:
        messages.success(request, "Xabaringiz yuborildi!", extra_tags='contact_form')
        return redirect('contact')

    departments = Department.objects.all()
    return render(request, 'contact.html', {'departments': departments})

def custom_404(request, exception): # 'exception' argumenti borligiga ishonch hosil qiling
    return render(request, '404.html', status=404)


# def doctors_page(request):
#     doctors = Staff.objects.filter(role='doctor').select_related('department', 'doctor_details')
#     departments = Department.objects.all()  # Filter tugmalari uchun
#
#     context = {
#         'doctors': doctors,
#         'departments': departments,
#     }
#     return render(request, 'doctors.html', context)

# def doctors_page(request):
#     # Shifokorlarni barcha kerakli bog'liqliklar bilan olamiz
#     doctors = Staff.objects.filter(role='doctor')
#
#     # Bazadagi shifokorlar ishlatayotgan barcha mutaxassisliklarni takrorlanmas holda yig'amiz
#     # Bu bizga filtr tugmalarini yaratish uchun kerak
#     specializations = doctors.values_list('doctor_details__specialization', flat=True).distinct()
#
#     # Bo'sh qiymatlarni olib tashlaymiz (agar bo'lsa)
#     specializations = [s for s in specializations if s]
#
#     context = {
#         'doctors': doctors,
#         'specializations': specializations,
#     }
#     return render(request, 'doctors.html', context)

def doctors_page(request):
    # select_related-ni qaytaring, bu DB ga yuklamani kamaytiradi
    doctors = Staff.objects.filter(role='doctor').select_related('doctor_details')

    # Filtrlar uchun mutaxassisliklarni olish
    specializations = doctors.values_list('doctor_details__specialization', flat=True).distinct()
    specializations = [s for s in specializations if s]

    context = {
        'doctors': doctors,
        'specializations': specializations,
    }
    return render(request, 'doctors.html', context)


def markaz_haqida_view(request):
    # Jami 12 ta bo'lim
    departments = Department.objects.all()[:12]
    # Jami 16 ta shifokor
    doctors = Staff.objects.filter(role='doctor').select_related('department')[:16]

    context = {
        'departments': departments,
        'doctors': doctors,
    }
    return render(request, 'markaz_haqida.html', context)


def rahbariyat_view(request):
    # Xodimlarni bazadan olish
    xodimlar = Staff.objects.all()

    # MUHIM: Mana shu qator bo'lishi va u funksiya ichida bo'lishi shart!
    return render(request, 'rahbariyat.html', {'xodimlar': xodimlar})


# def price_list_view(request):
#     # Laboratoriya tahlillari
#     lab_tests = LabTest.objects.all()
#     # Bo'limlar va ularga tegishli xizmatlar
#     departments = Department.objects.prefetch_related('services').all()
#     # Shifokorlar (pastki qism uchun)
#     doctors = Staff.objects.filter(role='doctor').select_related('doctor_details', 'department')
#
#     context = {
#         'lab_tests': lab_tests,
#         'departments': departments,
#         'doctors': doctors,
#     }
#     return render(request, 'price.html', context)

def price_list_view(request):
    lab_tests = LabTest.objects.all()
    departments = Department.objects.prefetch_related('services').all()

    # .order_by('id') qo'shildi - bu tartibni kafolatlaydi
    doctors = Staff.objects.filter(role='doctor').select_related(
        'doctor_details',
        'department'
    ).order_by('id')

    context = {
        'lab_tests': lab_tests,
        'departments': departments,
        'doctors': doctors,
    }
    return render(request, 'price.html', context)


def services_view(request):
    services = Service.objects.all()
    # 1. Bo'limlarni (Department) ham yuborish shart
    departments = Department.objects.all()  # Model nomingizni tekshiring (Department yoki Category)

    # Hamma shifokorlar orasidan tasodifiy 6 tasini olamiz
    all_doctors = list(Staff.objects.filter(role='doctor'))
    random_doctors = random.sample(all_doctors, min(len(all_doctors), 6))

    return render(request, 'services.html', {
        'services': services,
        'departments': departments,  # Mana shu qism qo'shildi
        'random_doctors': random_doctors
    })

from django.shortcuts import render, get_object_or_404
from .models import DoctorProfile


# def doctor_detail_view(request, pk):
#     # select_related staff uchun, prefetch_related esa staff ga bog'langan boshqa jadvallar uchun
#     doctor = get_object_or_404(
#         DoctorProfile.objects.select_related('staff').prefetch_related(
#             'staff__social_contacts',
#             'staff__educations',
#             'staff__experiences'
#         ),
#         pk=pk
#     )
#
#     context = {
#         'doctor': doctor,
#     }
#     return render(request, 'doctor_detail.html', context)

# def doctor_detail_view(request, pk):
#     # pk bu yerda Staff-ning ID-si (masalan: 8)
#     # Biz DoctorProfile ichidan shunday obyektni qidiramizki,
#     # uning 'staff' maydonining ID-si biz bergan 'pk' ga teng bo'lsin.
#     doctor = get_object_or_404(
#         DoctorProfile.objects.select_related('staff').prefetch_related(
#             'staff__social_contacts',
#             'staff__educations',
#             'staff__experiences'
#         ),
#         staff__id=pk  # <--- MANA SHU JOYNI O'ZGARTIRING (pk=pk emas, staff__id=pk)
#     )
#
#     context = {
#         'doctor': doctor,
#     }
#     return render(request, 'doctor_detail.html', context)
def doctor_detail_view(request, pk):
    # pk - bu price.html dan kelayotgan doctor.id
    doctor = get_object_or_404(
        DoctorProfile.objects.select_related('staff').prefetch_related(
            'staff__social_contacts',
            'staff__educations',
            'staff__experiences'
        ),
        staff_id=pk  # staff__id o'rniga staff_id deb yozish ham mumkin (aniqroq)
    )

    context = {
        'doctor': doctor,
    }
    return render(request, 'doctor_detail.html', context)


def book_appointment(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        date_str = request.POST.get('date')
        time_slot = request.POST.get('time_slot')

        # IKKALA JADVALNI TEKSHIRISH
        # 1. Saytdan olinganlar ichida bormi?
        exists_online = OnlineAppointment.objects.filter(
            doctor_id=doctor_id, date=date_str, time_slot=time_slot
        ).exists()

        # 2. Admin paneldan (reception) olinganlar ichida bormi?
        exists_offline = Appointment.objects.filter(
            doctor_id=doctor_id, date=date_str, time_slot=time_slot
        ).exists()

        if not (exists_online or exists_offline):
            # Ikkala joyda ham bo'sh bo'lsagina saqlaymiz
            appointment = OnlineAppointment.objects.create(
                department_id=request.POST.get('department'),
                doctor_id=doctor_id,
                patient_name=request.POST.get('patient_name'),
                patient_phone=request.POST.get('patient_phone'),
                date=date_str,
                time_slot=time_slot,
                notes=request.POST.get('notes')
            )
            messages.success(request,
                             f"SUCCESS|{appointment.patient_name}|{appointment.department.name}|{appointment.doctor.full_name}|{date_str}|{time_slot}")
        else:
            messages.error(request, "XATO|Uzr, bu vaqt allaqachon band qilingan.")

        return redirect(request.META.get('HTTP_REFERER', '/'))







#
# def book_appointment(request):
#     if request.method == 'POST':
#         # Formadan department ID sini ham olamiz
#         department_id = request.POST.get('department')
#         doctor_id = request.POST.get('doctor')
#         patient_name = request.POST.get('patient_name')
#         patient_phone = request.POST.get('patient_phone')
#         date_str = request.POST.get('date')
#         time_slot = request.POST.get('time_slot')
#         notes = request.POST.get('notes')
#
#         # Bazada bor-yo'qligini tekshirish
#         exists = OnlineAppointment.objects.filter(
#             doctor_id=doctor_id,
#             date=date_str,
#             time_slot=time_slot
#         ).exists()
#
#         if not exists:
#             # department_id ENDI NULL BO'LMAYDI
#             appointment = OnlineAppointment.objects.create(
#                 department_id=department_id,
#                 doctor_id=doctor_id,
#                 patient_name=patient_name,
#                 patient_phone=patient_phone,
#                 date=date_str,
#                 time_slot=time_slot,
#                 notes = notes
#             )
#             # ... qolgan success xabar kodlari ...
#             messages.success(request, f"SUCCESS|{patient_name}|{appointment.department.name}|{appointment.doctor.full_name}|{date_str}|{time_slot}")
#         else:
#             messages.error(request, "XATO|Uzr, bu vaqt band bo'lib qoldi.")
#
#         return redirect(request.META.get('HTTP_REFERER', '/'))













# 2. Bo'sh vaqt slotlarini qaytaruvchi API (AJAX uchun)
# def get_available_slots(request):
#     doctor_id = request.GET.get('doctor')
#     date_str = request.GET.get('date')
#
#     if not doctor_id or not date_str:
#         return JsonResponse({'error': 'Ma`lumotlar yetarli emas'}, status=400)
#
#     try:
#         selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
#     except ValueError:
#         return JsonResponse({'error': 'Sana formati noto`g`ri'}, status=400)
#
#     # --- YANGI CHEKLOVLAR ---
#     today = timezone.now().date()
#     max_date = today + datetime.timedelta(days=30)
#
#     # 1. Yakshanba tekshiruvi (6 - yakshanba)
#     if selected_date.weekday() == 6:
#         return JsonResponse({'error': 'Yakshanba dam olish kuni!'}, status=400)
#
#     # 2. Faqat 1 oylik muddat (o'tgan kunlar va 30 kundan keyin taqiqlanadi)
#     if selected_date < today or selected_date > max_date:
#         return JsonResponse({'error': 'Faqat kelgusi 30 kun ichida navbat olish mumkin.'}, status=400)
#     # -----------------------
#
#     booked_slots = OnlineAppointment.objects.filter(
#         doctor_id=doctor_id,
#         date=selected_date
#     ).values_list('time_slot', flat=True)
#
#     start_time = datetime.datetime.combine(selected_date, datetime.time(9, 0))
#     end_time = datetime.datetime.combine(selected_date, datetime.time(17, 0))
#
#     available_slots = []
#     current_time = start_time
#     while current_time < end_time:
#         slot_time = current_time.time()
#         if slot_time not in booked_slots:
#             available_slots.append(slot_time.strftime('%H:%M'))
#         current_time += datetime.timedelta(minutes=30)
#
#     return JsonResponse({'available_slots': available_slots})


# def get_available_slots(request):
#     doctor_id = request.GET.get('doctor')
#     date_str = request.GET.get('date')
#
#     if not doctor_id or not date_str:
#         return JsonResponse({'error': 'Ma`lumotlar yetarli emas'}, status=400)
#
#     try:
#         selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
#     except ValueError:
#         return JsonResponse({'error': 'Sana formati noto`g`ri'}, status=400)
#
#     # 1. Yakshanba tekshiruvi
#     if selected_date.weekday() == 6:
#         return JsonResponse({'error': 'Yakshanba dam olish kuni!'}, status=400)
#
#     # 2. Band vaqtlarni IKKALA jadvaldan ham yig'amiz
#     # Offline navbatlar (Admin panel orqali olingan)
#     booked_offline = Appointment.objects.filter(
#         doctor_id=doctor_id,
#         date=selected_date
#     ).values_list('time_slot', flat=True)
#
#     # Online navbatlar (Sayt orqali olingan - agar OnlineAppointment modeli bo'lsa)
#     booked_online = OnlineAppointment.objects.filter(
#         doctor_id=doctor_id,
#         date=selected_date
#     ).values_list('time_slot', flat=True)
#
#     # Ikkalasini birlashtiramiz (Set ishlatish takrorlanishni oldini oladi)
#     all_booked_slots = set(list(booked_offline) + list(booked_online))
#
#     # 3. Ish vaqtini belgilash
#     start_time = datetime.datetime.combine(selected_date, datetime.time(9, 0))
#
#     # Shanba kuni 16:00 gacha, boshqa kunlar 17:00 gacha
#     limit_hour = 16 if selected_date.weekday() == 5 else 17
#     end_time = datetime.datetime.combine(selected_date, datetime.time(limit_hour, 0))
#
#     available_slots = []
#     current_time = start_time
#     today = datetime.date.today()
#     now_time = datetime.datetime.now().time()
#
#     while current_time < end_time:
#         slot_time = current_time.time()
#
#         # O'tib ketgan vaqtni ko'rsatmaslik (Bugun bo'lsa)
#         if selected_date == today and slot_time <= now_time:
#             current_time += datetime.timedelta(minutes=30)
#             continue
#
#         # AGAR BU VAQT BAND BO'LSA, RO'YXATGA QO'SHMAYMIZ
#         if slot_time not in all_booked_slots:
#             available_slots.append(slot_time.strftime('%H:%M'))
#
#         current_time += datetime.timedelta(minutes=30)
#
#     return JsonResponse({'available_slots': available_slots})























from django.http import JsonResponse
import datetime
from django.utils import timezone
from .models import Appointment, OnlineAppointment  # Har ikkala modelni chaqiramiz


def get_available_slots(request):
    doctor_id = request.GET.get('doctor')
    date_str = request.GET.get('date')

    if not doctor_id or not date_str:
        return JsonResponse({'error': 'Ma`lumotlar yetarli emas'}, status=400)

    try:
        selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Sana formati noto`g`ri'}, status=400)

    today = timezone.now().date()

    # 1. Yakshanba tekshiruvi
    if selected_date.weekday() == 6:
        return JsonResponse({'error': 'Yakshanba dam olish kuni!'}, status=400)

    # 2. BAND VAQTLARNI IKKALA JADVALDAN OLISH
    # Admin paneldagi navbatlar
    booked_offline = Appointment.objects.filter(
        doctor_id=doctor_id,
        date=selected_date
    ).values_list('time_slot', flat=True)

    # Saytdagi online navbatlar
    booked_online = OnlineAppointment.objects.filter(
        doctor_id=doctor_id,
        date=selected_date
    ).values_list('time_slot', flat=True)

    # Ikkalasini bitta to'plamga birlashtiramiz
    all_booked_slots = set(list(booked_offline) + list(booked_online))

    # 3. Ish vaqtini belgilash (Sen aytgan namuna bo'yicha)
    start_time = datetime.datetime.combine(selected_date, datetime.time(9, 0))
    limit_hour = 16 if selected_date.weekday() == 5 else 17
    end_time = datetime.datetime.combine(selected_date, datetime.time(limit_hour, 0))

    available_slots = []
    current_time = start_time
    now_obj = datetime.datetime.now()

    while current_time < end_time:
        slot_time = current_time.time()

        # Bugun bo'lsa, o'tib ketgan vaqtlarni ko'rsatmaslik
        if selected_date == today and slot_time <= now_obj.time():
            current_time += datetime.timedelta(minutes=30)
            continue

        # AGAR VAQT IKKALA JADVALDA HAM YO'Q BO'LSA - DEMAK BO'SH
        if slot_time not in all_booked_slots:
            available_slots.append(slot_time.strftime('%H:%M'))

        current_time += datetime.timedelta(minutes=30)

    return JsonResponse({'available_slots': available_slots})






































# def get_available_slots(request): haqiyqiysi
#     doctor_id = request.GET.get('doctor')
#     date_str = request.GET.get('date')
#
#     if not doctor_id or not date_str:
#         return JsonResponse({'error': 'Ma`lumotlar yetarli emas'}, status=400)
#
#     try:
#         selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
#     except ValueError:
#         return JsonResponse({'error': 'Sana formati noto`g`ri'}, status=400)
#
#     today = timezone.now().date()
#     max_date = today + datetime.timedelta(days=30)
#
#     # 1. Yakshanba tekshiruvi
#     if selected_date.weekday() == 6:
#         return JsonResponse({'error': 'Yakshanba dam olish kuni!'}, status=400)
#
#     if selected_date < today or selected_date > max_date:
#         return JsonResponse({'error': 'Faqat kelgusi 30 kun ichida navbat olish mumkin.'}, status=400)
#
#     booked_slots = OnlineAppointment.objects.filter(
#         doctor_id=doctor_id,
#         date=selected_date
#     ).values_list('time_slot', flat=True)
#
#     # --- ISH VAQTINI BELGILASH ---
#     start_time = datetime.datetime.combine(selected_date, datetime.time(9, 0))
#
#     # Agar shanba bo'lsa (weekday == 5), 16:00 gacha, aks holda 17:00 gacha
#     if selected_date.weekday() == 5:
#         limit_hour = 16
#     else:
#         limit_hour = 17
#
#     end_time = datetime.datetime.combine(selected_date, datetime.time(limit_hour, 0))
#     # ------------------------------
#
#     available_slots = []
#     current_time = start_time
#
#     # current_time < end_time bo'lgani uchun:
#     # Ish kunlari oxirgi slot 16:30 (17:00 dan kichik)
#     # Shanba kuni oxirgi slot 15:30 (16:00 dan kichik) bo'ladi
#     while current_time < end_time:
#         slot_time = current_time.time()
#
#         # Bugungi kun bo'lsa, faqat o'tib ketmagan vaqtlarni ko'rsatish (ixtiyoriy lekin yaxshi UX)
#         if selected_date == today and slot_time <= datetime.datetime.now().time():
#             current_time += datetime.timedelta(minutes=30)
#             continue
#
#         if slot_time not in booked_slots:
#             available_slots.append(slot_time.strftime('%H:%M'))
#         current_time += datetime.timedelta(minutes=30)
#
#     return JsonResponse({'available_slots': available_slots})
















































def news_list(request):
    # Faqat yangiliklar sahifasi uchun kerakli ma'lumotlar
    all_news = News.objects.all().order_by('-created_at')[:10]
    recent_news = all_news[:4]
    departments = Department.objects.all()

    context = {
        'news': all_news,
        'recent_news': recent_news,
        'departments': departments,
    }
    return render(request, 'news.html', context)


def news_detail(request, pk):
    # 1. Yangilikni bazadan olamiz
    item = get_object_or_404(News, pk=pk)

    # BU YERDAN RAQAMNI OSHIRISH (item.save) OLIB TASHLANDI!
    # Chunki endi buni JavaScript fonda bajaradi.

    departments = Department.objects.all()

    # Sidebar uchun boshqa yangiliklar
    recent_news = News.objects.exclude(pk=pk).order_by('-created_at')[:3]

    context = {
        'item': item,
        'departments': departments,
        'recent_news': recent_news,
    }
    return render(request, 'news_detail.html', context)

def increment_views_ajax(request, pk):
    if request.method == "POST":
        # Bazada views_count ni bittaga oshirish
        News.objects.filter(pk=pk).update(views_count=F('views_count') + 1)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


def get_doctors_by_dept(request):
    dept_id = request.GET.get('dept_id')
    # Faqat tanlangan bo'limdagi va roli 'doctor' bo'lgan xodimlarni olish
    doctors = Staff.objects.filter(department_id=dept_id, role='doctor').values('id', 'full_name')
    return JsonResponse({'doctors': list(doctors)})




















import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.conf import settings
from mainApp.models import Department, Service, Staff


# 1. Yordamchi funksiya: Zaxira tizimi (Fallback)
def get_gemini_response(chat_history, user_message, instructions):
    # 1. Sizning YANGI API kalitingiz
    PRIMARY_KEY = "AIzaSyDQ9oDIBmbS8PPhA6I8firYAt4AtanatcQ"

    # 2. Modellarni sinash tartibi
    # Birinchi navbatda sizning kalitingiz bilan Flash 2.0 ni sinaymiz
    models_to_try = [
        "gemini-2.0-flash",  # Asosiy tanlov
        "gemini-2.0-flash-lite",  # Ikkinchi tanlov
        "gemini-pro-latest"  # Oxirgi chora
    ]

    for model_name in models_to_try:
        try:
            # Har safar kalitni qayta sozlaymiz (agar birinchisi bloklansa ham)
            genai.configure(api_key=PRIMARY_KEY)

            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=instructions
            )
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(user_message)
            return response.text

        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "quota" in error_str:
                print(f"--- {model_name} limiti tugadi, keyingisiga o'tilmoqda... ---")
                continue
            else:
                # Agar boshqa xato bo'lsa (masalan tarmoq xatosi)
                print(f"--- Xato yuz berdi: {str(e)} ---")
                raise e

    return "Kechirasiz, barcha modellar bo'yicha limit tugadi. Iltimos, birozdan so'ng urinib ko'ring."

# 2. Klinika ma'lumotlarini bazadan yig'ish
def get_clinic_context():
    lines = []
    # Bo'limlar va xizmatlar
    departments = Department.objects.prefetch_related('services').all()
    lines.append("=== KLINIKA BO'LIMLARI VA XIZMATLARI ===\n")
    for dept in departments:
        lines.append(f"BO'LIM: {dept.name}")
        for svc in dept.services.all():
            lines.append(f"  - {svc.name} | Narxi: {svc.price} so'm")
        lines.append("")

    # Shifokorlar
    doctors = Staff.objects.filter(role='doctor').select_related('department').all()
    lines.append("=== SHIFOKORLAR ===\n")
    for doctor in doctors:
        dept_name = doctor.department.name if doctor.department else "Umumiy"
        lines.append(f"SHIFOKOR: {doctor.full_name} | Bo'lim: {dept_name}")

    return "\n".join(lines)

# 3. Model uchun yo'riqnoma tayyorlash
def build_system_instruction(clinic_context: str) -> str:
    return f"""Siz "Bobur Doktor Shifo" klinikasining aqlli yordamchisisiz.
Vazifangiz: Bemor shikoyatiga qarab bo'lim yoki shifokorni tavsiya qilish.

QOIDALAR:
1. Faqat quyidagi ma'lumotlarga tayaning:
{clinic_context}
2. Javob O'ZBEK tilida, juda qisqa (2-3 jumla) bo'lsin.
3. Shoshilinch holatda (og'ir jarohat, hushsizlik) tez yordamga chaqirishni ayting.
4. Javob oxirida: "Qo'shimcha savollar bo'lsa, resepsiyamizga murojat qiling." deb yozing.
"""

# 4. Asosiy API View
@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    try:
        # API kalitini aynan shu yerda configure qilamiz
        api_key = getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
        genai.configure(api_key=api_key)

        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        history = data.get("history", [])

        if not user_message:
            return JsonResponse({"error": "Xabar bo'sh"}, status=400)

        clinic_context = get_clinic_context()
        system_instructions = build_system_instruction(clinic_context)

        # Tarixni Gemini formatiga o'girish
        chat_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})

        # Zaxira tizimi orqali javob olish
        bot_reply = get_gemini_response(chat_history, user_message, system_instructions)

        return JsonResponse({"reply": bot_reply})

    except Exception as e:
        error_message = str(e)
        print(f"--- Chatbot Xatosi: {error_message} ---")
        return JsonResponse({"reply": "Tizimda vaqtincha uzilish yuz berdi. Iltimos, qayta urinib ko'ring."}, status=200)

def chatbot_page(request):
    return render(request, "registration/chat.html")


from django.contrib.auth import logout
from django.shortcuts import redirect


def custom_logout(request):
    user = request.user

    # Standart holatda (reception yoki oddiy foydalanuvchilar uchun) login sahifasi
    next_login_page = 'login'

    if user.is_authenticated:
        # Foydalanuvchining Staff (Xodim) profili borligini tekshiramiz
        if hasattr(user, 'staff_profile') and user.staff_profile is not None:
            user_role = user.staff_profile.role  # 'doctor', 'reception', 'admin'

            if user_role == 'doctor':
                next_login_page = 'doctor_dashboard_login'
            elif user_role == 'reception':
                next_login_page = 'login'
            elif user_role == 'admin':
                # Sizda maxsus admin login url-nomi yo'q ekan, shuning uchun to'g'ri standart admin panelga otamiz
                logout(request)
                return redirect('/admin/')

    # Sessiyani tozalash (tizimdan chiqarish)
    logout(request)

    # Tegishli login sahifasiga yo'naltirish
    return redirect(next_login_page)