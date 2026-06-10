# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from django.conf.urls import handler404  # 404 xatolikni ushlab qolish uchun
# from mainApp.views import *
# from django.contrib.auth.views import LogoutView,PasswordChangeView
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', home_view, name='home'),
#     path('departments/', departments_view, name='departments_page'),
#     # path('departments/<int:pk>/', department_detail, name='department_detail'),
#     path('contact/', contact_view, name='contact'),
#     path('doctors/', doctors_page, name='doctors_list'),
#     path('markaz-haqida/', markaz_haqida_view, name='markaz_haqida'),
#     path('rahbariyat/', rahbariyat_view, name='rahbariyat'),
#     path('price/', price_list_view, name='price_list'),
#     path('services/', services_view, name='services_list'),
#     path('doctor/<int:pk>/', doctor_detail_view, name='doctor_detail'),
#     path('book-appointment/', book_appointment, name='book_appointment'),
#     path('api/available-slots/', get_available_slots, name='available_slots'),
#     path('yangiliklar/', news_list, name='news_list'),
#     path('yangiliklar/<int:pk>/', news_detail, name='news_detail'),
#     path('yangiliklar/view-count/<int:pk>/', increment_views_ajax, name='increment_views_ajax'),
#     path('get-doctors-by-dept/', get_doctors_by_dept, name='get_doctors_by_dept'),
#
#
#     path('login/', MyLoginView.as_view(), name='login'),
#     path('reception/dashboard/', reception_dashboard, name='reception_dash'),
#
#     # Chiqish (next_page login sahifasiga qaytaradi)
#     path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
#
#     # --- PROFIL VA PAROL (Xatoni tuzatuvchi qism) ---
#     # Profil sahifasi
#     path('reception/profile/', profile_view, name='profile_view'),
#
#     # Parolni o'zgartirish
#     path('reception/password-change/',
#          PasswordChangeView.as_view(
#              template_name='registration/password_change.html',
#              success_url=reverse_lazy('profile_view')
#          ),
#          name='password_change'),
# ]
#
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#
# handler404 = 'mainApp.views.custom_404'




from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.contrib.auth.views import LogoutView, PasswordChangeView

from mainApp.views import *
from django.contrib import admin
from mainApp.forms import CustomAdminLoginForm
from mainApp.views import  custom_logout, doctor_dashboard_login

admin.site.login_form = CustomAdminLoginForm

urlpatterns = [
    # --- ADMIN PANELI ---
    path('admin/', admin.site.urls),

    # --- ASOSIY SAHIFALAR ---
    path('', home_view, name='home'),
    path('markaz-haqida/', markaz_haqida_view, name='markaz_haqida'),
    path('rahbariyat/', rahbariyat_view, name='rahbariyat'),
    path('contact/', contact_view, name='contact'),

    # --- SHIFOKORLAR VA BO'LIMLAR ---
    path('departments/', departments_view, name='departments_page'),
    path('doctors/', doctors_page, name='doctors_list'),
    path('doctor/<int:pk>/', doctor_detail_view, name='doctor_detail'),
    path('get-doctors-by-dept/', get_doctors_by_dept, name='get_doctors_by_dept'),

    # --- XIZMATLAR VA NARXLAR ---
    path('services/', services_view, name='services_list'),
    path('price/', price_list_view, name='price_list'),

    # --- YANGILIKLAR ---
    path('yangiliklar/', news_list, name='news_list'),
    path('yangiliklar/<int:pk>/', news_detail, name='news_detail'),
    path('yangiliklar/view-count/<int:pk>/', increment_views_ajax, name='increment_views_ajax'),

    # --- NAVBAT VA AI INTEGRATSIYA ---
    path('book-appointment/', book_appointment, name='book_appointment'),
    path('api/available-slots/', get_available_slots, name='available_slots'),



    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('dashboard/', reception_dashboard, name='reception_dash'),
    path('dashboard/departments/', departments_list, name='departments_list'),
    path('dashboard/departments/<int:pk>/', department_detail, name='department_detail'),
    path('dashboard/services/', services_list, name='services_list_dashboard'),
    path('dashboard/services/<int:pk>/', service_detail, name='service_detail_dashboard'),
# Shifokorlar ro'yxati sahifasi
    path('dashboard/doctors/', doctors_list_dashboard, name='doctors_list_dashboard'),

    # Shifokor haqida batafsil ma'lumot (ID bo'yicha)
    path('dashboard/doctors/<int:pk>/', doctor_detail_dashboard, name='doctor_detail_dashboard'),



    path('dashboard/lab-tests/', lab_tests_list_dashboard, name='lab_tests_list_dashboard'),
    path('dashboard/lab-tests/<int:pk>/', lab_test_detail_dashboard, name='lab_test_detail_dashboard'),

    path('dashboard/patients/', patients_list_dashboard, name='patients_list_dashboard'),
    path('dashboard/patients/create/', patient_create_dashboard, name='patient_create_dashboard'),
    path('dashboard/patients/<int:pk>/edit/', patient_edit_dashboard, name='patient_edit_dashboard'),
    path('dashboard/patients/<int:pk>/delete/', patient_delete_dashboard, name='patient_delete_dashboard'),
    path('dashboard/patients/<int:pk>/', patient_detail_dashboard, name='patient_detail_dashboard'),

    path('dashboard/contacts/', contact_messages_list, name='contact_messages_list'),
    path('dashboard/contacts/<int:pk>/', contact_message_detail, name='contact_message_detail'),
    path('dashboard/contacts/<int:pk>/delete/', contact_message_delete, name='contact_message_delete'),
    path('dashboard/contacts/<int:pk>/read/', mark_read_view, name='mark_as_read'),

    path('dashboard/appointments/', appointment_list_dashboard, name='appointments_list'),
    path('dashboard/appointments/create/', book_appointment_dashboard, name='book_appointment_dashboard'),
    path('dashboard/appointments/<int:pk>/edit/', appointment_edit_dashboard, name='appointment_edit'),
    path('dashboard/appointments/<int:pk>/delete/', appointment_delete_dashboard, name='appointment_delete'),
    path('dashboard/appointments/<int:pk>/', appointment_detail_dashboard, name='appointment_detail'),
    path('appointments/<int:pk>/status/<str:status>/', change_status, name='change_status'),

    # API (Dinamik tanlovlar uchun)
    path('dashboard/api/get-doctors/', get_doctors_by_department, name='get_doctors_by_department'),
    path('dashboard/api/available-slots/', get_available_slots, name='get_available_slots'),

    # Online Navbatlar (Dashboard qismi)
    path('dashboard/online-appointments/', online_appointments_list, name='dashboard_online_appointments_list'),
    path('dashboard/online-appointments/<int:pk>/confirm/', confirm_online_appointment,
         name='dashboard_confirm_online_appointment'),
    path('dashboard/online-appointments/<int:pk>/delete/', delete_online_appointment,
         name='dashboard_delete_online_appointment'),
    path('dashboard/online-appointments/<int:pk>/view/', view_online_appointment_json,
         name='dashboard_view_online_appointment_json'),
    path('dashboard/online-appointments/<int:pk>/edit-modal/', edit_online_appointment_modal,
         name='dashboard_edit_online_appointment_modal'),
    path('dashboard/online-appointments/<int:pk>/update/', update_online_appointment,
         name='dashboard_update_online_appointment'),



    path('profile/password/verify/', change_password_verify, name='change_password_verify'),
    path('profile/password/change/', actual_change_password, name='actual_change_password'),

    # Profilni tahrirlash tizimi
    path('profile/verify/', profile_verify, name='profile_verify'), # Avval parolni so'raydi
    path('profile/edit/', profile_edit, name='profile_edit'),       # Keyin tahrirlashga o'tadi






    path('dashboard/medical-records/', medical_records_list, name='medical_records_list'),
    path('dashboard/medical-records/<int:pk>/view/', view_medical_record_json, name='view_medical_record_json'),
    path('dashboard/medical-records/<int:pk>/pdf/', export_medical_record_pdf, name='export_medical_record_pdf'),

    path('dashboard/payments/', payments_list, name='dashboard_payments_list'),

    # Qo'shish
    path('dashboard/payments/create/', payment_create, name='payment_create'),

    # Tahrirlash
    path('dashboard/payments/<int:pk>/update/', payment_update, name='payment_update'),

    # O'chirish
    path('dashboard/payments/<int:pk>/delete/', payment_delete, name='payment_delete'),

    # ID bo'yicha JSON ko'rish (Modal uchun)
    path('dashboard/payments/<int:pk>/view/', payment_view_json, name='payment_view_json'),    # path('dashboard/contacts/<int:pk>/send-reply/', send_auto_reply, name='send_auto_reply'),










    path('dashboard/admin_dashboard_index/', reception_admin_dashboard, name='dashboard_reseption_index_dashboard'),

    path('doctor/login/', doctor_dashboard_login, name='doctor_dashboard_login'),
    # Nomini 'doctor_dashboard' qildik, HTMLda shunday yozilgani uchun
    path('doctor/dashboard/', doctor_dashboard_index, name='doctor_dashboard'),

    path('doctor_dashboard/departments/', doctor_departments_list, name='doctor_departments_list'),
    path('doctor_dashboard/departments/<int:pk>/', doctor_department_detail, name='doctor_department_detail'),

    path('doctor_dashboard/services/', doctor_services_list, name='doctor_services_list_dashboard'),
    path('doctor_dashboard/services/<int:pk>/', doctor_service_detail, name='doctor_service_detail_dashboard'),

    path('doctor_dashboard/lab-tests/', doctor_lab_tests_list_dashboard, name='doctor_lab_tests_list_dashboard'),
    path('doctor_dashboard/lab-tests/<int:pk>/', doctor_lab_test_detail_dashboard, name='doctor_lab_test_detail_dashboard'),


    path('doctor/medical-records/', doctor_medical_records_list, name='doctor_medical_records_list'),
    path('doctor/medical-records/create/', doctor_medical_record_create, name='doctor_medical_record_create'),
    path('doctor/medical-records/<int:pk>/edit/', doctor_medical_record_edit, name='doctor_medical_record_edit'),
    path('doctor/medical-records/<int:pk>/delete/', doctor_medical_record_delete, name='doctor_medical_record_delete'),
    path('doctor/medical-records/<int:pk>/pdf/', export_medical_record_pdf, name='doctor_medical_record_pdf_export'),







    path('doctor_dashboard/patients/', doctor_patients_list_dashboard, name='doctor_patients_list_dashboard'),
    path('doctor_dashboard/patients/create/', doctor_patient_create_dashboard, name='doctor_patient_create_dashboard'),
    path('doctor_dashboard/patients/<int:pk>/edit/', doctor_patient_edit_dashboard, name='doctor_patient_edit_dashboard'),
    path('doctor_dashboard/patients/<int:pk>/delete/', doctor_patient_delete_dashboard, name='doctor_patient_delete_dashboard'),
    path('doctor_dashboard/patients/<int:pk>/', doctor_patient_detail_dashboard, name='doctor_patient_detail_dashboard'),



    path('doctor/my-appointments/', doctor_my_appointments, name='doctor_my_appointments'),
    path('doctor/api/check-appointments/',check_new_appointments, name='check_new_appointments'),
    path('doctor/mark-received/<int:app_id>/<str:app_type>/', mark_as_received, name='mark_received'),

    path('doctor_admin/dashboard/', doctor_admin_dashboard, name='doctor_admin_dashboard'),
    path('doctor-admin/profile/', doctor_admin_profile_edit, name='doctor_admin_profile_edit'),

    # Xavfsizlik
    path('doctor-admin/security/', doctor_admin_security_edit, name='doctor_admin_security_edit'),





    # path('profile/', profile_view, name='profile_view'),
    # path('update-status/<int:pk>/', update_appointment_status, name='update_status'),
# Auth
# path('login/', MyLoginView.as_view(), name='login'),
#     path('logout/', custom_logout, name='logout'), # Biz yozgan custom_logout
#     path('reception/dashboard/', reception_dashboard, name='reception_dash'),
#     path('reception/profile/', profile_view, name='profile_view'),
#
#     # --- PAROLNI O'ZGARTIRISH ---
#     path('reception/password-change/',
#          PasswordChangeView.as_view(
#              template_name='registration/password_change.html',
#              success_url=reverse_lazy('profile_view')
#          ),
#          name='password_change'),














]
from django.views.static import serve
from django.urls import re_path
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 2. Render serverida (DEBUG = False bo'lganda ham) media rasmlarni ochish uchun majburiy ruxsat:
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# 404 xatolikni boshqarish (bunga tegmang, tursin)
handler404 = 'mainApp.views.custom_404'