from django.db import models
from django.contrib.auth.models import AbstractUser

class Company(models.Model):
    company_name = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    phone_number_2 = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    mobile_2 = models.CharField(max_length=100, null=True, blank=True)
    post_address = models.CharField(max_length=100, null=True, blank=True)
    motto = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.company_name

class CustomUser(AbstractUser):
    class UserType(models.TextChoices):
        ADMIN = "admin", "Admin"
        CASHIER = "cashier", "Cashier"

    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.CASHIER
    )
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def get_full_name(self):
        return f"{self.first_name} {self.middle_name}"


