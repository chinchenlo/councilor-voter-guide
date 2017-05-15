# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Sum, Q
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .models import Candidates, Terms, Intent
from .forms import IntentForm


def districts(request, election_year, county):
    districts = Terms.objects.filter(election_year=election_year, county=county).values('constituency', 'district')\
                                  .annotate(candidates=Count('id'))\
                                  .order_by('constituency')
    return render(request, 'candidates/districts.html', {'election_year': election_year, 'county': county, 'districts': districts})

def district(request, election_year, county, constituency):
    candidates = Terms.objects.filter(election_year=election_year, county=county, constituency=constituency).order_by('-votes')
    return render(request, 'candidates/district.html', {'election_year': election_year, 'county': county, 'district': candidates[0].district, 'candidates': candidates})

def intent_home(request):
    if request.user.is_authenticated:
        return redirect(reverse('candidates:intent_upsert'))
    return render(request, 'candidates/intent_home.html', )

def intent_upsert(request):
    instances = Intent.objects.filter(user=request.user, election_year=2018)
    instance = instances[0] if instances else None
    if not request.user.is_authenticated:
        return redirect(reverse('candidates:intent_home'))
    if request.method == 'GET':
        form = IntentForm(instance=instance)
    if request.method == 'POST':
        form = IntentForm(request.POST, instance=instance)
        if form.is_valid():
            intent = form.save(commit=False)
            intent.user = request.user
            intent.save()
    return render(request, 'candidates/intent_upsert.html', {'form': form})

def intent_detail(request, intent_id):
    intent = get_object_or_404(Intent.objects, uid=intent_id)
    return render(request, 'candidates/intent_detail.html', {'intent': intent})

def pc(request, candidate_id, election_year):
    candidate = get_object_or_404(Terms.objects, election_year=election_year, candidate_id=candidate_id)
    return render(request, 'candidates/pc.html', {'candidate': candidate})
