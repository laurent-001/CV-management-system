from .models import CompanyInfo

def company_info_processor(request):
    """
    Makes the company information available to all templates.
    """
    company_info = CompanyInfo.objects.first()
    return {'company_info': company_info}
