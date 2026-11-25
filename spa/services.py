
import requests


def obtener_productos_belleza():

    url = 'https://world.openbeautyfacts.org/cgi/search.pl'

    parametros = {
        'search_terms': 'face cream',
        'search_simple': 1,
        'action': 'process',
        'json': 1,
        'page_size': 6,
        'fields': 'product_name,brands,image_front_url'
    }

    encabezados = {
        'User-Agent': 'AlmaSpa/1.0'
    }

    respuesta = requests.get(
        url,
        params=parametros,
        headers=encabezados,
        timeout=10
    )

    respuesta.raise_for_status()

    datos = respuesta.json()

    productos = []

    for producto in datos.get('products', []):

        if producto.get('product_name'):

            productos.append({
                'nombre': producto.get('product_name'),
                'marca': producto.get('brands', ''),
                'imagen': producto.get('image_front_url', '')
            })

    return productos
