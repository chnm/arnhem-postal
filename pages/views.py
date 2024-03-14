from django.shortcuts import render
from django.views.generic import TemplateView


class AboutPageView(TemplateView):
    template_name = "postal/about.html"

class EvolutionOfHolocaustPageView(TemplateView):
    template_name = "postal/evolution-of-holocaust.html"
