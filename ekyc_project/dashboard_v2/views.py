from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q, Avg
import csv
import sqlite3
from datetime import datetime
import re

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

# ---------- DASHBOARD VIEW USING GUI DB ----------

def fetch_ekyc_from_gui():
    conn = sqlite3.connect('ekyc_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ekyc_data ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@login_required
def dashboard_view(request):
    query = request.GET.get('q', '').strip().lower()

    all_entries = fetch_ekyc_from_gui()

    # Apply search filter manually
    if query:
        all_entries = [
            e for e in all_entries if
            query in (e['name'] or '').lower() or
            query in (e['aadhaar_number'] or '').lower() or
            query in (e['pan_number'] or '').lower() or
            query in (e['passport_number'] or '').lower()
        ]

    total_records = len(all_entries)
    aadhaar_count = sum(1 for e in all_entries if is_aadhaar(e.get('aadhaar_number')))
    pan_count = sum(1 for e in all_entries if is_pan(e.get('pan_number')))
    passport_count = sum(1 for e in all_entries if is_passport(e.get('passport_number')))

    # Risk counts (using hardcoded logic based on status/fraud_score if available)
    high_risk_count = sum(1 for e in all_entries if (e.get('fraud_score') or 0) >= 0.8)
    medium_risk_count = sum(1 for e in all_entries if 0.5 <= (e.get('fraud_score') or 0) < 0.8)
    low_risk_count = sum(1 for e in all_entries if (e.get('fraud_score') or 0) < 0.5)
    scores = [e.get('fraud_score') for e in all_entries if e.get('fraud_score') is not None]
    average_fraud_score = round(sum(scores) / len(scores) * 100, 2) if scores else 0

    context = {
        'recent_entries': all_entries,  # Now shows ALL entries from GUI DB
        'query': query,
        'total_records': total_records,
        'aadhaar_count': aadhaar_count,
        'pan_count': pan_count,
        'passport_count': passport_count,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'average_fraud_score': average_fraud_score,
    }
    return render(request, 'dashboard_v2/dashboard.html', context)


# ---------- ENTRY MANAGEMENT ----------

@login_required
def delete_entry(request, entry_id):
    conn = sqlite3.connect('ekyc_database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ekyc_data WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    messages.success(request, "Entry deleted successfully.")
    return redirect('dashboard')


@login_required
def view_records_view(request):
    records = fetch_ekyc_from_gui()
    return render(request, 'dashboard_v2/view_records.html', {'records': records})


# ---------- EXPORT DATA ----------

@login_required
def export_data_view(request):
    entries = fetch_ekyc_from_gui()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ekyc_data_export.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Name', 'Document Type', 'Aadhaar Number', 'PAN Number',
        'Passport Number', 'Status', 'Fraud Score', 'Timestamp'
    ])
    for e in entries:
        writer.writerow([
            e.get('id'), e.get('name'), e.get('document_type'),
            e.get('aadhaar_number'), e.get('pan_number'),
            e.get('passport_number'), e.get('status'),
            e.get('fraud_score'), e.get('timestamp')
        ])
    return response


# ---------- DOCUMENT FILTERED LISTS ----------

@login_required
def aadhaar_list(request):
    entries = [e for e in fetch_ekyc_from_gui() if is_aadhaar(e.get('aadhaar_number'))]
    query = request.GET.get('q', '').lower()
    if query:
        entries = [e for e in entries if query in (e.get('name') or '').lower() or query in (e.get('aadhaar_number') or '').lower()]
    return render(request, 'dashboard_v2/aadhaar_list.html', {'entries': entries})


@login_required
def pan_list(request):
    entries = [e for e in fetch_ekyc_from_gui() if is_pan(e.get('pan_number'))]
    query = request.GET.get('q', '').lower()
    if query:
        entries = [e for e in entries if query in (e.get('name') or '').lower() or query in (e.get('pan_number') or '').lower()]
    return render(request, 'dashboard_v2/pan_list.html', {'entries': entries})


@login_required
def passport_list(request):
    entries = [e for e in fetch_ekyc_from_gui() if is_passport(e.get('passport_number'))]
    query = request.GET.get('q', '').lower()
    if query:
        entries = [e for e in entries if query in (e.get('name') or '').lower() or query in (e.get('passport_number') or '').lower()]
    return render(request, 'dashboard_v2/passport_list.html', {'entries': entries})


# ---------- HOME ----------

def home_view(request):
    return redirect('dashboard')
