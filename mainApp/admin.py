# from django.contrib import admin
# from django.utils.html import format_html
# from django.db.models import Sum, Count
# from django.utils import timezone
# from import_export.admin import ImportExportModelAdmin  # Excel eksport uchun
# from .models import (
#     Department, Service, Staff, DoctorProfile,
#     Patient, OnlineAppointment, Appointment,
#     MedicalRecord, LabTest, LabReferral, Payment, News
# )
#
#
# # --- 1. ADMIN ACTIONS (Ommaviy amallar) ---
# @admin.action(description="Tanlanganlarni 'Tasdiqlangan' deb belgilash")
# def mark_confirmed(modeladmin, request, queryset):
#     queryset.update(is_confirmed=True)
#
#
# @admin.action(description="Tanlanganlarni 'Yakunlandi' deb belgilash")
# def mark_completed(modeladmin, request, queryset):
#     queryset.update(status='completed')
#
#
# # --- 2. ASOSIY ADMIN SOZLAMALARI ---
#
# @admin.register(Appointment)
# class AppointmentAdmin(ImportExportModelAdmin):
#     # 'status' maydonini ro'yxatga qo'shdik (list_editable ishlashi uchun shart)
#     list_display = ('id', 'patient_link', 'doctor', 'service', 'date_status', 'time_slot', 'status', 'colored_status')
#
#     # Endi bu xato bermaydi
#     list_editable = ('status',)
#
#     list_display_links = ('id', 'patient_link')  # Qaysi ustunlar tahrirlash sahifasiga olib kirsin
#     list_filter = ('status', 'date', 'doctor', 'service__department')
#     search_fields = ('patient__full_name', 'patient__phone', 'doctor__full_name')
#     date_hierarchy = 'date'
#     actions = [mark_completed]
#     # Bemor profiliga tezkor o'tish linki
#     def patient_link(self, obj):
#         return format_html('<a href="/admin/mainApp/patient/{}/change/" style="font-weight:bold;">{}</a>',
#                            obj.patient.id, obj.patient.full_name)
#
#     patient_link.short_description = "Bemor"
#
#     # Statusga qarab rangli tugmalar
#     def colored_status(self, obj):
#         colors = {
#             'waiting': '#ffc107',  # Sariq
#             'paid': '#28a745',  # Yashil
#             'completed': '#17a2b8',  # Moviy
#             'cancelled': '#dc3545',  # Qizil
#         }
#         return format_html(
#             '<span style="background: {}; color: white; padding: 3px 10px; border-radius: 12px; font-weight: 500;">{}</span>',
#             colors.get(obj.status, '#6c757d'),
#             obj.get_status_display()
#         )
#
#     colored_status.short_description = "Holati"
#
#     # Sana o'tib ketgan bo'lsa ogohlantirish
#     def date_status(self, obj):
#         if obj.date < timezone.now().date() and obj.status == 'waiting':
#             return format_html('<span style="color: red; font-weight: bold;">⚠️ {}</span>', obj.date)
#         return obj.date
#
#     date_status.short_description = "Sana"
#
#
# @admin.register(OnlineAppointment)
# class OnlineAppointmentAdmin(admin.ModelAdmin):
#     list_display = ('patient_name', 'patient_phone', 'doctor', 'date', 'time_slot', 'status_icon')
#     list_filter = ('is_confirmed', 'date')
#     search_fields = ('patient_name', 'patient_phone')
#     actions = [mark_confirmed]
#
#     def status_icon(self, obj):
#         if obj.is_confirmed:
#             return format_html('<span style="color: green; font-size: 1.2em;">✔</span>')
#         return format_html('<span style="color: orange; font-size: 1.2em;">⏳</span>')
#
#     status_icon.short_description = "Tasdiq"
#
#
# @admin.register(Patient)
# class PatientAdmin(ImportExportModelAdmin):
#     list_display = ('full_name', 'phone', 'total_visits', 'last_visit')
#     search_fields = ('full_name', 'phone')
#
#     # Bemorning jami tashriflar soni
#     def total_visits(self, obj):
#         return obj.appointments.count()
#
#     total_visits.short_description = "Tashriflar"
#
#     def last_visit(self, obj):
#         last = obj.appointments.order_by('-date').first()
#         return last.date if last else "-"
#
#     last_visit.short_description = "Oxirgi sana"
#
#
# @admin.register(Payment)
# class PaymentAdmin(ImportExportModelAdmin):
#     list_display = ('appointment', 'amount_display', 'payment_type', 'created_at')
#     list_filter = ('payment_type', 'created_at')
#     date_hierarchy = 'created_at'
#
#     def amount_display(self, obj):
#         return format_html('<b style="color: #28a745;">{:,.0f} so\'m</b>', obj.amount)
#
#     amount_display.short_description = "Summa"
#
#     # Admin panelning pastki qismida jami tushumni ko'rsatish (Summary)
#     def changelist_view(self, request, extra_context=None):
#         response = super().changelist_view(request, extra_context)
#         try:
#             qs = response.context_data['cl'].queryset
#             extra_context = extra_context or {}
#             extra_context['total_revenue'] = qs.aggregate(Sum('amount'))['amount__sum'] or 0
#         except (AttributeError, KeyError):
#             pass
#         return super().changelist_view(request, extra_context=extra_context)
#
#
# # --- 3. INLINE SOZLAMALAR ---
# class DoctorProfileInline(admin.StackedInline):
#     model = DoctorProfile
#     can_delete = False
#
#
# @admin.register(Staff)
# class StaffAdmin(admin.ModelAdmin):
#     list_display = ('full_name', 'role', 'department', 'phone', 'avatar')
#     inlines = [DoctorProfileInline]
#
#     def avatar(self, obj):
#         if obj.photo:
#             return format_html('<img src="{}" style="width: 40px; height: 40px; border-radius: 50%;" />', obj.photo.url)
#         return "Rasm yo'q"
#
#
# # Qolgan modellar
# admin.site.register(Department)
# admin.site.register(Service)
# admin.site.register(MedicalRecord)
# admin.site.register(LabReferral)
# admin.site.register(LabTest)
# admin.site.register(News)

#
# from django.contrib import admin
# from django.utils.html import format_html
# from django.db.models import Sum
# from django.utils import timezone
# from import_export.admin import ImportExportModelAdmin
# from .models import (
#     Department, Service, Staff, DoctorProfile,
#     Patient, OnlineAppointment, Appointment,
#     MedicalRecord, LabTest, LabReferral, Payment, News, StaffSocialContact, StaffEducation, StaffExperience
# )
# from django.utils.safestring import mark_safe
# from .models import ContactMessage
#
#
#
# @admin.register(ContactMessage)
# class ContactMessageAdmin(admin.ModelAdmin):
#     # Ro'yxatda ko'rinadigan ustunlar
#     list_display = ('name', 'subject', 'email', 'created_at', 'is_read')
#
#     # O'ng tomonda filtrlar paneli
#     list_filter = ('is_read', 'created_at')
#
#     # Qidiruv maydonlari
#     search_fields = ('name', 'email', 'subject', 'message')
#
#     # Faqat o'qish uchun maydonlar (tahrirlab bo'lmaydi)
#     readonly_fields = ('created_at',)
#
#     # Ro'yxatning o'zida "O'qildimi?" belgisini o'zgartirish imkoniyati
#     list_editable = ('is_read',)
#
#     # Sanaga ko'ra tartiblash (eng oxirgisi tepada)
#     ordering = ('-created_at',)
#
#     # Admin paneldagi blok nomi (ixtiyoriy)
#     fieldsets = (
#         ("Foydalanuvchi ma'lumotlari", {
#             'fields': ('name', 'email')
#         }),
#         ("Xabar mazmuni", {
#             'fields': ('subject', 'message')
#         }),
#         ("Status", {
#             'fields': ('is_read', 'created_at')
#         }),
#     )
#
#
# # --- 0. ASOSIY AVTOMATLASHTIRISH KLASSI ---
# class BaseAuditAdmin(admin.ModelAdmin):
#     """Audit va avtomatik maydonlarni boshqarish"""
#     readonly_fields = ('created_at', 'updated_at', 'created_by')
#
#     # Ma'lumot qo'shish sahifasida bu maydonlarni ko'rsatmaslik
#     exclude = ('created_by',)
#
#     def save_model(self, request, obj, form, change):
#         if not obj.pk:
#             obj.created_by = request.user
#         super().save_model(request, obj, form, change)
#
#
# class BaseAuditImportExportAdmin(ImportExportModelAdmin, BaseAuditAdmin):
#     pass
#
#
# # --- 1. ADMIN ACTIONS ---
# @admin.action(description="Tanlanganlarni 'Tasdiqlangan' deb belgilash")
# def mark_confirmed(modeladmin, request, queryset):
#     queryset.update(is_confirmed=True)
#
#
# @admin.action(description="Tanlanganlarni 'Yakunlandi' deb belgilash")
# def mark_completed(modeladmin, request, queryset):
#     queryset.update(status='completed')
#
#
# # --- 2. INLINE KLASSLAR ---
# class DoctorProfileInline(admin.StackedInline):
#     model = DoctorProfile
#     can_delete = False
#     exclude = ('created_by',)
#     fk_name = "staff"
#
#
# # Aloqa ma'lumotlari uchun (1 tadan ko'p bo'lmagani uchun StackedInline qulay)
# class SocialContactInline(admin.StackedInline):
#     model = StaffSocialContact
#     extra = 1
#     max_num = 1  # 1 tadan ortiq aloqa ma'lumoti shart emas
#     exclude = ('created_by',)
#
#
# # Tahsil olgan joylari uchun (Jadval ko'rinishida)
# class EducationInline(admin.TabularInline):
#     model = StaffEducation
#     extra = 1  # Bo'sh qator soni
#     exclude = ('created_by',)
#
#
# # Ish tajribasi uchun (Jadval ko'rinishida)
# class ExperienceInline(admin.TabularInline):
#     model = StaffExperience
#     extra = 1
#     exclude = ('created_by',)
#
#
# # --- STAFF ADMINNI YANGILASH ---
#
# @admin.register(Staff)
# class StaffAdmin(BaseAuditAdmin):
#     list_display = ('id', 'avatar_circle', 'full_name', 'role', 'department', 'created_by', 'created_at')
#     list_filter = ('role', 'department', 'created_by')
#     search_fields = ('full_name', 'phone')
#
#     # BU YERGA YANGI INLINELARNI QO'SHAMIZ
#     inlines = [
#         DoctorProfileInline,
#         SocialContactInline,
#         EducationInline,
#         ExperienceInline
#     ]
#
#     exclude = ('user', 'created_by')
#
#     def avatar_circle(self, obj):
#         url = obj.photo.url if obj.photo else '/static/jazzmin/img/user.png'
#         return format_html(
#             '<img src="{}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; border: 1px solid #ddd;" />',
#             url)
#
#     avatar_circle.short_description = "Rasm"
#
#     def save_model(self, request, obj, form, change):
#         if not change:
#             obj.created_by = request.user
#         super().save_model(request, obj, form, change)
#
# # --- 3. JADVALLAR SOZLAMALARI ---
#
# @admin.register(Appointment)
# class AppointmentAdmin(BaseAuditImportExportAdmin):
#     list_display = ('id', 'patient_link', 'doctor', 'service', 'date_status', 'time_slot', 'status', 'created_by',
#                     'created_at')
#     list_editable = ('status',)
#     list_filter = ('status', 'date', 'doctor', 'created_by')
#     search_fields = ('patient__full_name', 'doctor__full_name')
#
#     def patient_link(self, obj):
#         return format_html('<a href="/admin/mainApp/patient/{}/change/">{}</a>', obj.patient.id, obj.patient.full_name)
#
#     patient_link.short_description = "Bemor"
#
#     def date_status(self, obj):
#         if obj.date < timezone.now().date() and obj.status == 'waiting':
#             return format_html('<span style="color: red; font-weight: bold;">⚠️ {}</span>', obj.date)
#         return obj.date
#
#
# @admin.register(Patient)
# class PatientAdmin(BaseAuditImportExportAdmin):
#     list_display = ('id', 'full_name', 'phone', 'gender', 'created_by', 'created_at')
#     search_fields = ('full_name', 'phone')
#
#
# @admin.register(Staff)
# class StaffAdmin(BaseAuditAdmin):
#     list_display = ('id', 'avatar_circle', 'full_name', 'role', 'department', 'created_by', 'created_at')
#     list_filter = ('role', 'department', 'created_by') # Kim yaratganini filtrga qo'shdik
#     search_fields = ('full_name', 'phone')
#     inlines = [DoctorProfileInline]
#
#     # 'user' maydonini formadan olib tashlaymiz (ixtiyoriy holga keldi)
#     exclude = ('user', 'created_by')
#
#     def avatar_circle(self, obj):
#         url = obj.photo.url if obj.photo else '/static/jazzmin/img/user.png'
#         return format_html(
#             '<img src="{}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; border: 1px solid #ddd;" />',
#             url)
#     avatar_circle.short_description = "Rasm"
#
#     # BU YERDA obj.user = request.user SATRINI OLIB TASHLADIK!
#     def save_model(self, request, obj, form, change):
#         if not change:  # Agar yangi xodim qo'shilayotgan bo'lsa
#             obj.created_by = request.user
#         super().save_model(request, obj, form, change)
#
#
# @admin.register(Department)
# class DepartmentAdmin(BaseAuditAdmin):
#     list_display = ('id', 'department_icon', 'name', 'created_by', 'created_at')
#     search_fields = ('name',)
#
#     def department_icon(self, obj):
#         if obj.image:
#             return format_html(
#                 '<img src="{}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover;" />',
#                 obj.image.url)
#         return "📁"
#
#     department_icon.short_description = "Rasm"
#
#
# @admin.register(Payment)
# class PaymentAdmin(BaseAuditImportExportAdmin):
#     list_display = ('id', 'amount_display', 'payment_type', 'is_paid', 'created_by', 'created_at')
#     search_fields = ('amount', 'appointment__patient__full_name')
#
#     def amount_display(self, obj):
#         return format_html('<b style="color: #28a745;">{:,.0f} so\'m</b>', obj.amount)
#
#
# @admin.register(OnlineAppointment)
# class OnlineAppointmentAdmin(BaseAuditAdmin):
#     list_display = ('id', 'patient_name', 'patient_phone', 'doctor', 'date', 'is_confirmed', 'created_by')
#     actions = [mark_confirmed]
#
#
# @admin.register(Service)
# class ServiceAdmin(admin.ModelAdmin):
#     # list_display dagi 'author' ni 'created_by' ga almashtirdik
#     list_display = ('display_image', 'name', 'department', 'price', 'created_by')
#     list_filter = ('department',)
#     search_fields = ('name',)
#
#     # "Kim yaratdi" maydonini admin panelda tanlamaslik uchun exclude qilamiz
#     exclude = ('created_by',)
#
#     # Rasm ko'rinishi uchun funksiya
#     def display_image(self, obj):
#         if obj.image:
#             return mark_safe(f'<img src="{obj.image.url}" width="75" height="auto" style="border-radius: 8px;" />')
#         return "Rasm yo'q"
#
#     display_image.short_description = 'Rasm'
#
#     # Avtomatik saqlash mantiqi
#     def save_model(self, request, obj, form, change):
#         if not change:  # Agar yangi obyekt yaratilayotgan bo'lsa
#             obj.created_by = request.user
#         super().save_model(request, obj, form, change)
#
#
# @admin.register(MedicalRecord)
# class MedicalRecordAdmin(BaseAuditAdmin):
#     list_display = ('id', 'patient', 'doctor', 'diagnosis', 'created_by', 'created_at')
#
#
# @admin.register(LabReferral)
# class LabReferralAdmin(BaseAuditAdmin):
#     list_display = ('id', 'patient', 'test', 'status', 'created_by', 'created_at')
#
#
# @admin.register(LabTest)
# class LabTestAdmin(BaseAuditAdmin):
#     list_display = ('id', 'name', 'price', 'created_by')
#
#
# @admin.register(News)
# class NewsAdmin(BaseAuditAdmin):
#     list_display = ('id', 'news_photo', 'title', 'created_by', 'created_at')
#
#     def news_photo(self, obj):
#         if obj.image:
#             return format_html(
#                 '<img src="{}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover;" />',
#                 obj.image.url)
#         return "📰"
#
#     news_photo.short_description = "Rasm"

#
# from django.contrib import admin
# from django.utils.html import format_html
# from django.db.models import Sum
# from django.utils import timezone
# from import_export.admin import ImportExportModelAdmin
# from .models import (
#     Department, Service, Staff, DoctorProfile,
#     Patient, OnlineAppointment, Appointment,
#     MedicalRecord, LabTest, LabReferral, Payment, News,
#     StaffSocialContact, StaffEducation, StaffExperience
# )
# from django.utils.safestring import mark_safe
# from .models import ContactMessage
#
#
# @admin.register(ContactMessage)
# class ContactMessageAdmin(admin.ModelAdmin):
#     # Ro'yxatda ko'rinadigan ustunlar
#     list_display = ('name', 'subject', 'email', 'created_at', 'is_read')
#
#     # O'ng tomonda filtrlar paneli
#     list_filter = ('is_read', 'created_at')
#
#     # Qidiruv maydonlari
#     search_fields = ('name', 'email', 'subject', 'message')
#
#     # Faqat o'qish uchun maydonlar (tahrirlab bo'lmaydi)
#     readonly_fields = ('created_at',)
#
#     # Ro'yxatning o'zida "O'qildimi?" belgisini o'zgartirish imkoniyati
#     list_editable = ('is_read',)
#
#     # Sanaga ko'ra tartiblash (eng oxirgisi tepada)
#     ordering = ('-created_at',)
#
#     # Admin paneldagi blok nomi (ixtiyoriy)
#     fieldsets = (
#         ("Foydalanuvchi ma'lumotlari", {
#             'fields': ('name', 'email')
#         }),
#         ("Xabar mazmuni", {
#             'fields': ('subject', 'message')
#         }),
#         ("Status", {
#             'fields': ('is_read', 'created_at')
#         }),
#     )
#
#
# # --- 0. ASOSIY AVTOMATLASHTIRISH KLASSI ---
# class BaseAuditAdmin(admin.ModelAdmin):
#     """Audit va avtomatik maydonlarni boshqarish"""
#     readonly_fields = ('created_at', 'updated_at', 'created_by')
#
#     # Ma'lumot qo'shish sahifasida bu maydonlarni ko'rsatmaslik
#     exclude = ('created_by',)
#
#     def save_model(self, request, obj, form, change):
#         if not obj.pk:
#             obj.created_by = request.user
#         super().save_model(request, obj, form, change)
#
#
# class BaseAuditImportExportAdmin(ImportExportModelAdmin, BaseAuditAdmin):
#     pass
#
#
# # --- 1. ADMIN ACTIONS ---
# @admin.action(description="Tanlanganlarni 'Tasdiqlangan' deb belgilash")
# def mark_confirmed(modeladmin, request, queryset):
#     queryset.update(is_confirmed=True)
#
#
# @admin.action(description="Tanlanganlarni 'Yakunlandi' deb belgilash")
# def mark_completed(modeladmin, request, queryset):
#     queryset.update(status='completed')
#
#
# # --- 2. INLINE KLASSLAR ---
# class DoctorProfileInline(admin.StackedInline):
#     model = DoctorProfile
#     can_delete = False
#     exclude = ('created_by',)
#     fk_name = "staff"
#
# class SocialContactInline(admin.StackedInline):
#     model = StaffSocialContact
#     extra = 1
#     max_num = 1
#     exclude = ('created_by',)
#
# class EducationInline(admin.TabularInline):
#     model = StaffEducation
#     extra = 1
#     exclude = ('created_by',)
#
# class ExperienceInline(admin.TabularInline):
#     model = StaffExperience
#     extra = 1
#     exclude = ('created_by',)
#
#
# # --- 3. JADVALLAR SOZLAMALARI ---
#
# @admin.register(Staff)
# class StaffAdmin(BaseAuditAdmin):
#     list_display = ('id', 'avatar_circle', 'full_name', 'role', 'department', 'created_by', 'created_at')
#     list_filter = ('role', 'department', 'created_by')
#     search_fields = ('full_name', 'phone')
#     inlines = [
#         DoctorProfileInline,
#         SocialContactInline,
#         EducationInline,
#         ExperienceInline
#     ]
#
#     # 'user' maydonini formadan olib tashlaymiz
#     exclude = ('user', 'created_by')
#
#     def avatar_circle(self, obj):
#         url = obj.photo.url if obj.photo else '/static/jazzmin/img/user.png'
#         return format_html(
#             '<img src="{}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; border: 1px solid #ddd;" />',
#             url)
#     avatar_circle.short_description = "Rasm"
#
#     def save_model(self, request, obj, form, change):
#         if not change:
#             obj.created_by = request.user
#         super().save_model(request, obj, form, change)
#
#
# @admin.register(Appointment)
# class AppointmentAdmin(BaseAuditImportExportAdmin):
#     list_display = ('id', 'patient_link', 'doctor', 'service', 'date_status', 'time_slot', 'status', 'created_by',
#                     'created_at')
#     list_editable = ('status',)
#     list_filter = ('status', 'date', 'doctor', 'created_by')
#     search_fields = ('patient__full_name', 'doctor__full_name')
#
#     def patient_link(self, obj):
#         return format_html('<a href="/admin/mainApp/patient/{}/change/">{}</a>', obj.patient.id, obj.patient.full_name)
#
#     patient_link.short_description = "Bemor"
#
#     def date_status(self, obj):
#         if obj.date < timezone.now().date() and obj.status == 'waiting':
#             return format_html('<span style="color: red; font-weight: bold;">⚠️ {}</span>', obj.date)
#         return obj.date
#
#
# @admin.register(Patient)
# class PatientAdmin(BaseAuditImportExportAdmin):
#     list_display = ('id', 'full_name', 'phone', 'gender', 'created_by', 'created_at')
#     search_fields = ('full_name', 'phone')
#
#
# @admin.register(Department)
# class DepartmentAdmin(BaseAuditAdmin):
#     list_display = ('id', 'department_icon', 'name', 'created_by', 'created_at')
#     search_fields = ('name',)
#
#     def department_icon(self, obj):
#         if obj.image:
#             return format_html(
#                 '<img src="{}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover;" />',
#                 obj.image.url)
#         return "📁"
#
#     department_icon.short_description = "Rasm"
#
#
# @admin.register(Payment)
# class PaymentAdmin(BaseAuditImportExportAdmin):
#     list_display = ('id', 'amount_display', 'payment_type', 'is_paid', 'created_by', 'created_at')
#     search_fields = ('amount', 'appointment__patient__full_name')
#
#     def amount_display(self, obj):
#         return format_html('<b style="color: #28a745;">{:,.0f} so\'m</b>', obj.amount)
#
#
# @admin.register(OnlineAppointment)
# class OnlineAppointmentAdmin(BaseAuditAdmin):
#     list_display = ('id', 'patient_name', 'patient_phone', 'doctor', 'date', 'is_confirmed', 'created_by')
#     actions = [mark_confirmed]
#
#
# @admin.register(Service)
# class ServiceAdmin(admin.ModelAdmin):
#     list_display = ('display_image', 'name', 'department', 'price', 'created_by')
#     list_filter = ('department',)
#     search_fields = ('name',)
#     exclude = ('created_by',)
#
#     def display_image(self, obj):
#         if obj.image:
#             return mark_safe(f'<img src="{obj.image.url}" width="75" height="auto" style="border-radius: 8px;" />')
#         return "Rasm yo'q"
#
#     display_image.short_description = 'Rasm'
#
#     def save_model(self, request, obj, form, change):
#         if not change:
#             obj.created_by = request.user
#         super().save_model(request, obj, form, change)
#
#
# @admin.register(MedicalRecord)
# class MedicalRecordAdmin(BaseAuditAdmin):
#     list_display = ('id', 'patient', 'doctor', 'diagnosis', 'created_by', 'created_at')
#
#
# @admin.register(LabReferral)
# class LabReferralAdmin(BaseAuditAdmin):
#     list_display = ('id', 'patient', 'test', 'status', 'created_by', 'created_at')
#
#
# @admin.register(LabTest)
# class LabTestAdmin(BaseAuditAdmin):
#     list_display = ('id', 'name', 'price', 'created_by')
#
#
# @admin.register(News)
# class NewsAdmin(BaseAuditAdmin):
#     list_display = ('id', 'news_photo', 'title', 'created_by', 'created_at')
#
#     def news_photo(self, obj):
#         if obj.image:
#             return format_html(
#                 '<img src="{}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover;" />',
#                 obj.image.url)
#         return "📰"
#
#     news_photo.short_description = "Rasm"

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from django.utils import timezone
from import_export.admin import ImportExportModelAdmin
from .models import (
    Department, Service, Staff, DoctorProfile,
    Patient, OnlineAppointment, Appointment,
    MedicalRecord, LabTest, LabReferral, Payment, News,
    StaffSocialContact, StaffEducation, StaffExperience,ActionLog
)
from django.utils.safestring import mark_safe
from .models import ContactMessage
from django import forms

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    list_editable = ('is_read',)
    ordering = ('-created_at',)
    fieldsets = (
        ("Foydalanuvchi ma'lumotlari", {'fields': ('name', 'email')}),
        ("Xabar mazmuni", {'fields': ('subject', 'message')}),
        ("Status", {'fields': ('is_read', 'created_at')}),
    )


class BaseAuditAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at', 'updated_at', 'created_by')
    exclude = ('created_by',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class BaseAuditImportExportAdmin(ImportExportModelAdmin, BaseAuditAdmin):
    pass


@admin.action(description="Tanlanganlarni 'Tasdiqlangan' deb belgilash")
def mark_confirmed(modeladmin, request, queryset):
    queryset.update(is_confirmed=True)


@admin.action(description="Tanlanganlarni 'Yakunlandi' deb belgilash")
def mark_completed(modeladmin, request, queryset):
    queryset.update(status='completed')


class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    exclude = ('created_by',)
    fk_name = "staff"

class SocialContactInline(admin.StackedInline):
    model = StaffSocialContact
    extra = 1
    max_num = 1
    exclude = ('created_by',)

class EducationInline(admin.TabularInline):
    model = StaffEducation
    extra = 1
    exclude = ('created_by',)

class ExperienceInline(admin.TabularInline):
    model = StaffExperience
    extra = 1
    exclude = ('created_by',)


@admin.register(Staff)
class StaffAdmin(BaseAuditAdmin):
    list_display = ('id', 'avatar_circle', 'full_name', 'role', 'department', 'created_by', 'created_at')
    list_filter = ('role', 'department', 'created_by')
    search_fields = ('full_name', 'phone')
    inlines = [DoctorProfileInline, SocialContactInline, EducationInline, ExperienceInline]
    exclude = ( 'created_by',)
    fields = ('user', 'role', 'department', 'full_name', 'photo', 'phone')

    def avatar_circle(self, obj):
        url = obj.photo.url if obj.photo else '/static/jazzmin/img/user.png'
        return format_html('<img src="{}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover; border: 1px solid #ddd;" />', url)
    avatar_circle.short_description = "Rasm"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class AppointmentAdminForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'
        widgets = {
            # 'doctor' maydonini Select2 dan oddiy dropdown-ga aylantiramiz
            'doctor': forms.Select(attrs={'class': 'no-select2'}),
        }

@admin.register(Appointment)
class AppointmentAdmin(BaseAuditImportExportAdmin):
    # 1. Ro'yxatda ko'rinadigan ustunlar
    list_display = (
        'id',
        'display_patient_red',  # Ism va telefon (waiting bo'lsa qizil)
        'department',
        'doctor',
        'get_service_info',
        'date_status',
        'time_slot',
        'status',
        'is_consultation'
    )

    # 2. Ichiga kirmasdan o'zgartirish (Statusni tezkor boshqarish)
    list_editable = ('status',)

    # 3. Tartiblash: Avval kutilayotganlar, keyin sana/vaqt
    # 'status' bo'yicha tartiblasak, 'waiting' (w) oxirgi harf bo'lgani uchun
    # bizga mantiqiy tartib kerak. Buning uchun maxsus ordering ishlatamiz.
    ordering = ('status', '-date', '-time_slot')

    # 4. Qidiruv: Bemor, telefon va shifokor bo'yicha
    search_fields = ('patient_name', 'patient_phone', 'doctor__full_name', 'department__name')

    # 5. O'ng tomondagi filtrlar paneli (Yangi qo'shilganlar, status va shifokorlar)
    list_filter = (
        'status',
        'date',
        'department',
        'doctor',
        'is_consultation',
        'created_at'
    )

    # 6. Sana ierarxiyasi (Kalendar bo'yicha qulay navigatsiya)
    date_hierarchy = 'date'

    # 7. Bir sahifadagi yozuvlar soni
    list_per_page = 25

    # 8. Shifokor va bo'limni tezkor qidirish (Autocomplete)
    autocomplete_fields = [ 'doctor', 'department']

    # --- MAXSUS FUNKSIYALAR ---

    def display_patient_red(self, obj):
        """Agar status 'waiting' bo'lsa, qizil rangda, bo'lmasa qora rangda chiqaradi"""
        color = "red" if obj.status == 'waiting' else "#2c3155"
        weight = "bold" if obj.status == 'waiting' else "normal"

        return format_html(
            '<div style="color: {}; font-weight: {};">'
            '<b>{}</b><br>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            color, weight, obj.patient_name, obj.patient_phone
        )

    display_patient_red.short_description = "Bemor (Statusga qarab rang)"

    def get_service_info(self, obj):
        """Xizmat turini chiroyli ko'rsatish"""
        if obj.service:
            return format_html('<span style="color: #00a0e3;">🛠 {}</span>', obj.service.name)
        elif obj.lab_test:
            return format_html('<span style="color: #8e44ad;">🧪 {}</span>', obj.lab_test.name)
        elif obj.is_consultation:
            return format_html('<span style="color: #27ae60;">🩺 Ko‘rik</span>')
        return "Noma'lum"

    get_service_info.short_description = "Xizmat/Tahlil"

    def date_status(self, obj):
        """O'tib ketgan sanalarni ogohlantirish"""
        now_date = timezone.now().date()
        if obj.date < now_date and obj.status == 'waiting':
            return format_html(
                '<span style="background-color: #ffcccc; padding: 3px 8px; border-radius: 4px; color: #cc0000; font-weight: bold;">'
                '⚠️ {} (Muddati o‘tgan)</span>', obj.date
            )
        return obj.date

    date_status.short_description = "Sana"

    # Status ranglari (Admin panelda rangli badge qilib chiqarish)
    def status_colored(self, obj):
        colors = {
            'waiting': '#f39c12',  # To'q sariq
            'received': '#3498db',  # Moviy
            'paid': '#27ae60',  # Yashil
            'completed': '#2ecc71',  # Och yashil
            'cancelled': '#e74c3c'  # Qizil
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 4px 10px; border-radius: 12px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#ccc'), obj.get_status_display()
        )

    # Agar list_display'da statusni rangli qilmoqchi bo'lsangiz:
    # 'status' o'rniga 'status_colored' yozing, lekin list_editable ishlamay qoladi.

    def get_service_info(self, obj):
        if obj.service:
            return f"Xizmat: {obj.service.name}"
        elif obj.lab_test:
            return f"Tahlil: {obj.lab_test.name}"
        elif obj.is_consultation:
            return "🩺 Shifokor ko'rigi"
        return "Noma'lum"
    get_service_info.short_description = "Xizmat turi"

    def date_status(self, obj):
        if obj.date < timezone.now().date() and obj.status == 'waiting':
            return format_html('<span style="color: red; font-weight: bold;">⚠️ {}</span>', obj.date)
        return obj.date

    class Media:
        js = ('js/admin_filter.js',)

@admin.register(Patient)
class PatientAdmin(BaseAuditImportExportAdmin):
    list_display = ('id', 'full_name', 'phone', 'gender', 'created_by', 'created_at')
    search_fields = ('full_name', 'phone')


@admin.register(Department)
class DepartmentAdmin(BaseAuditAdmin):
    list_display = ('id', 'department_icon', 'name', 'created_by', 'created_at')
    search_fields = ('name',)

    def department_icon(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover;" />', obj.image.url)
        return "📁"
    department_icon.short_description = "Rasm"


from django.contrib import admin
from django.utils.html import format_html
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(BaseAuditImportExportAdmin):
    list_display = (
        'id',
        'get_patient_name',
        'get_payment_reason',
        'amount_display',
        'payment_type',
        'is_paid',
        'created_at'
    )

    list_filter = ('is_paid', 'payment_type', 'created_by', 'created_at')

    search_fields = (
        'appointment__patient_name',
        'appointment__patient_phone',
        'online_appointment__patient_name',
        'amount'
    )

    autocomplete_fields = ['appointment', 'online_appointment']

    # MUHIM: Faqat 'amount' va tizim maydonlari readonly bo'lishi kerak.
    # 'service', 'lab_test' va 'is_consultation' readonly bo'lsa,
    # ularni tanlab bo'lmaydi (ayniqsa Online navbatlar uchun).
    readonly_fields = (
        'amount',
        'created_at',
        'updated_at',
        'created_by'
    )

    fieldsets = (
        ("Bemor Navbati", {
            'fields': ('appointment', 'online_appointment'),
            'description': "Klinikaga kelgan yoki Online yozilgan bemorni tanlang."
        }),
        ("To'lov Tafsilotlari (Avtomatik to'ladi)", {
            'fields': ('service', 'lab_test', 'is_consultation', 'amount'),
            'description': "Tanlangan navbat ma'lumotlari asosida to'ldiriladi."
        }),
        ("To'lov Holati", {
            'fields': ('payment_type', 'is_paid'),
        }),
        ("Tizim Ma'lumotlari", {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',),
        }),
    )

    def get_patient_name(self, obj):
        if obj.appointment:
            return obj.appointment.patient_name
        elif obj.online_appointment:
            return obj.online_appointment.patient_name
        return "-"
    get_patient_name.short_description = "Bemor Ismi"

    def get_payment_reason(self, obj):
        if obj.service:
            return format_html('<span style="color: #007bff;">📋 {}</span>', obj.service.name)
        elif obj.lab_test:
            return format_html('<span style="color: #6f42c1;">🧪 {}</span>', obj.lab_test.name)
        elif obj.is_consultation:
            return mark_safe('<span style="color: #fd7e14;">🩺 Shifokor ko\'rigi</span>')
        return "-"
    get_payment_reason.short_description = "To'lov Maqsadi"

    def amount_display(self, obj):
        # Narxni doim modeldagi amount'dan olamiz
        val = obj.amount if obj.amount else 0.0
        formatted_val = "{:,.0f}".format(val).replace(",", " ")
        return format_html('<b style="color: #28a745; font-size: 14px;">{} so\'m</b>', formatted_val)
    amount_display.short_description = "Summa"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(OnlineAppointment)
class OnlineAppointmentAdmin(BaseAuditAdmin):
    # 1. Ro'yxatda ko'rinadigan ustunlar
    list_display = (
        'id',
        'patient_name',
        'patient_phone',
        'department',
        'doctor',
        'date',
        'time_slot',
        'notes',
        'is_confirmed',
        'created_at'
    )

    # 2. Faqat tasdiqlashni ro'yxatning o'zida qoldiramiz
    # Sana va vaqtni olib tashladik, endi ularni o'zgartirish uchun ichiga kirish shart
    list_editable = ('is_confirmed',)

    # 3. Tartiblash (Ordering)
    # Avval is_confirmed bo'yicha (False tepada bo'lishi uchun),
    # keyin sana va vaqt bo'yicha tartiblaydi
    ordering = ('is_confirmed', '-date', '-time_slot')

    # 4. O'ng tomondagi filtrlar
    list_filter = (
        'is_confirmed',
        'department',
        'doctor',
        'date'
    )

    # 5. Qidiruv
    search_fields = ('patient_name', 'patient_phone', 'doctor__full_name')

    # 6. Sana ierarxiyasi
    date_hierarchy = 'date'

    # 7. Boshqa sozlamalar
    list_per_page = 20
    actions = [mark_confirmed]
    autocomplete_fields = ['doctor', 'department']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('display_image', 'name', 'department', 'price', 'created_by')
    list_filter = ('department',)
    search_fields = ('name',)
    exclude = ('created_by',)

    def display_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="75" height="auto" style="border-radius: 8px;" />')
        return "Rasm yo'q"
    display_image.short_description = 'Rasm'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(BaseAuditAdmin):
    list_display = ('id', 'patient', 'doctor', 'diagnosis', 'created_by', 'created_at')


@admin.register(LabReferral)
class LabReferralAdmin(BaseAuditAdmin):
    list_display = ('id', 'patient', 'test', 'status', 'created_by', 'created_at')


@admin.register(LabTest)
class LabTestAdmin(BaseAuditAdmin):
    list_display = ('id', 'name', 'price', 'created_by')


@admin.register(News)
class NewsAdmin(BaseAuditAdmin):
    list_display = ('id', 'news_photo', 'title', 'created_by', 'created_at')

    def news_photo(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 35px; height: 35px; border-radius: 50%; object-fit: cover;" />', obj.image.url)
        return "📰"
    news_photo.short_description = "Rasm"


from django.contrib import admin
from django.utils.html import format_html


from django.utils.safestring import mark_safe
from django.contrib import admin

from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import ActionLog


@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('display_user', 'display_action', 'display_model', 'object_repr', 'timestamp')
    list_filter = ('action', 'timestamp', 'content_type')
    search_fields = ('object_repr', 'user__username', 'user__first_name', 'user__last_name')

    def display_user(self, obj):
        if obj.user:
            # 1. Xodim profilini tekshiramiz
            staff_profile = getattr(obj.user, 'staff_profile', None)
            if staff_profile:
                return f"{staff_profile.full_name} ({staff_profile.get_role_display()})"

            # 2. Agar xodim profili yo'q bo'lsa, lekin u Superuser (Admin) bo'lsa
            if obj.user.is_superuser:
                full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
                # Agar ismi-sharifi bo'sh bo'lsa, loginini ishlatamiz
                display_name = full_name if full_name else obj.user.username
                return f"{display_name} (Admin)"

            # 3. Oddiy foydalanuvchi bo'lsa
            return f"@{obj.user.username} (Foydalanuvchi)"

        return mark_safe('<span style="color: gray;">Tizim (Avtomatik)</span>')

    def display_action(self, obj):
        # Harakat turlari uchun ranglar lug'ati
        # 'create', 'update', 'delete' so'zlari sizning modellaringizda qanday yozilganiga qarab moslang
        action_styles = {
            'create': 'color: #28a745; font-weight: bold;',  # Yashil
            'update': 'color: #007bff; font-weight: bold;',  # Ko'k
            'delete': 'color: #dc3545; font-weight: bold;',  # Qizil
            'Yaratildi': 'color: #28a745; font-weight: bold;',
            'Tahrirlandi': 'color: #007bff; font-weight: bold;',
            'O\'chirildi': 'color: #dc3545; font-weight: bold;',
        }

        style = action_styles.get(obj.action, 'color: black;')
        return mark_safe(f'<span style="{style}">{obj.action}</span>')

    display_action.short_description = "Harakat"

    def display_model(self, obj):
        if obj.content_type:
            # Model nomini tushunarliroq qilish (masalan, Payment -> To'lov)
            return obj.content_type.model.capitalize()
        return "-"

    display_model.short_description = "Model / Bo'lim"

    # 1. Yangi harakat qo'shish tugmasini olib tashlaydi
    def has_add_permission(self, request):
        return False

    # 2. Mavjud loglarni tahrirlash imkoniyatini yopadi
    def has_change_permission(self, request, obj=None):
        return False

    # 3. Loglarni o'chirish imkoniyatini yopadi (ixtiyoriy, lekin xavfsizlik uchun tavsiya etiladi)
    def has_delete_permission(self, request, obj=None):
        return False

    # 4. Hammasini faqat o'qish rejimi (Read-only)ga o'tkazadi
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

