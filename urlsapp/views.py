from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import URL
import json
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.conf import settings
from django.contrib.auth.models import User

@staff_member_required
def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        request.session.set_expiry(365 * 24 * 60 * 60)  # 1 year
        request.session['admin_logged_in'] = True
        return redirect(settings.LOGIN_REDIRECT_URL)
    return redirect('/admin/')

def index(request):
    urls = URL.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'urls': urls})

@login_required
def shorten(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        original_url = data.get('original_url')
        
        if not original_url:
            return JsonResponse({'error': 'URL is required'}, status=400)
            
        try:
            # Check if URL already exists
            existing_url = URL.objects.filter(original_url=original_url).first()
            if existing_url:
                return JsonResponse({
                    'short_url': existing_url.get_short_url(),
                    'exists': True
                })
                
            # Create new URL
            url = URL(original_url=original_url)
            url.full_clean()
            url.save()
            return JsonResponse({
                'short_url': url.get_short_url(),
                'exists': False
            })
            
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    # GET request
    urls = URL.objects.all().order_by('-created_at')
    return render(request, 'shorten.html', {'urls': urls})

def redirect_view(request, short_code):
    try:
        url = URL.objects.get(short_code=short_code)
        url.click_count += 1
        url.save()
        return redirect(url.original_url)
    except URL.DoesNotExist:
        return HttpResponseRedirect('/')
    
def not_found(request):
    urls = URL.objects.all().order_by('-created_at')
    query = request.GET.get('q', '')
    context = {
        'urls': urls,
        'query': query
    }
    return render(request, 'not_found.html', context)

def search(request):
    query = request.GET.get('q', '')
    if query:
        urls = URL.objects.filter(original_url__icontains=query) | URL.objects.filter(title__icontains=query)
    else:
        urls = URL.objects.all().order_by('-created_at')
    
    data = {
        'urls': [
            {
                'original_url': url.original_url,
                'get_short_url': url.get_short_url(),
                'title': url.title,
                'click_count': url.click_count,
                'created_at': url.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for url in urls
        ]
    }
    return JsonResponse(data)