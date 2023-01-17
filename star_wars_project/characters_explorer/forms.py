from django import forms

class ValueCountForm(forms.Form):
    """
    Form representing columns to be used to count values combinations
    """    
    name = forms.BooleanField(required=False)
    height = forms.BooleanField(required=False)
    mass = forms.BooleanField(required=False)
    hair_color = forms.BooleanField(required=False)
    skin_color = forms.BooleanField(required=False)
    eye_color = forms.BooleanField(required=False)
    birth_year = forms.BooleanField(required=False)
    gender = forms.BooleanField(required=False)
    homeworld = forms.BooleanField(required=False)
    date = forms.BooleanField(required=False)