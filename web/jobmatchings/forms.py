from django import forms
from jobapplications.models import JobApplication, Ranking

class EmployerRankingForm(forms.Form):

    def __init__(self, *args, **kwargs):
        jobId = kwargs.pop('jobId', -1)
        self.jobId = jobId
        super().__init__(*args, **kwargs)
        self.rankingFields = []
        self.rankingFieldsNames = {}



        RANK_CHOICES = ( 
            (1, "1st"), 
            (2, "2"), 
            (3, "3"), 
            (4, "4"), 
            (5, "5"), 
            (6, "6"), 
            (7, "7"), 
            (8, "8"), 
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (999, "Reject"),
            (1000, "Not yet ranked"),
        )
        
        for rank in Ranking.objects.filter(job__id=jobId).all():
            field_name = '%s' % (rank.id,)
            rankingDict = {}

            currentRank = int(rank.employerRank)

            if rank.is_ranking_open_for_employer:
                self.fields[field_name] = forms.ChoiceField(
                    choices = RANK_CHOICES,
                    initial=currentRank,
                    widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Category'})
                )
            else:
                if currentRank == 999:
                    RANK_CHOICES = [(currentRank, "Reject")]
                elif currentRank == 1000:
                    RANK_CHOICES = [(currentRank, "Not yet ranked")]
                else:
                    RANK_CHOICES = [(currentRank, str(currentRank))]

                self.fields[field_name] = forms.ChoiceField(
                    choices = RANK_CHOICES,
                    initial=currentRank,
                    widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Category'})
                )

            rankingDict['rankField'] = self[field_name]

            rankingDict['rank'] = rank
            self.rankingFields.append(rankingDict)
            self.rankingFieldsNames[rank] = 'rank' + field_name



    def get_ranking_fields(self):
        return self.rankingFields



    def clean(self):
        cleaned_data = super().clean()

        self.cleaned_data = cleaned_data

    def save(self, pk, user):

        for rank in  Ranking.objects.filter(job__id=self.jobId).all():
            rank.update(employerRank = int(self.cleaned_data.get(self.rankingFieldsNames[rank])))

class CandidateRankingForm(forms.Form):

    def __init__(self, *args, **kwargs):
        candidateId = kwargs.pop('candidateId', -1)
        self.candidateId = candidateId
        super().__init__(*args, **kwargs)
        self.rankingFields = []
        self.rankingFieldsNames = {}

        RANK_CHOICES = ( 
            (1, "1st"), 
            (2, "2"), 
            (3, "3"), 
            (4, "4"), 
            (5, "5"), 
            (6, "6"), 
            (7, "7"), 
            (8, "8"), 
            (9, "9"),
            (10, "10"),
            (11, "11"),
            (12, "12"),
            (13, "13"),
            (14, "14"),
            (15, "15"),
            (999, "Reject"),
            (1000, "Not yet ranked"),
        )
        
        for rank in Ranking.objects.filter(candidate__id=candidateId, is_closed=False).all():
            field_name = '%s' % (rank.id,)
            rankingDict = {}

            currentRank = int(rank.candidateRank)

            if rank.is_ranking_open_for_candidate:
                self.fields[field_name] = forms.ChoiceField(
                    choices = RANK_CHOICES,
                    initial=currentRank,
                    widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Category'})
                )
                if rank.employerRank == 1:
                    rankingDict['employerRank'] = rank.employerRank
                elif rank.employerRank == 1000 or rank.employerRank == 999:
                    rankingDict['employerRank'] = "Not selected"
                else:
                    rankingDict['employerRank'] = "Ranked"
            else:

                if currentRank == 999:
                    RANK_CHOICES = [(currentRank, "Reject")]
                elif currentRank == 1000:
                    RANK_CHOICES = [(currentRank, "Not yet ranked")]
                else:
                    RANK_CHOICES = [(currentRank, str(currentRank))]

                rankingDict['employerRank'] = "Ranking not yet opened"

                self.fields[field_name] = forms.ChoiceField(
                    choices = RANK_CHOICES,
                    initial=currentRank,
                    widget=forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select Category'})
                )

            rankingDict['rankField'] = self[field_name]
            rankingDict['rank'] = rank
            self.rankingFields.append(rankingDict)
            self.rankingFieldsNames[rank] = 'rank' + field_name



    def get_ranking_fields(self):
        return self.rankingFields

    def clean(self):
        cleaned_data = super().clean()

        self.cleaned_data = cleaned_data

    def save(self, pk, user):

        for rank in  Ranking.objects.filter(job__id=self.jobId).all():
            rank.update(employerRank = int(self.cleaned_data.get(self.rankingFieldsNames[rank])))
