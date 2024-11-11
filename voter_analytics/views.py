from django.shortcuts import render

from django.views.generic import ListView, DetailView
from .models import Voter
from .forms import VoterFilterForm

import plotly.express as px
from django.db.models import Count

class VoterListView(ListView):
    model = Voter
    template_name = 'voter_analytics/voter_list.html'
    context_object_name = 'voters'
    paginate_by = 100

    def get_queryset(self):
        queryset = super().get_queryset()
        form = VoterFilterForm(self.request.GET)
        if form.is_valid():
            if form.cleaned_data['party_affiliation']:
                queryset = queryset.filter(party_affiliation=form.cleaned_data['party_affiliation'])
            min_dob = self.request.GET.get('min_dob')
            if min_dob:
                queryset = queryset.filter(date_of_birth__gte=form.cleaned_data['min_dob'])
            if form.cleaned_data['max_dob']:
                queryset = queryset.filter(date_of_birth__lte=form.cleaned_data['max_dob'])
            if form.cleaned_data['voter_score']:
                queryset = queryset.filter(voter_score=form.cleaned_data['voter_score'])
            if form.cleaned_data['v20state']:
                queryset = queryset.filter(v20state=True)
            if form.cleaned_data['v21town']:
                queryset = queryset.filter(v21town=True)
            if form.cleaned_data['v21primary']:
                queryset = queryset.filter(v21primary=True)
            if form.cleaned_data['v22general']:
                queryset = queryset.filter(v22general=True)
            if form.cleaned_data['v23town']:
                queryset = queryset.filter(v23town=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = VoterFilterForm(self.request.GET)
        return context
    
class VoterDetailView(DetailView):
    model = Voter
    template_name = 'voter_analytics/voter_detail.html'
    context_object_name = 'voter'

class VoterGraphView(ListView):
    model = Voter
    template_name = 'voter_analytics/graphs.html'
    context_object_name = 'voters'

    def get_queryset(self):
        queryset = super().get_queryset()
        form = VoterFilterForm(self.request.GET)
        if form.is_valid():
            party_affiliations = form.cleaned_data.get('party_affiliation')
            if party_affiliations and 'all' not in party_affiliations:
                queryset = queryset.filter(party_affiliation__in=party_affiliations)

            voter_score = form.cleaned_data.get('voter_score')
            if voter_score and voter_score != 'all':
                queryset = queryset.filter(voter_score=voter_score)
            if form.cleaned_data['min_dob']:
                queryset = queryset.filter(date_of_birth__year__gte=form.cleaned_data['min_dob'])
            if form.cleaned_data['max_dob']:
                queryset = queryset.filter(date_of_birth__year__lte=form.cleaned_data['max_dob'])
            #if form.cleaned_data['voter_score']:
                #queryset = queryset.filter(voter_score=form.cleaned_data['voter_score'])
            for election in ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']:
                if form.cleaned_data[election]:
                    queryset = queryset.filter(**{election: True})
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        voters = self.get_queryset()

        birth_years = voters.values_list('date_of_birth__year', flat=True)
        fig_birth_year = px.histogram(
            x=birth_years,
            nbins=100,
            labels={'x': 'Year of Birth', 'y': 'Count'},
            title='Distribution of Voters by Year of Birth'
        )
        context['graph_birth_year'] = fig_birth_year.to_html(full_html=False)

        party_counts = voters.values('party_affiliation').annotate(count=Count('id'))
        fig_party = px.pie(
            names=[entry['party_affiliation'] for entry in party_counts],
            values=[entry['count'] for entry in party_counts],
            title='Distribution of Voters by Party Affiliation'
        )
        context['graph_party'] = fig_party.to_html(full_html=False)

        election_fields = ['v20state', 'v21town', 'v21primary', 'v22general', 'v23town']
        election_labels = {
            'v20state': '2020 State Election',
            'v21town': '2021 Town Election',
            'v21primary': '2021 Primary Election',
            'v22general': '2022 General Election',
            'v23town': '2023 Town Election'
        }
        election_data = []
        for field in election_fields:
            count = voters.filter(**{field: True}).count()
            election_data.append({'election': election_labels[field], 'count': count})
        fig_election = px.bar(
            x=[entry['election'] for entry in election_data],
            y=[entry['count'] for entry in election_data],
            labels={'x': 'Election', 'y': 'Number of Participants'},
            title='Voter Participation in Elections'
        )
        context['graph_election'] = fig_election.to_html(full_html=False)

        context['form'] = VoterFilterForm(self.request.GET)

        return context