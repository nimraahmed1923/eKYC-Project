from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg
from django.http import HttpResponse
import csv
from datetime import datetime
import re

from dashboard_v2.models import EkycData

# ---------- AUTHENTICATION VIEWS ----------

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'dashboard_v2/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ---------- PATTERN HELPERS ----------

def is_aadhaar(val):
    return bool(re.fullmatch(r'\d{12}', val or '')) and val != '000000000000'

def is_pan(val):
    return bool(re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', val or '')) and val != 'AAAAA0000A'

def is_passport(val):
    val = (val or '').strip()
    return (
        val != 'A0000000' and (
            bool(re.fullmatch(r'[A-Z][0-9]{7}', val)) or
            bool(re.fullmatch(r'\d{8}', val))
        )
    )

# ---------- DASHBOARD VIEW ----------

@login_required
def dashboard_view(request):
    query = request.GET.get('q', '').strip()
    document_type = request.GET.get('doc_type', '')
    status_filter = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    entries = EkycData.objects.all()

    if query:
        entries = entries.filter(
            Q(name__icontains=query) |
            Q(aadhaar_number__icontains=query) |
            Q(pan_number__icontains=query) |
            Q(passport_number__icontains=query)
        )

    if document_type:
        entries = entries.filter(document_type__iexact=document_type)

    if status_filter:
        entries = entries.filter(status__iexact=status_filter)

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            entries = entries.filter(timestamp__gte=start_dt)
        except ValueError:
            messages.warning(request, "Invalid start date format. Use YYYY-MM-DD.")

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            entries = entries.filter(timestamp__lte=end_dt)
        except ValueError:
            messages.warning(request, "Invalid end date format. Use YYYY-MM-DD.")

    recent_entries = entries.order_by('-timestamp')[:100]

    all_entries = EkycData.objects.all()
    total_records = all_entries.count()
    aadhaar_count = sum(1 for e in all_entries if is_aadhaar(e.aadhaar_number))
    pan_count = sum(1 for e in all_entries if is_pan(e.pan_number))
    passport_count = sum(1 for e in all_entries if is_passport(e.passport_number))

    high_risk_count = all_entries.filter(fraud_score__gte=0.8).count()
    medium_risk_count = all_entries.filter(fraud_score__gte=0.5, fraud_score__lt=0.8).count()
    low_risk_count = all_entries.filter(fraud_score__lt=0.5).count()
    average_fraud_score = all_entries.aggregate(avg=Avg('fraud_score'))['avg'] or 0

    context = {
        'query': query,
        'document_type': document_type,
        'status_filter': status_filter,
        'start_date': start_date,
        'end_date': end_date,
        'recent_entries': recent_entries,
        'total_records': total_records,
        'aadhaar_count': aadhaar_count,
        'pan_count': pan_count,
        'passport_count': passport_count,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'average_fraud_score': round(average_fraud_score * 100, 2),
    }

    return render(request, 'dashboard_v2/dashboard.html', context)


# ---------- ENTRY MANAGEMENT ----------

@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(EkycData, id=entry_id)
    entry.delete()
    messages.success(request, "Entry deleted successfully.")
    return redirect('dashboard')


@login_required
def view_records_view(request):
    records = EkycData.objects.all().order_by('-timestamp')
    return render(request, 'dashboard_v2/view_records.html', {'records': records})


# ---------- EXPORT DATA ----------

@login_required
def export_data_view(request):
    query = request.GET.get('q', '').strip()
    document_type = request.GET.get('doc_type', '')
    status_filter = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    entries = EkycData.objects.all()

    if query:
        entries = entries.filter(
            Q(name__icontains=query) |
            Q(aadhaar_number__icontains=query) |
            Q(pan_number__icontains=query) |
            Q(passport_number__icontains=query)
        )

    if document_type:
        entries = entries.filter(document_type__iexact=document_type)

    if status_filter:
        entries = entries.filter(status__iexact=status_filter)

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            entries = entries.filter(timestamp__gte=start_dt)
        except ValueError:
            messages.warning(request, "Invalid start date format. Use YYYY-MM-DD.")

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')
            entries = entries.filter(timestamp__lte=end_dt)
        except ValueError:
            messages.warning(request, "Invalid end date format. Use YYYY-MM-DD.")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ekyc_data_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Document Type', 'Aadhaar Number', 'PAN Number', 'Passport Number', 'Status', 'Fraud Score', 'Timestamp'])

    for row in entries.values_list('id', 'name', 'document_type', 'aadhaar_number', 'pan_number', 'passport_number', 'status', 'fraud_score', 'timestamp'):
        writer.writerow(row)

    return response


# ---------- DOCUMENT FILTERED LISTS ----------

@login_required
def aadhaar_list(request):
    search_query = request.GET.get('q', '').strip()
    entries = EkycData.objects.all()
    entries = [e for e in entries if is_aadhaar(e.aadhaar_number)]

    if search_query:
        entries = [e for e in entries if search_query.lower() in e.name.lower() or search_query in (e.aadhaar_number or '')]

    return render(request, 'dashboard_v2/aadhaar_list.html', {'entries': entries})


@login_required
def pan_list(request):
    search_query = request.GET.get('q', '').strip()
    entries = EkycData.objects.all()
    entries = [e for e in entries if is_pan(e.pan_number)]

    if search_query:
        entries = [e for e in entries if search_query.lower() in e.name.lower() or search_query in (e.pan_number or '')]

    return render(request, 'dashboard_v2/pan_list.html', {'entries': entries})


@login_required
def passport_list(request):
    search_query = request.GET.get('q', '').strip()
    entries = EkycData.objects.all()
    entries = [e for e in entries if is_passport(e.passport_number)]

    if search_query:
        entries = [e for e in entries if search_query.lower() in e.name.lower() or search_query in (e.passport_number or '')]

    return render(request, 'dashboard_v2/passport_list.html', {'entries': entries})


# ---------- HOME ----------

def home_view(request):
    return redirect('dashboard')