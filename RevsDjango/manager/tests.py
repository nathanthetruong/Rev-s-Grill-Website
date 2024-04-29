from django.urls import reverse, resolve
from django.test import TestCase, Client
from .models import MenuItems, Employees, Orders, Inventory
from django.contrib.auth.models import User
from django.db import models
from django.test import override_settings
from .views import StartDateForm, EndDateForm
from .views import getExcessReport
from django.utils import timezone
from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages

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
        self.assertIn('Frequency', response.content.decode())


class TestManagerPage(TestCase):
    def test_add_new_menu_item(self):
        item_count_before = MenuItems.objects.count()
        response = self.client.post(reverse('Revs-Manager-Screen'), data={
            'price': '9.99',
            'description': 'New Burger',
            'category': 'Burgers',
            'times_ordered': '0',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
        })
        item_count_after = MenuItems.objects.count()
        self.assertEqual(item_count_after, item_count_before + 1)
        self.assertRedirects(response, reverse('Revs-Manager-Screen'))

    def test_manager_page_loads_correctly(self):
        response = self.client.get(reverse('Revs-Manager-Screen'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manager Page')


class ExcessReportPageTests(TestCase):
    def test_excess_report_page_loads_correctly(self):
        response = self.client.get(reverse('Revs-excess-Screen'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Excess Report")
        self.assertContains(response, '<input type="date"', count=2)  # Checks for two date inputs
        self.assertContains(response, '<form')  # Checks for presence of forms

    def test_excess_report_page_content(self):
        response = self.client.get(reverse('Revs-excess-Screen'))
        self.assertEqual(response.status_code, 200)
        # Check for specific content that should always be present
        self.assertContains(response, "Excess Report")
        self.assertContains(response, "Start Date:")
        self.assertContains(response, "End Date:")
        self.assertContains(response, "Submit")


class RestockReportPageTests(TestCase):

    def test_restock_report_page_access(self):
        response = self.client.get(reverse('Revs-restock-Screen'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manager/restock.html')


class ProductUsagePageTests(TestCase):
    def test_product_usage_page_loads_correctly(self):
        """ Test if the Product Usage page loads successfully """
        response = self.client.get(reverse('Revs-productusage-Screen'))
        self.assertEqual(response.status_code, 200)

    def test_product_usage_page_content(self):
        """ Test for the presence of static text in the Product Usage page """
        response = self.client.get(reverse('Revs-productusage-Screen'))
        self.assertIn('Product Usage', response.content.decode())
        self.assertIn('Start Date:', response.content.decode())
        self.assertIn('End Date:', response.content.decode())




#tests views.py
#check compatablity with database 

# class MenuItemsTests(TestCase):
#     def setUp(self):
#         # Create sample data here if needed
#         MenuItems.objects.create(
#             price=10.99,
#             description="Test Burger",
#             category="Burgers",
#             times_ordered=10,
#             start_date="2021-01-01",
#             end_date="2021-12-31"
#         )

#     def test_add_menu_item(self):
#         # Mimic the file upload
#         image_path = '/path/to/image.jpg'
#         image = SimpleUploadedFile(name='test_image.jpg', content=open(image_path, 'rb').read(), content_type='image/jpeg')
#         response = self.client.post(reverse('Revs-Manager-Screen'), data={
#             'price': 12.99,
#             'description': 'New Veggie Burger',
#             'category': 'Burgers',
#             'times_ordered': 0,
#             'start_date': '2022-01-01',
#             'end_date': '2022-12-31',
#             'image': image
#         })
#         self.assertEqual(response.status_code, 302)  # Expecting a redirect after POST
#         self.assertEqual(MenuItems.objects.count(), 2)  # Check if the item was added

#     def test_delete_menu_item(self):
#         item_id = MenuItems.objects.get(description="Test Burger").id
#         response = self.client.post(reverse('deleteItem'), {'item_id': item_id})
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(MenuItems.objects.count(), 0)  # Item should be deleted

#     def test_modify_menu_item(self):
#         item = MenuItems.objects.get(description="Test Burger")
#         response = self.client.post(reverse('modifyItem'), {
#             'item_id': item.id,
#             'price': 15.00,
#             'description': item.description,
#             'category': item.category,
#             'times_ordered': item.times_ordered,
#             'start_date': item.start_date,
#             'end_date': item.end_date
#         })
#         self.assertEqual(response.status_code, 302)
#         item.refresh_from_db()
#         self.assertEqual(item.price, 15.00)

#     def test_manager_page_loads_correctly(self):
#         response = self.client.get(reverse('Revs-Manager-Screen'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'manager/manager.html')

#     def test_form_errors(self):
#         response = self.client.post(reverse('Revs-Manager-Screen'), data={
#             'price': 12.99,
#             'description': 'New Veggie Burger',
#             'category': 'Burgers',
#             'times_ordered': 0,
#             'start_date': '2023-01-01',
#             'end_date': '2022-12-31'  # Invalid end date
#         })
#         messages = list(get_messages(response.wsgi_request))
#         self.assertEqual(len(messages), 1)
#         self.assertIn('End date must be after start date', str(messages[0]))

