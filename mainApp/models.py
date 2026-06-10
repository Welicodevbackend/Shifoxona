from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .middleware import get_current_user # Middleware dan foydalanamiz

class ActionLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Yaratildi'),
        ('update', 'Tahrirlandi'),
        ('delete', "O'chirildi"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Mas'ul xodim")
    action = models.CharField("Harakat", max_length=10, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Bo'lim")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField("O'zgartirilgan obyekt", max_length=255)
    timestamp = models.DateTimeField("Vaqt", auto_now_add=True)

    class Meta:
        verbose_name = "Harakat"
        verbose_name_plural = "Harakatlar jurnali"
        ordering = ['-timestamp']

    def __str__(self):
        user_name = self.user.username if self.user else "Tizim"
        return f"{user_name} | {self.get_action_display()} | {self.object_repr}"

# Log yaratish funksiyasi
def create_log(instance, action):
    user = get_current_user()
    # Agar foydalanuvchi tizimga kirmagan bo'lsa (masalan anonim), user None bo'ladi
    if user and not user.is_authenticated:
        user = None

    # Faqat AuditModel dan meros olganlarni log qilamiz
    if isinstance(instance, AuditModel):
        ActionLog.objects.create(
            user=user,
            action=action,
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id,
            object_repr=str(instance)
        )

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if issubclass(sender, AuditModel):
        action = 'create' if created else 'update'
        create_log(instance, action)

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if issubclass(sender, AuditModel):
        create_log(instance, 'delete')
# --- 0. AUDIT MODEL ---
class AuditModel(models.Model):
    created_at = models.DateTimeField("Yaratilgan vaqti", auto_now_add=True)
    updated_at = models.DateTimeField("Tahrirlangan vaqti", auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Kim yaratdi", related_name="created_%(class)s_set"
    )

    class Meta:
        abstract = True

# --- 1. KLINIKA STRUKTURASI ---
class Department(AuditModel):
    name = models.CharField("Bo'lim nomi", max_length=100, unique=True)
    description = models.TextField("Bo'lim haqida", blank=True)
    image = models.ImageField("Rasm", upload_to='departments/', blank=True)

    class Meta:
        verbose_name = "Bo'lim"
        verbose_name_plural = "Bo'limlar"

    def __str__(self):
        return self.name

class Service(AuditModel):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='services')
    name = models.CharField("Xizmat nomi", max_length=200)
    price = models.FloatField("Narxi")
    description = RichTextField("Tavsif", blank=True, null=True)
    image = models.ImageField("Rasm", upload_to='services/', blank=True, null=True)

    class Meta:
        verbose_name = "Xizmat"
        verbose_name_plural = "Xizmatlar"

    def __str__(self):
        return f"{self.name} - {self.price} so'm"

# --- 2. XODIMLAR TIZIMI ---
class Staff(AuditModel):
    ROLE_CHOICES = [('doctor', 'Shifokor'), ('reception', 'Reseption'), ('admin', 'Admin')]
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        related_name='staff_profile',
        null=True,
        blank=True,
        verbose_name="Tizimga kirish logini (Ixtiyoriy)"
    )
    role = models.CharField("Lavozimi", max_length=20, choices=ROLE_CHOICES)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField("F.I.Sh", max_length=200)
    photo = models.ImageField("Rasm", upload_to='staff/', default='default-staff.png')
    phone = models.CharField("Telefon", max_length=20, unique=True)

    class Meta:
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"

    def __str__(self):
        # Agar xodim shifokor bo'lsa va uning DoctorProfile (doctor_details) bo'lsa
        if self.role == 'doctor' and hasattr(self, 'doctor_details'):
            return f"{self.full_name} ({self.doctor_details.specialization})"

        # Agar shifokor bo'lmasa yoki profili hali yaratilmagan bo'lsa
        return f"{self.full_name} ({self.get_role_display()})"

class DoctorProfile(AuditModel):
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name='doctor_details', limit_choices_to={'role': 'doctor'})
    specialization = models.CharField("Mutaxassisligi", max_length=255)
    experience_years = models.PositiveIntegerField("Ish staji (yil)", default=0)
    slot_duration = models.IntegerField("Bemorga vaqt (min)", default=30)
    bio = models.TextField("Shifokor haqida", blank=True)

    class Meta:
        verbose_name = "Shifokor profili"
        verbose_name_plural = "Shifokorlar profillari"

    def __str__(self):
        return f"Dr. {self.staff.full_name}"

# --- 3. BEMORLAR BAZASI ---
class Patient(AuditModel):
    full_name = models.CharField("Bemor F.I.Sh", max_length=200)
    phone = models.CharField("Telefon raqami", max_length=20, unique=True)
    birth_date = models.DateField("Tug'ilgan sanasi", null=True, blank=True)
    gender = models.CharField("Jinsi", max_length=10, choices=[('male', 'Erkak'), ('female', 'Ayol')])
    address = models.CharField("Manzili", max_length=255, blank=True)

    class Meta:
        verbose_name = "Bemor"
        verbose_name_plural = "Bemorlar"

    def __str__(self):
        return self.full_name

# --- 4. NAVBATLAR TIZIMI (Ikki turdagi jadval) ---
class LabTest(AuditModel):
    name = models.CharField("Tahlil nomi", max_length=255)
    price = models.FloatField("Narxi")

    class Meta:
        verbose_name = "Laboratoriya tahlili"
        verbose_name_plural = "Laboratoriya tahlillari"
    def __str__(self):
        return self.name
# A. Faqat sayt orqali loginsiz olingan tezkor arizalar
class OnlineAppointment(AuditModel):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Bo'lim")
    doctor = models.ForeignKey(Staff, on_delete=models.CASCADE, limit_choices_to={'role': 'doctor'})
    patient_name = models.CharField("Bemor ismi", max_length=200)
    patient_phone = models.CharField("Telefon raqami", max_length=20)
    # service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True)
    date = models.DateField("Sana")
    time_slot = models.TimeField("Vaqt")
    notes = models.TextField("Qo'shimcha ma'lumot yoki shikoyat", blank=True, null=True)
    is_confirmed = models.BooleanField("Tasdiqlangan", default=False)

    class Meta:
        unique_together = ('doctor', 'date', 'time_slot')
        verbose_name = "Online Navbat"
        verbose_name_plural = "Online Navbatlar"

    def __str__(self):
        return f"{self.patient_name} (Online)"

    def __str__(self):
        return f"{self.patient_name} - {self.date} {self.time_slot}"


# B. Rasmiy ko'rik jadvali (Offline kelganlar va tasdiqlangan onlinelar uchun)
# class Appointment(AuditModel):
#     STATUS_CHOICES = [
#         ('waiting', 'Kutilmoqda'),
#         ('received', 'Qabul qilindi'),
#         ('paid', 'Toʻlov qilindi'),
#         ('completed', 'Yakunlandi'),
#         ('cancelled', 'Bekor qilindi'),
#     ]
#     doctor = models.ForeignKey(Staff, on_delete=models.CASCADE, limit_choices_to={'role': 'doctor'})
#     patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
#
#     # Ikki xil xizmat turi uchun ustunlar
#     service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tibbiy xizmat")
#     lab_test = models.ForeignKey(LabTest, on_delete=models.SET_NULL, null=True, blank=True,
#                                  verbose_name="Laboratoriya tahlili")
#
#     date = models.DateField("Sana")
#     time_slot = models.TimeField("Vaqt")
#     status = models.CharField("Holati", max_length=20, choices=STATUS_CHOICES, default='waiting')
#
#     def clean(self):
#         # Ikkala maydon ham bo'sh bo'lmasligini tekshiramiz
#         if not self.service and not self.lab_test:
#             raise ValidationError("Yo tibbiy xizmatni, yoki laboratoriya tahlilini tanlash shart!")
#
#         # Ikkalasi ham tanlanib qolishini oldini olamiz (ixtiyoriy, agar bitta navbatda faqat 1ta ish bo'lsa)
#         if self.service and self.lab_test:
#             raise ValidationError("Bitta navbatda ham xizmat, ham tahlilni tanlab bo'lmaydi. Alohida navbat oling.")
#
#     def save(self, *args, **kwargs):
#         self.full_clean()
#         super().save(*args, **kwargs)
#
#     class Meta:
#         unique_together = ('doctor', 'date', 'time_slot')
class Appointment(AuditModel):
    STATUS_CHOICES = [
        ('waiting', 'Kutilmoqda'),
        ('received', 'Qabul qilindi'),
        ('paid', 'Toʻlov qilindi'),
        ('completed', 'Yakunlandi'),
        ('cancelled', 'Bekor qilindi'),
    ]
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Bo'lim")
    doctor = models.ForeignKey(Staff, on_delete=models.CASCADE, limit_choices_to={'role': 'doctor'})

    # Bemor ma'lumotlari to'g'ridan-to'g'ri shu yerda
    patient_name = models.CharField("Bemorning ism-familiyasi", max_length=255)
    patient_phone = models.CharField("Telefon raqami", max_length=20)

    # 3 ta xizmat turi
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tibbiy xizmat")
    lab_test = models.ForeignKey(LabTest, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name="Laboratoriya tahlili")
    is_consultation = models.BooleanField("Shunchaki shifokor ko'rigi (Konsultatsiya)", default=False)

    date = models.DateField("Sana")
    time_slot = models.TimeField("Vaqt")
    status = models.CharField("Holati", max_length=20, choices=STATUS_CHOICES, default='waiting')

    def clean(self):
        if not self.service and not self.lab_test and not self.is_consultation:
            raise ValidationError(
                "Yo tibbiy xizmatni, yoki laboratoriya tahlilini tanlash yoki ko'rikni belgilash shart!")

        selected_count = sum([bool(self.service), bool(self.lab_test), self.is_consultation])
        if selected_count > 1:
            raise ValidationError("Bitta navbatda faqat bitta xizmat turini tanlash mumkin!")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('doctor', 'date', 'time_slot')

    def __str__(self):
        return f"{self.patient_name} | {self.date}"

# --- 5. TIBBIY XIZMATLAR VA MOLIYA ---
class MedicalRecord(AuditModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_history')
    doctor = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'doctor'})
    diagnosis = models.CharField("Tashxis", max_length=255)
    prescription = models.TextField("Retsept")

    class Meta:
        verbose_name = "Tibbiy karta"
        verbose_name_plural = "Tibbiy kartalar"



class LabReferral(AuditModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_referrals', verbose_name="Bemor")
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE, verbose_name="Tahlil turi")
    status = models.CharField(
        "Holati",
        max_length=20,
        choices=[('pending', 'Kutilmoqda'), ('completed', 'Tayyor')],
        default='pending'
    )
    result_text = models.TextField("Natija", blank=True)

    class Meta:
        verbose_name = "Laboratoriya yo'llanmasi"
        verbose_name_plural = "Laboratoriya yo'llanmalari"

    def __str__(self):
        return f"{self.patient.full_name} - {self.test.name}"

#
# class Payment(AuditModel):
#     # Navbatlar bilan bog'liqlik
#     appointment = models.OneToOneField(
#         'Appointment', on_delete=models.CASCADE,
#         related_name='payment', null=True, blank=True,
#         verbose_name="Klinika navbati"
#     )
#     online_appointment = models.OneToOneField(
#         'OnlineAppointment', on_delete=models.CASCADE,
#         related_name='payment', null=True, blank=True,
#         verbose_name="Online navbat"
#     )
#
#     # To'lov ma'lumotlari
#     amount = models.FloatField("To'lov summasi", default=0.0)
#     payment_type = models.CharField(
#         "To'lov turi",
#         max_length=10,
#         choices=[('cash', 'Naqd'), ('card', 'Karta'), ('online', 'Online')],
#         default='cash'
#     )
#     is_paid = models.BooleanField("To'langanlik holati", default=False)
#
#     def clean(self):
#         # 1. Kamida bitta navbat turi bo'lishi shart
#         if not self.appointment and not self.online_appointment:
#             raise ValidationError(
#                 "To'lovni biron bir navbatga bog'lash shart!"
#             )
#
#         # 2. Bir vaqtda ikkalasiga bog'lab bo'lmaydi
#         if self.appointment and self.online_appointment:
#             raise ValidationError(
#                 "To'lovni bir vaqtning o'zida ikkala navbat turiga bog'lab bo'lmaydi!"
#             )
#
#     def save(self, *args, **kwargs):
#         # To'lov summasini avtomatik hisoblash mantiqi
#         if self.appointment:
#             # Agar klinika navbati bo'lsa, xizmat yoki tahlil narxini olamiz
#             if self.appointment.service:
#                 self.amount = self.appointment.service.price
#             elif self.appointment.lab_test:
#                 self.amount = self.appointment.lab_test.price
#
#         # Online navbat uchun summa (agar kerak bo'lsa, bu yerga ham mantiq qo'shish mumkin)
#         # Hozircha online_appointment da narx yo'qligi uchun amount o'zgarmaydi
#
#         self.full_clean()
#         super().save(*args, **kwargs)
#
#     class Meta:
#         verbose_name = "To'lov"
#         verbose_name_plural = "To'lovlar"
#
#     def __str__(self):
#         status = "To'langan" if self.is_paid else "To'lanmagan"
#         return f"{self.amount} so'm - {status}"



class Payment(AuditModel):
    # Navbatlar bilan bog'liqlik
    appointment = models.OneToOneField(
        'Appointment', on_delete=models.SET_NULL,
        related_name='payment', null=True, blank=True,
        verbose_name="Klinika navbati"
    )
    online_appointment = models.OneToOneField(
        'OnlineAppointment', on_delete=models.SET_NULL,
        related_name='payment', null=True, blank=True,
        verbose_name="Online navbat"
    )

    # --- AVTOMATIK TO'LDIRILADIGAN MAYDONLAR ---
    service = models.ForeignKey(
        'Service', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Tibbiy xizmat"
    )
    lab_test = models.ForeignKey(
        'LabTest', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Laboratoriya tahlili"
    )
    is_consultation = models.BooleanField("Shifokor ko'rigi", default=False)

    # To'lov ma'lumotlari
    amount = models.FloatField("To'lov summasi", default=0.0)
    payment_type = models.CharField(
        "To'lov turi",
        max_length=10,
        choices=[('cash', 'Naqd'), ('card', 'Karta'), ('online', 'Online')],
        default='cash'
    )
    is_paid = models.BooleanField("To'langanlik holati", default=False)

    def clean(self):
        # Kamida bitta navbat turi bo'lishi shart
        if not self.appointment and not self.online_appointment:
            raise ValidationError("To'lovni biron bir navbatga bog'lash shart!")

        # Bir vaqtda ikkalasiga bog'lab bo'lmaydi
        if self.appointment and self.online_appointment:
            raise ValidationError("To'lovni bir vaqtning o'zida ikkala navbat turiga bog'lab bo'lmaydi!")

    def save(self, *args, **kwargs):
        # 1. Ma'lumotlarni sinxronizatsiya qilish
        if self.appointment:
            self.service = self.appointment.service
            self.lab_test = self.appointment.lab_test
            self.is_consultation = self.appointment.is_consultation
        # Online navbat bo'lsa ham xizmatlar tanlangan bo'lishi mumkinligini hisobga olamiz
        elif self.online_appointment:
            # Agar online navbatda xizmat maydonlari bo'lmasa, quyidagilarni qo'lda tanlash kerak bo'ladi
            pass

        # 2. NARXNI BELGILASH (Eng muhim qismi)
        # Qaysi navbat turi bo'lishidan qat'iy nazar, agar XIZMAT tanlangan bo'lsa,
        # birinchi navbatda o'sha xizmatning narxi (123 000) olinishi shart!

        if self.service:
            self.amount = self.service.price
        elif self.lab_test:
            self.amount = self.lab_test.price
        elif self.is_consultation:
            self.amount = 50000.0  # Ko'rik narxi
        elif self.online_appointment:
            # Faqat hech qanday xizmat tanlanmagan bo'lsagina online standart narxi olinadi
            self.amount = 60000.0
        else:
            self.amount = 0.0

        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"

    def __str__(self):
        status = "To'langan" if self.is_paid else "To'lanmagan"
        return f"{self.amount} so'm - {status}"

    def __str__(self):
        status = "To'langan" if self.is_paid else "To'lanmagan"
        return f"{self.amount} so'm - {status}"


class News(AuditModel):
    title = models.CharField("Sarlavha", max_length=255)
    slug = models.SlugField("Slug", unique=True, blank=True)
    summary = models.CharField("Qisqa mazmun", max_length=500, help_text="Asosiy sahifada ko'rinadigan qisqa matn")
    content = RichTextField("Maqola mazmuni")
    image = models.ImageField("Rasm", upload_to='news/', blank=True)
    views_count = models.PositiveIntegerField("Ko'rishlar soni", default=0)

    class Meta:
        verbose_name = "Yangilik"
        verbose_name_plural = "Yangiliklar"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=150, verbose_name="Ismi")
    email = models.EmailField(verbose_name="Email manzili")
    subject = models.CharField(max_length=255, verbose_name="Mavzu")
    message = models.TextField(verbose_name="Xabar matni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yuborilgan vaqti")
    is_read = models.BooleanField(default=False, verbose_name="O'qildimi?")

    def __str__(self):
        return f"{self.name} - {self.subject}"

    class Meta:
        verbose_name = "Bog'lanish xabari"
        verbose_name_plural = "Bog'lanish xabarlari"
        ordering = ['-created_at']

class StaffEducation(AuditModel): # AuditModel dan meros olindi
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='educations')
    graduated_year = models.CharField("Bitirgan yil", max_length=50)
    specialization = models.CharField("Mutaxassislik", max_length=255)
    university = models.CharField("Universitet", max_length=255)

    class Meta:
        verbose_name = "Xodim tahsili"
        verbose_name_plural = "Xodimlar tahsili"
class StaffExperience(AuditModel): # AuditModel dan meros olindi
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='experiences')
    years = models.CharField("Yillar", max_length=100)
    department = models.CharField("Bo'lim", max_length=255)
    position = models.CharField("Lavozim", max_length=255)
    hospital = models.CharField("Shifoxona", max_length=255)

    class Meta:
        verbose_name = "Xodim ish tajribasi"
        verbose_name_plural = "Xodimlar ish tajribalari"

class StaffSocialContact(AuditModel): # AuditModel dan meros olindi
    staff = models.OneToOneField(Staff, on_delete=models.CASCADE, related_name='social_contacts')
    email = models.EmailField("Email", blank=True, null=True)
    telegram = models.CharField("Telegram", max_length=100, blank=True, null=True)
    instagram = models.CharField("Instagram", max_length=100, blank=True, null=True)
    facebook = models.CharField("Facebook", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Xodim aloqa ma'lumoti"
        verbose_name_plural = "Xodimlar aloqa ma'lumotlari"
#
# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from django.contrib.contenttypes.models import ContentType
# from .middleware import get_current_user # Middleware dan foydalanamiz
#
# class ActionLog(models.Model):
#     ACTION_CHOICES = [
#         ('create', 'Yaratildi'),
#         ('update', 'Tahrirlandi'),
#         ('delete', "O'chirildi"),
#     ]
#
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Mas'ul xodim")
#     action = models.CharField("Harakat", max_length=10, choices=ACTION_CHOICES)
#     content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Bo'lim")
#     object_id = models.PositiveIntegerField()
#     content_object = GenericForeignKey('content_type', 'object_id')
#     object_repr = models.CharField("O'zgartirilgan obyekt", max_length=255)
#     timestamp = models.DateTimeField("Vaqt", auto_now_add=True)
#
#     class Meta:
#         verbose_name = "Harakat"
#         verbose_name_plural = "Harakatlar jurnali"
#         ordering = ['-timestamp']
#
#     def __str__(self):
#         user_name = self.user.username if self.user else "Tizim"
#         return f"{user_name} | {self.get_action_display()} | {self.object_repr}"
#
# # Log yaratish funksiyasi
# def create_log(instance, action):
#     user = get_current_user()
#     # Agar foydalanuvchi tizimga kirmagan bo'lsa (masalan anonim), user None bo'ladi
#     if user and not user.is_authenticated:
#         user = None
#
#     # Faqat AuditModel dan meros olganlarni log qilamiz
#     if isinstance(instance, AuditModel):
#         ActionLog.objects.create(
#             user=user,
#             action=action,
#             content_type=ContentType.objects.get_for_model(instance),
#             object_id=instance.id,
#             object_repr=str(instance)
#         )
#
# @receiver(post_save)
# def log_save(sender, instance, created, **kwargs):
#     if issubclass(sender, AuditModel):
#         action = 'create' if created else 'update'
#         create_log(instance, action)
#
# @receiver(post_delete)
# def log_delete(sender, instance, **kwargs):
#     if issubclass(sender, AuditModel):
#         create_log(instance, 'delete')
#
