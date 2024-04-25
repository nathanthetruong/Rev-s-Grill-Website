from django.urls import reverse, resolve
from django.test import TestCase, Client
from .models import MenuItems, Employees, Orders
from django.contrib.auth.models import User
from django.db import models
from django.test import override_settings

#pytest
#coverage run -m pytest
#coverage html

class TestTrendsUrls:
    """
    Tests to ensure that the URL for the Trends page is correctly configured
    and resolves to the intended view.
    """
    def test_trends_url(self):
        path = reverse('Revs-trends-Screen')
        assert resolve(path).view_name == 'Revs-trends-Screen'

class TestManagerView(TestCase):
    """
    Tests to check if the Manager page loads correctly and uses the appropriate
    template when accessed.
    """
    def test_manager_get(self):
        response = self.client.get(reverse('Revs-Manager-Screen'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manager/manager.html')

class MenuItem(models.Model):
    """
    Defines a model for storing menu items with their names, prices, and descriptions.
    """
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()

class TrendsPageTests(TestCase):
    """
    Tests to verify that the Trends page renders correctly, returns a 200 OK status,
    uses the correct template, and includes the necessary context data.
    """
    def test_trends_page_renders_correct_template(self):
        response = self.client.get(reverse('Revs-trends-Screen'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manager/trends.html')
        self.assertIn('trends', response.context)

@override_settings(STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class StaticFilesTest(TestCase):
    """
    Tests to ensure that static files are correctly loaded in the Trends page.
    This includes checking for the presence of specific CSS and image files in the rendered HTML.
    """
    def test_static_files_loaded(self):
        response = self.client.get(reverse('Revs-trends-Screen'))
        self.assertIn('managerstyle.css', response.content.decode())
        self.assertIn('rev.png', response.content.decode())


class ContentDisplayTest(TestCase):
    def setUp(self):
        # Set up data here if needed
        pass

    def test_content_display(self):
        response = self.client.get(reverse('Revs-trends-Screen'))
        self.assertIn('Item 1', response.content.decode())
        self.assertIn('Total Sales', response.content.decode())

    
# class FormSubmissionTest(TestCase):
#     def test_form_submission(self):
#         data = {
#             'startDate': '2023-01-01',
#             'endDate': '2023-12-31'
#         }
#         response = self.client.post(reverse('Revs-trends-Screen'), data)
#         self.assertEqual(response.status_code, 302)  # Assuming it redirects after POST


# class MenuItemTestCase(TestCase):
#     def setUp(self):
#         # Set up data for the whole TestCase
#         MenuItem.objects.create(name="Burger", price=9.99, description="A classic burger.")

    # def test_create_menu_item(self):
    #     """Test the creation of a menu item."""
    #     MenuItem.objects.create(name="Salad", price=5.99, description="Fresh garden salad.")
    #     self.assertEqual(MenuItem.objects.count(), 2)

#     def test_read_menu_item(self):
#         """Test reading a menu item."""
#         item = MenuItem.objects.get(name="Burger")
#         self.assertEqual(item.price, 9.99)
#         self.assertEqual(item.description, "A classic burger.")

    # def test_update_menu_item(self):
    #     """Test updating a menu item."""
    #     item = MenuItem.objects.get(name="Burger")
    #     item.price = 10.99
    #     item.save()
    #     updated_item = MenuItem.objects.get(name="Burger")
    #     self.assertEqual(updated_item.price, 10.99)

#     def test_delete_menu_item(self):
#         """Test deleting a menu item."""
#         item = MenuItem.objects.get(name="Burger")
#         item.delete()
#         self.assertEqual(MenuItem.objects.count(), 0)