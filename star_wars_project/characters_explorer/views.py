from django.views.generic.base import TemplateView
from django.views.generic import ListView, DetailView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils import timezone
from django.conf import settings
from . import models
from .forms import ValueCountForm

import requests
import math
import concurrent.futures
import petl
import datetime


class Home(TemplateView):
    """
    Home page
    """    
    template_name = 'characters_explorer/index.html'


class Collections(ListView):
    """
    View representing list of collections
    """    
    context_object_name = 'characters_list'
    model = models.Characters
    template_name = 'characters_explorer/collections.html'

    def post(self, request):
        """_
        Method to return post request
        """        
        characters_url = "https://swapi.dev/api/people/"
        planets_url = "https://swapi.dev/api/planets/"
        count_urls = [{'resource_type': 'characters', 'url': characters_url},
                      {'resource_type': 'planets', 'url': planets_url}]

        # Collect number of planets and characters to download
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(count_urls)) as executor:
            count_per_resource = executor.map(self._request_count, count_urls)

        for count in count_per_resource:
            if 'characters' in count:
                count_characters = count['characters']
                results_characters = count['results']
            elif 'planets' in count:
                count_planets = count['planets']
                results_planets = count['results']

        print(
            f'received counts characters = {count_characters}, planets = {count_planets}')

        urls_characters = [{'resource_type': 'characters', 'url': f'https://swapi.dev/api/people/?page={page}'}
                           for page in range(2, math.ceil(count_characters / 10) + 1)]
        urls_planets = [{'resource_type': 'planets', 'url': f'https://swapi.dev/api/planets/?page={page}'}
                        for page in range(2, math.ceil(count_planets / 10) + 1)]
        results_urls = urls_characters + urls_planets

        # Collect the data for planets and characters, good alternative is  Asynchronism but i would require 
        # different library than recommended requests, so multithreading was used
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(results_urls)) as executor:
            results_per_page = executor.map(
                self._request_results, results_urls)

        for result in results_per_page:
            if 'characters' in result:
                results_characters += result['characters']
            elif 'planets' in result:
                results_planets.update(result['planets'])

        print(
            f'received {len(results_characters)} characters and {len(results_planets)} planets')

        # Transform and save the characters table
        characters_table = self._table_transform(
            results_characters, results_planets)
        characters_model = models.Characters()
        characters_model.download_date = timezone.now()
        characters_model.folder_path = 'collections'
        characters_model.save(characters_table=characters_table)

        return HttpResponseRedirect(self.request.path_info)

    def _request_count(self, url):
        """
        Helper method to count number of planets and characters to be requested

        Args:
            url (str): url to get count from

        Returns:
            dict: dict containing resources count and results to not be repeated
        """        
        response = requests.get(url['url'])
        response_data = response.json()
        if url['resource_type'] == 'planets':
            results = {}
            for planet in response_data['results']:
                results[planet["url"]] = planet["name"]
        else:
            results = response_data['results']

        return {url['resource_type']: response_data['count'], 'results': results}

    def _request_results(self, url):
        """
        Helper method to get results from given url

        Args:
            url (str): url to get results from

        Returns:
            dict: results for given resource
        """        
        response = requests.get(url['url'])
        response_data = response.json()

        if url['resource_type'] == 'planets':
            results = {}
            for planet in response_data['results']:
                results[planet["url"]] = planet["name"]
        else:
            results = response_data['results']

        return {url['resource_type']: results}

    def _table_transform(self, results_characters, planets_dict):
        """
        Helper method to transform the table

        Args:
            results_characters (Table): Petl table containing characters
            planets_dict (dict): dictionary with planets

        Returns:
            Table: transformed Petl table
        """        
        # To speed up transformations for larger datasets Multiprocessing can be used
        characters_table = petl.fromdicts(results_characters)
        characters_table = petl.cut(characters_table, "name", "height", "mass", "hair_color",
                                    "skin_color", "eye_color", "birth_year", "gender", "homeworld", "edited")

        characters_table = petl.convert(characters_table, 'edited', lambda date: datetime.datetime.strptime(
            date, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d'))
        characters_table = petl.rename(characters_table, 'edited', 'date')

        characters_table = petl.convert(
            characters_table, 'homeworld', planets_dict)

        return characters_table


class CollectionDetails(DetailView):
    """
    View representing details about given collection
    """    
    context_object_name = 'characters_details'
    model = models.Characters
    template_name = 'characters_explorer/collection_details.html'

    count_buttons_checked = {'name': '',
                             'height': '',
                             'mass': '',
                             'hair_color': '',
                             'skin_color': '',
                             'eye_color': '',
                             'birth_year': '',
                             'gender': '',
                             'homeworld': '',
                             'date': ''}

    def get_context_data(self, **kwargs):
        """
        Overridden get context method to add csv files data to the context

        Returns:
            dict: context
        """        
        obj = self.get_object()
        context = super(CollectionDetails, self).get_context_data(**kwargs)
        context['file_name'] = obj.file_name

        characters_table = petl.fromcsv(
            settings.MEDIA_ROOT.joinpath(obj.folder_path, obj.file_name))

        load_number = self.kwargs['load_num'] if self.kwargs['load_num'] <= petl.nrows(
            characters_table) else petl.nrows(characters_table)

        characters_table = petl.head(characters_table, load_number)
        headers = petl.header(characters_table)

        context['headers'] = headers
        context['collection_data'] = list(
            petl.values(characters_table, *headers))
        context['value_count_buttons'] = self.count_buttons_checked
        context['load_more'] = True
        return context

    def post(self, request, pk, load_num, *args, **kwargs):
        """_
        Method to return post request depending on the form 
        """  
        if 'value_count' in request.POST:
            form = ValueCountForm(request.POST)
            if form.is_valid():
                cleaned_data = [elem[0]
                                for elem in form.cleaned_data.items() if elem[1]]
                if len(cleaned_data) >= 1:
                    for button in self.count_buttons_checked:
                        if button in cleaned_data:
                            self.count_buttons_checked[button] = 'checked'
                        else:
                            self.count_buttons_checked[button] = ''
                    context = self._get_value_count_context(cleaned_data)
                    return render(request, self.template_name, context=context)
                else:
                    for key in self.count_buttons_checked.keys():
                        self.count_buttons_checked[key] = ''
                    return redirect('collection_details', pk=pk, load_num=10)

        load_number = self.kwargs['load_num'] + 10
        return redirect('collection_details', pk=pk, load_num=load_number)

    def _get_value_count_context(self, cleaned_data):
        """
        Helper method to create table with value count

        Args:
            cleaned_data (list): list with form's set buttons

        Returns:
            dict: context
        """        
        context = {}
        obj = self.get_object()

        context['file_name'] = obj.file_name
        characters_table = petl.fromcsv(
            settings.MEDIA_ROOT.joinpath(obj.folder_path, obj.file_name))
        characters_table = petl.valuecounts(characters_table, *cleaned_data)
        characters_table = petl.cutout(characters_table, 'frequency')

        context['headers'] = petl.header(characters_table)
        context['collection_data'] = list(
            petl.values(characters_table, *context['headers']))

        context['value_count_buttons'] = self.count_buttons_checked

        context['load_more'] = False
        return context
