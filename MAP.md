
# ThoughtTronix Codebase Map

## 1. The Four Django Apps

- **accounts:** This app handles user accounts, including signing up, logging in, and controlling employee access.
- **products:** This app manages the products being sold, their categories, and what customers see when browsing the store.
- **orders:** This app handles shopping carts, checkout, placing orders, and viewing previous purchases.
- **dashboard:** This app provides employees with sales information, including revenue, orders, and popular products.

## 2. How the Home Page Loads

When someone visits the ThoughtTronix homepage at `/`, Django checks `config/urls.py` to find where the request should go. The `products/urls.py` file connects the homepage to `CatalogView` in `products/views.py`. This view retrieves the products and applies any search or category filters. The `templates/products/catalog.html` file displays the products, while `templates/base.html` provides the overall page layout.
  
  ## 3. Exploring the Cart Model

  The Cart model in orders/models.py keeps track of a customer's shopping cart. One method I found interesting was add(), because when a customer adds the same product more than once, the system increases the quantity instead of creating separate entries for that product.


## 4. What Happens When a Category Is Deleted?

```python
category = models.ForeignKey(
    Category,
    on_delete=models.PROTECT,
    related_name="products",
)
```

This code in `products/models.py` prevents a category from being deleted if it still has products assigned to it. The `on_delete=models.PROTECT` setting protects those products from being accidentally removed. Before the category can be deleted, the products must either be moved to another category or deleted first.
  
## 5. How the Tests Are Organized

ThoughtTronix uses pytest and pytest-django to test the different parts of the website. The tests are organized within each Django app, such as accounts, products, orders, and dashboard.

The conftest.py file contains shared fixtures that create sample data for testing. These fixtures set up things like customers, employees, products, categories, and shopping carts. This allows the tests to check whether different features work correctly without having to create the same information every time.

When I ran the tests, all 164 passed successfully.

## 6. Something I Still Find Confusing

One thing I found confusing was how the store handles inventory when multiple customers purchase the same product. I asked Claude what would happen if two customers tried to buy the last available item at the same time. I learned that ThoughtTronix does not actually track inventory quantities. It only checks whether a product is marked as available. I understand why both orders would go through, but I am still curious about how inventory tracking would be added to prevent overselling.


## 7. My Three Original Questions

**Question 1:** What happens if two customers try to buy the last available product at the same time? Does the system determine who gets it?

**What I learned:** ThoughtTronix does not track inventory quantities, so both customers can successfully place an order as long as the product is marked as available.

**Question 2:** If a customer places an order and changes their mind, can they cancel it themselves, or does an employee have to do it?

**What I learned:** Customers cannot cancel their own orders, and an employee must change the order status to Cancelled through the Back Office.

**Question 3:** What happens if a customer forgets their password? Can they reset it themselves, or does someone have to help them?

**What I learned:** The website does not have a password reset option, so someone with superuser access must reset the customer's password.
  