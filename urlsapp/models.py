from django.db import models
import string
import random
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import requests
from django.utils.html import strip_tags
from bs4 import BeautifulSoup

class URL(models.Model):
    original_url = models.URLField(unique=True)
    short_code = models.CharField(max_length=6, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    click_count = models.IntegerField(default=0)
    title = models.CharField(max_length=255, blank=True)
    
    def get_short_url(self):
        return f"http://auvt.cc/{self.short_code}"
    
    def save(self, *args, **kwargs):
        if not self.short_code:
            self.short_code = self.generate_short_code()
        if not self.title:
            self.title = self.fetch_url_title()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_short_code():
        characters = string.ascii_letters + string.digits
        reserved_words = ['admin', 'static', 'media']
        
        while True:
            code = ''.join(random.choice(characters) for _ in range(6))
            if code not in reserved_words and not URL.objects.filter(short_code=code).exists():
                return code
            
    def clean(self):
        validate = URLValidator()
        try:
            validate(self.original_url)
        except ValidationError:
            raise ValidationError({'original_url': 'Invalid URL format'})
    
    def fetch_url_title(self):
        try:
            response = requests.get(self.original_url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title')
                if title:
                    return strip_tags(title.text)
        except:
            pass
        return ""