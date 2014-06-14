from django import forms


class FixForm(forms.Form):
    git_commit_id = forms.URLField(label='Commit URL In GitHub', max_length=128, required=True, error_messages={'required': 'A commit URL from github is required.'})
    message = forms.CharField( widget=forms.Textarea(attrs={'rows': 4 }),
                               label='Describe Your Fix',
                               max_length=500,
                               required=True,
                               error_messages={'required': 'Please provide an brief overview of the fix.'} )
    min_amount = forms.FloatField(label='Fix Payment Request in BTC',
                                  required=True,
                                  error_messages={'required': 'Please enter an amount in BTC you would like to receive.'})
    issue_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    type = forms.ChoiceField(widget = forms.Select(),
                     choices = ([('pull_request','Pull Request'),
                                 ('committer','Repo Comitter'), ]),
                     initial='committer', required = True, label='Commit Type')

