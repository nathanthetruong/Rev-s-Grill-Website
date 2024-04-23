from django.urls import reverse, resolve
from django.test import TestCase, Client
from .models import MenuItems, Employees, Orders
from django.contrib.auth.models import User
from django.db import models

#pytest
#coverage run -m pytest
#coverage html

class TestTrendsUrls:
    # Ensures Trends Page URL and view are correctly linked
    def test_trends_url(self):
        path = reverse('Revs-trends-Screen')
        assert resolve(path).view_name == 'Revs-trends-Screen'

# class TestManagerView(TestCase):
#     def test_manager_get(self):
#         response = self.client.get(reverse('Revs-Manager-Screen'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'manager/manager.html')


class MenuItem(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
