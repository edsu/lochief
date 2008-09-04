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

# Future home of cataloging views.

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader, RequestContext
from django.utils import simplejson

from helios.cataloging import models
from helios.cataloging import forms

def edit_record(request, id):
    context = RequestContext(request)
    record = get_object_or_404(models.Record, id=id)
    version = record.current_version()
    data = simplejson.loads(version.data)
    
    form = forms.PersonForm(data)
    context['form'] = form
    template = loader.get_template('cataloging/edit_person.html')
    response = HttpResponse(template.render(context))
    return response
