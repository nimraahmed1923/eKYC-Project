from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator
import csv
import sqlite3
import re

# ---------- AUTH ----------

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


# ---------- VALIDATION HELPERS ----------

def is_aadhaar(val):
    return bool(re.fullmatch(r'\d{12}', val or '')) and val != '000000000000'

def is_pan(val):
    return bool(re.fullmatch(r'[A-Z]{5}[0-9]{4}[A-Z]', val or '')) and val != 'AAAAA0000A'

def is_passport(val):
    val = (val or '').strip()
    return (
        val.upper() != 'A0000000' and
        bool(re.fullmatch(r'[A-Z0-9]{5,12}', val))
    )


# ---------- DB HELPER ----------

def fetch_ekyc_from_gui():
    conn = sqlite3.connect('ekyc_database.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Add fingerprint_score column fallback if it doesn't exist
    try:
        cursor.execute("SELECT * FROM ekyc_data ORDER BY timestamp DESC")
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE ekyc_data ADD COLUMN fingerprint_score REAL")
        conn.commit()
        cursor.execute("SELECT * FROM ekyc_data ORDER BY timestamp DESC")
        rows = cursor.fetchall()

    conn.close()
    return [dict(row) for row in rows]


# ---------- DASHBOARD ----------

@login_required
def dashboard_view(request):
    query = request.GET.get('q', '').strip().lower()
    page_number = request.GET.get('page', 1)
    all_entries = fetch_ekyc_from_gui()

    if query:
        all_entries = [
            e for e in all_entries if
            query in (e['name'] or '').lower() or
            query in (e['aadhaar_number'] or '').lower() or
            query in (e['pan_number'] or '').lower() or
            query in (e['passport_number'] or '').lower()
        ]

    def is_unknown(entry):
        return (entry.get('name') or '').strip().lower() == 'unknown name'

    def fingerprint_match(entry):
        score = entry.get('fingerprint_score')
        return score is not None and score >= 85

    total_records = len(all_entries)
    aadhaar_count = sum(1 for e in all_entries if is_aadhaar(e.get('aadhaar_number')))
    pan_count = sum(1 for e in all_entries if is_pan(e.get('pan_number')))
    passport_count = sum(1 for e in all_entries if is_passport(e.get('passport_number')))
    fingerprint_match_count = sum(1 for e in all_entries if fingerprint_match(e))

    # Fraud logic based on "Unknown Name"
    high_risk_count = sum(1 for e in all_entries if is_unknown(e))
    medium_risk_count = 0
    low_risk_count = total_records - high_risk_count
    average_fraud_score = round((high_risk_count / total_records) * 100, 2) if total_records > 0 else 0

    # Pagination
    paginator = Paginator(all_entries, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'total_records': total_records,
        'aadhaar_count': aadhaar_count,
        'pan_count': pan_count,
        'passport_count': passport_count,
        'high_risk_count': high_risk_count,
        'medium_risk_count': medium_risk_count,
        'low_risk_count': low_risk_count,
        'average_fraud_score': average_fraud_score,
        'fingerprint_match_count': fingerprint_match_count,
        'recent_entries': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'dashboard_v2/dashboard.html', context)


# ---------- DELETE ----------

@login_required
def delete_entry(request, entry_id):
    conn = sqlite3.connect('ekyc_database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ekyc_data WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    messages.success(request, "Entry deleted successfully.")
    return redirect('dashboard')


# ---------- VIEW ----------

@login_required
def view_records_view(request):
    records = fetch_ekyc_from_gui()
    return render(request, 'dashboard_v2/view_records.html', {'records': records})


# ---------- EXPORT ----------

@login_required
def export_data_view(request):
    entries = fetch_ekyc_from_gui()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ekyc_data_export.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Name', 'Document Type', 'Aadhaar Number', 'PAN Number',
        'Passport Number', 'Status', 'Fraud Score', 'Fingerprint Score', 'Timestamp'
    ])
    for e in entries:
        writer.writerow([
            e.get('id'), e.get('name'), e.get('document_type'),
            e.get('aadhaar_number'), e.get('pan_number'),
            e.get('passport_number'), e.get('status'),
            'High' if (e.get('name') or '').lower() == 'unknown name' else 'Low',
            e.get('fingerprint_score') or 'N/A',
            e.get('timestamp')
        ])
    return response


# ---------- FILTERED VIEWS ----------

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


def home_view(request):
    return redirect('dashboard')
