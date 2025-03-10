from django.contrib import admin
from django.contrib import messages
from .models import URL

@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ('title', 'original_url', 'short_code', 'get_short_url', 'created_at')
    readonly_fields = ('short_code',)
    
    def save_model(self, request, obj, form, change):
        if URL.objects.filter(original_url=obj.original_url).exists():
            existing = URL.objects.get(original_url=obj.original_url)
            messages.info(request, f"URL already exists. Short URL: {existing.get_short_url()}")
            return
        super().save_model(request, obj, form, change)