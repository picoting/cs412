from django import forms
from .models import Voter

from .constants import PARTY_AFFILIATION_MAP

class VoterFilterForm(forms.Form):
    PARTY_CHOICES = [('all', 'All')] + [(party, party) for party in PARTY_AFFILIATION_MAP.values()]
    VOTER_SCORE_CHOICES = [('all', 'All')] + [(score, score) for score in Voter.objects.values_list('voter_score', flat=True).distinct()]
    YEAR_CHOICES = [(year, year) for year in range(1900, 2025)]

    party_affiliation = forms.MultipleChoiceField(
        choices=PARTY_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    min_dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2025)), required=False)
    max_dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2025)), required=False)
    voter_score = forms.ChoiceField(choices=VOTER_SCORE_CHOICES, required=False)
    v20state = forms.BooleanField(required=False)
    v21town = forms.BooleanField(required=False)
    v21primary = forms.BooleanField(required=False)
    v22general = forms.BooleanField(required=False)
    v23town = forms.BooleanField(required=False)

    def clean_party_affiliation(self):
        data = self.cleaned_data.get('party_affiliation')
        if 'all' in data:
            return [choice[0] for choice in [('all', 'All')] + [(party, party) for party in PARTY_AFFILIATION_MAP.values()]]
        return data
