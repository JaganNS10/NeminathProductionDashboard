from .models import Sheet

def sidebar_sheets(request):
    return {
        'sidebar_sheets': Sheet.objects.filter(is_active=True)
    }