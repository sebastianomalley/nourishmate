# 🌱 NourishMate

**🎥 [Watch Submission Video on YouTube](https://youtu.be/d-slbq5vMxs)**


A personal nutrition tracker and meal planner built with Django. Log your meals, track your macros and micronutrients, manage pantry and grocery lists, and get intelligent recipe suggestions—all in one place.

## What It Does

- **Food Logging**  
  Record each meal or snack with quantity, unit, category, and full nutrition breakdown (calories, protein, carbs, fats, vitamins, minerals, etc.).

- **Nutrition Summary**  
  View your totals for “Today,” last 7 days, 30 days, or any custom date range. See at-a-glance which nutrients are low or high compared to daily targets.

- **Pantry Management**  
  Keep an up-to-date list of what’s in your pantry. Increase or decrease quantities as you use items.

- **Grocery List**  
  Build a smart grocery list from recipe ingredients you’re missing. Add missing items directly from any recipe suggestion.

- **Recipe Search & Smart Suggestions**  
  • Traditional search by keywords (via Spoonacular API)  
  • “Smart” mode that combines your pantry contents with your nutrient gaps to recommend recipes that fill your dietary needs.

- **User Accounts & Saved Recipes**  
  Register and log in to save favorite recipes for later reference.

## Challenges & Lessons Learned

1. **Date-Picker Defaults & Time Zones**  
   - Browsers sometimes default the HTML date input to UTC, causing “today” to show as tomorrow.  
   - Solved by explicitly setting both the form’s `initial` and the widget’s `value` to Python’s `date.today()` in New York time.

2. **Inline Form Errors in Modals**  
   - Django’s built-in `{{ form.as_p }}` renders errors above inputs, which broke our Bootstrap layout in edit-entry modals.  
   - Fixed by manually rendering the `date_logged` field (and its error block) in each template so the red error text appears directly beneath the input.

3. **Dual `mode` Parameters in Recipe URLs**  
   - Having both a hidden `mode=search` and a checkbox `mode=smart` meant Django always saw the last value and skipped the intended branch.  
   - Resolved by grabbing the first `mode` value from `request.GET.getlist("mode")` so the user’s initial choice wins.

4. **Template & View Refactoring**  
   - Consolidated separate “smart” and “search” pages into a single `combined_recipe_view` and a single `recipe.html`.  
   - Cleaned up unused templates (e.g. `smart_recipe_suggestions.html`) and improved naming (e.g. `foodlog_form.html` → `foodlog_edit.html`).

## Future Improvements

- **AJAX Enhancements**  
  • Submit grocery‐list additions without a full page reload.  
  • Inline nutrient graphs and visuals.

- **Recipe Details**  
  • Show ingredient images and step-by-step instructions.  
  • Allow scaling recipe portions.

- **Mood Tracking**  
  • Let users log their mood alongside each food entry.  
  • Correlate mood data with nutrition trends over time.

- **Photo-Based Analysis**  
  • “Snap your plate” feature: upload a meal photo for automatic portion & nutrient estimation via an image-recognition API.  
  • Store and compare these scans alongside manual logs.

- **Data Visualization**  
  • Add interactive charts (e.g. weekly macronutrient & mood-correlation trends) using a JS library.


---

## Testing

Tests were created and can be found in `tracker/tests/`.  For example:

- **Model Tests** (e.g. `test_models.py`)  
- **Form & View Tests** (e.g. `test_forms.py`, `test_views.py`, `test_pantry.py`, etc.)  
- **Authentication & Permissions** (`test_auth.py`)  
- **Endpoint Smoke Tests** (`test_recipe_endpoints.py`) for:
  - AJAX “Save Recipe” (`save_recipe` returns JSON + creates record)  
  - Non-AJAX “Save Recipe” (redirects + creates record)  
  - “Delete Saved Recipe” (removes record + redirects)

To run all tests:

```bash
python manage.py test
