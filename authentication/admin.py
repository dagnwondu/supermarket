from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import CustomUser, Company
# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Assigned Group'


    # Define which fields to show in the list display
    list_display = (
        'username','company', 'email', 'first_name', 'last_name', 'middle_name', 'user_type',
        'get_groups', 'is_staff', 'is_active'
    )

    # Define the form fields for the user edit page
    fieldsets = (
        *UserAdmin.fieldsets,  # Include the default UserAdmin fieldsets
        ('Custom Info', {
            'fields': ('user_type', 'middle_name' ,'company',)  # Add custom fields here
        }),
    )

    # Define the form fields for the user creation page
    add_fieldsets = (
        *UserAdmin.add_fieldsets,  # Include the default UserAdmin add_fieldsets
        ('Custom Info', {
            'fields': ('user_type', 'middle_name')  # Add custom fields here
        }),
    )

    # Add a horizontal filter for groups and permissions
    filter_horizontal = ('groups', 'user_permissions')

    # To ensure permissions show up when editing users
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

    # Make sure permissions and groups show up on the User model's edit page
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj or obj.is_superuser:
            return fieldsets
        return fieldsets  # Allow permission field only for superusers



@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'address')
    ordering = ('company_name',)
    search_fields = ('company_name', 'address')
