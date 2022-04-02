from import_export import resources
from .models import Cuisine

class CuisineResource(resources.ModelResource):
    class meta:
        model = Cuisine
