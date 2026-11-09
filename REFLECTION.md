## Discount Coupons

**Question 1: Design Decision and Follow-Up**

During the design interview, I didn't really disagree with Claude or find any of the questions confusing because the options were explained clearly. One decision I thought was important was how the coupon information would be saved on orders. I chose to have the discount details saved with each order so that changing or retiring a coupon wouldn't affect previous purchases. After implementing the feature, I tested this by placing an order with a coupon, retiring that coupon, and checking that the original order total stayed the same. This helped me understand why saving the original order information matters.

**Question 2: Implementation Review and Improvement**

After reviewing the implementation, Claude identified an issue where entering a duplicate coupon code with different capitalization could cause the admin page to crash instead of displaying a validation error. I decided to fix this because staff should receive a clear message when a coupon code already exists. We made the correction and added a test to make sure the issue wouldn't happen again. This improved the reliability of the coupon management feature.

## Featured Products

The Featured Products feature starts in `products/models.py`, where the `is_featured` field was added to the Product Model. The database migration saves that new field. The `catalog.html` and `detail.html` templates check whether a product is marked as featured. If it is, the website labels the product with a Featured badge. I learned that adding a field to the model alone doesn't make it appear on the website. The templates also have to be updated in order for it to display it.

I tested the feature by marking Seraphine, SoulSear Mark I, and SoulSear Mark II as featured in Django Admin. I then checked the storefront to make sure the Featured badges appeared on the correct products. I also opened Seraphine's individual product page to confirm the badge displayed there. After making the changes, I ran `uv run pytest`, and all 164 tests passed.

One challenge I ran into was getting the Featured badges to display on the correct products. After selecting Seraphine as a featured product, I noticed that its Featured badge wasn't showing up like it was supposed to. However, Seraphine Doorbell was showing as featured even though I hadn't selected it. I decided to check the settings in Django Admin before making any changes to the code because the badges were already displaying, just not on the correct products. I wanted to make sure the issue wasn't caused by the selected checkboxes before changing something that was already working. I had to restart the admin page, and double-check the Featured checkboxes for both products. I made sure Seraphine was checked and Seraphine Doorbell was unchecked, then saved the changes and checked the storefront again. This taught me that even when the code is working correctly, I still need to verify the settings and test the website to make sure everything displays the way it's supposed to.