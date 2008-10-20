# Copyright 2008 Gabriel Sean Farrell
#
# This file is part of Helios.
# 
# Helios is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Helios is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Helios.  If not, see <http://www.gnu.org/licenses/>.

from django import forms
from django.forms.formsets import formset_factory

class HistoryForm(forms.Form):
    message = forms.CharField(label='')

class PersonForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    url = forms.URLField()

class PositionForm(forms.Form):
    title = forms.CharField()
    employer = forms.CharField()
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)

PositionFormSet = formset_factory(PositionForm, can_delete=True)
HistoryFormSet = formset_factory(HistoryForm)
