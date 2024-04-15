from django.test import TestCase
from django.urls import reverse

class TrendsPageTests(TestCase):
    def setUp(self):
        self.url = reverse('trends')  
    def test_trends_page_loads_correctly(self):
        """ Test that the trends page loads correctly and uses the correct template. """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'trends.html')  # Check that the right template is used

    def test_trends_page_context_data(self):
        """ Test that the trends page includes necessary context data. """
        response = self.client.get(self.url)
        # Assuming context includes these keys, adjust according to your actual context
        self.assertIn('sales_trends_data', response.context)
        self.assertIn('monthly_growth_rates', response.context)

    def test_trends_page_form(self):
        """ Test that the date selection form is present and correctly set up. """
        response = self.client.get(self.url)
        # Check for the presence of the form and date input fields
        self.assertContains(response, '<form', 1)
        self.assertContains(response, '<input type="date"', 2)  # Two date inputs for start and end dates

    def test_trends_page_table_and_list_rendering(self):
        """ Test that the page renders a table for sales trends and a list for growth rates. """
        response = self.client.get(self.url)
        # Verify presence of the table and the list in the response
        self.assertContains(response, '<table')
        self.assertContains(response, '<ul')

class RestockPageTests(TestCase):
    def setUp(self):
        # Setting up the URL for the restock page
        self.url = reverse('restock') 

    def test_restock_page_loads_correctly(self):
        """Test that the restock page loads correctly."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_restock_page_uses_correct_template(self):
        """Test that the restock page uses the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'manager/restock.html')  
        
class ProductUsagePageTests(TestCase):
    def setUp(self):
        # Setting up the URL for the product usage page
        self.url = reverse('productusage') 

    def test_product_usage_page_loads_correctly(self):
        """Test that the product usage page loads correctly."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_product_usage_page_uses_correct_template(self):
        """Test that the product usage page uses the correct template."""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'manager/productusage.html')  
