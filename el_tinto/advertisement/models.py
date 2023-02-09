from django.db import models


class Leads(models.Model):
    COWORKINGS = 'COWORKINGS'
    RESTAURANTS = 'RESTAURANTS'
    LIBRARIES = 'LIBRARIES'
    THEATERS = 'THEATERS'
    CAFES = 'CAFES'

    SITES = [
        (COWORKINGS, "Co-workings"),
        (RESTAURANTS, "Restaurantes"),
        (LIBRARIES, "Bibliotecas"),
        (THEATERS, "Teatros"),
        (CAFES, "Cafés")
    ]

    created = models.DateTimeField(auto_now_add=True)
    site = models.CharField(max_length=15, choices=SITES, default='')
    request_info = models.TextField(default='')