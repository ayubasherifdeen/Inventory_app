import autocomplete_light
from .models import Product

autocomplete_light.register(
    Product,
    search_fields['sku'],
    attrs={'data-autocomplete-minimum-characters':1},
)
