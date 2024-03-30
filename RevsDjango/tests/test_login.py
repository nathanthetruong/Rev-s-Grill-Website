from django.urls import reverse, resolve

class TestUrls:
    # Ensures Login URL and view are correctly linked
    def test_login_url(self):
        path = reverse('Revs-Login-Screen')
        assert resolve(path).view_name == 'Revs-Login-Screen'