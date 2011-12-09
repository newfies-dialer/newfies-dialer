import newfies

def newfies_version(request):
    return { 'newfies_version': newfies.__version__ }
    
