from django.shortcuts import redirect
from django.urls import reverse
from .mongo_utils import get_profiles_collection

class ProfileCompletionMiddleware:
    """
    Middleware to force users to complete their profile 
    before they can proceed to checkout or other restricted actions.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URLs that DON'T require profile completion
        # We must allow the profile completion page itself, and auth pages!
        exempt_urls = [
            reverse('home'),
            reverse('login'),
            reverse('signup'),
            reverse('logout'),
            reverse('complete_profile'),
            '/admin/',
            '/static/',
            '/media/',
        ]

        if request.user.is_authenticated:
            # Check if current path is in exempt list
            current_path = request.path
            is_exempt = any(current_path.startswith(url) for url in exempt_urls)

            if not is_exempt:
                # Check if profile is complete in MongoDB
                profiles_col = get_profiles_collection()
                profile = profiles_col.find_one({'user_id': request.user.id})
                
                if not profile or not profile.get('is_complete', False):
                    # Redirect to complete profile page
                    return redirect('complete_profile')

        response = self.get_response(request)
        return response
