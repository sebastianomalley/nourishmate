"""
This file contains all of the request handlers for NourishMate.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.timezone import localdate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest

from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta
import requests
import json

from .models import (
    FoodLog, GroceryItem, CATEGORY_CHOICES,
    PantryItem, SupplementLog, SavedRecipe
)
from .forms import FoodLogForm, PantryItemForm


# ─── Module-level constants ─────────────────────────────────────────────────────
CATEGORY_ORDER = [
    'fruit',
    'vegetable',
    'meat',
    'protein',
    'grain',
    'dairy',
    'fish',
    'frozen',
    'dessert',
    'wine',
    'other'
]

# Supplements for (home page).
SUPPLEMENT_NUTRIENTS = {
    "morning": {
        "vitamin_d": 30,
        "vitamin_b12": 3.0,
        "calcium": 1200,
    },
    "afternoon": {
        "iron": 25,
        "vitamin_c": 120,
    },
    "evening": {
        "fiber": 35,
        "magnesium": 500,
        "zinc": 15,
    },
}


# ─── Authentication / Registration ──────────────────────────────────────────────
def register(request):
    """
    Allow a new user to sign up with username/password.
    Auto-log them in and redirect to home.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()

    for name, field in form.fields.items():
        field.widget.attrs["class"] = "form-control"

    form.fields["password1"].label = "Password"
    form.fields["password2"].label = "Confirm"

    return render(request, "tracker/register.html", {"form": form})


# ─── Home / Dashboard ───────────────────────────────────────────────────────────
@login_required
def home(request):
    """
    Show today’s supplement status and a summary of
    today’s nutrient intake vs. daily targets.
    """
    today = localdate()
    logs = FoodLog.objects.filter(date_logged=today)
    DAILY_TARGETS = {
        "calories": 2000,
        "protein": 50,
        "fiber": 25,
        "vitamin_c": 75,
        "iron": 18,
        "vitamin_d": 20,
        "vitamin_b12": 2.4,
        "calcium": 1000,
        "magnesium": 400,
        "zinc": 11,
    }

    totals = {nutrient: 0 for nutrient in DAILY_TARGETS}

    for log in logs:
        for nutrient in totals:
            totals[nutrient] += getattr(log, nutrient, 0)

    taken = {slot: False for slot in SUPPLEMENT_NUTRIENTS.keys()}

    logs_today = SupplementLog.objects.filter(user=request.user, date=today)
    for log in logs_today:
        taken[log.time_of_day] = True
        for nutrient, amount in SUPPLEMENT_NUTRIENTS.get(log.time_of_day, {}).items():
            if nutrient in totals:
                totals[nutrient] += amount

    low_nutrients = [
        nutrient for nutrient, target in DAILY_TARGETS.items()
        if totals[nutrient] < target * 0.8
    ]

    return render(request, 'tracker/home.html', {
        "low_nutrients": low_nutrients,
        "taken_supplements": taken,
        "slots": list(SUPPLEMENT_NUTRIENTS.keys()),
        "totals": totals,
    })

@login_required
@require_POST
def toggle_supplement(request, slot):
    valid_slots = ['morning', 'afternoon', 'evening']
    if slot not in valid_slots:
        return redirect('home')

    today = localdate()
    log = SupplementLog.objects.filter(user=request.user, date=today, time_of_day=slot).first()

    if log:
        log.delete()
    else:
        SupplementLog.objects.create(user=request.user, date=today, time_of_day=slot)

    return redirect('home')


# ─── FoodLog CRUD ───────────────────────────────────────────────────────────────
@login_required
def food_log_list(request):
    """
    List AND paginate FoodLog entries.
    """
    sort = request.GET.get('sort', 'date_desc')
    category_filter = request.GET.get('category', '')

    sort_map = {
        'date_asc': 'date_logged',
        'date_desc': '-date_logged',
        'name_asc': 'food_name',
        'name_desc': '-food_name',
        'calories_asc': 'calories',
        'calories_desc': '-calories',
    }

    qs = FoodLog.objects.order_by(sort_map.get(sort, '-date_logged'))

    if category_filter:
        qs = qs.filter(category=category_filter)

    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj   = paginator.get_page(page_number)

    if request.method == 'POST':
        form = FoodLogForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(f"{request.path}?page={page_obj.number}&sort={sort}&category={category_filter}")
    else:
        form = FoodLogForm()

    bound_forms = {log.pk: FoodLogForm(instance=log) for log in page_obj}

    return render(request, 'tracker/food_log_list.html', {
        'form': form,
        'page_obj': page_obj,
        'bound_forms': bound_forms,
        'sort': sort,
        'category_filter': category_filter,
        'CATEGORY_CHOICES': CATEGORY_CHOICES,
    })


class FoodLogUpdateView(LoginRequiredMixin, UpdateView):
    """
    Edit an existing FoodLog entry.
    """
    model = FoodLog
    form_class = FoodLogForm
    template_name = "tracker/food_log_edit.html"

    def get_success_url(self):
        base = reverse_lazy("food_log_list")
        qs   = self.request.GET.urlencode()
        return f"{base}?{qs}" if qs else base

    def form_valid(self, form):
        """
        Handle successful form submission.
        """
        self.object = form.save()
        redirect_url = self.get_success_url()
        return HttpResponseRedirect(redirect_url)

    def form_invalid(self, form):
        """
        Handle form errors.
        """
        return self.render_to_response(self.get_context_data(form=form))

from django.urls import reverse


class FoodLogDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a FoodLog entry.
    """
    model = FoodLog
    template_name = "tracker/foodlog_confirm_delete.html"

    def get_success_url(self):
        """
        Redirect back to the list.
        """
        base = reverse("food_log_list")
        qs   = self.request.GET.urlencode()
        return f"{base}?{qs}" if qs else base
    

# ─── Grocery List ────────────────────────────────────────────────────────────────
@login_required
def add_to_grocery_list(request):
    """
    Handles both JSON-based (AJAX) and form POST submissions to add items to GroceryItem.
    """
    try:
        if request.method == "POST":
            # Determine request type.
            if request.headers.get("Content-Type") == "application/json":
                data = json.loads(request.body)
                items = data.get("items", [])
                quantities = data.get("quantities", [])
                categories = data.get("categories", [])
                next_url = data.get("next", "/grocery/")
            else:
                # Handle regular form POST.
                items = request.POST.getlist("food_name")
                quantities = request.POST.getlist("quantity")
                categories = request.POST.getlist("category")
                next_url = request.POST.get("next", "/grocery/")

            # Save each grocery item.
            for name, qty, cat in zip(items, quantities, categories):
                GroceryItem.objects.create(
                    user=request.user,
                    name=name,
                    quantity=qty,
                    category=cat or "other"
                )

            # Response based on request type.
            if request.headers.get("Content-Type") == "application/json":
                return JsonResponse({"status": "ok"})
            else:
                return HttpResponseRedirect(next_url)

        return HttpResponseBadRequest("Only POST requests are allowed.")

    except Exception as e:
        if request.headers.get("Content-Type") == "application/json":
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
        return HttpResponseBadRequest("An error occurred: " + str(e))


@login_required
def grocery_list(request):
    """
    Group GroceryItem by category and render.
    """
    items = GroceryItem.objects.all().order_by('added_on')
    grouped = defaultdict(list)
    for item in items:
        grouped[item.category].append(item)

    ordered_grouped = OrderedDict()
    for category in CATEGORY_ORDER:
        if category in grouped:
            ordered_grouped[category] = grouped[category]

    return render(request, 'tracker/grocery_list.html', {
        'grouped_items': ordered_grouped,
        'CATEGORY_CHOICES': CATEGORY_CHOICES
    })


@login_required
def toggle_purchased(request, item_id):
    """Toggle the `purchased` flag on a GroceryItem."""
    item = get_object_or_404(GroceryItem, id=item_id)
    item.purchased = not item.purchased
    item.save()
    return redirect('grocery_list')


@login_required
def delete_grocery_item(request, item_id):
    """Delete a GroceryItem and redirect back to list."""
    item = get_object_or_404(GroceryItem, id=item_id)
    item.delete()
    return redirect('grocery_list')


@login_required
def update_grocery_category(request, item_id):
    """POST to update a GroceryItem’s category."""
    if request.method == "POST":
        item = get_object_or_404(GroceryItem, id=item_id)
        new_category = request.POST.get("category")
        if new_category:
            item.category = new_category
            item.save()
    return redirect('grocery_list')


# ─── Pantry Management ──────────────────────────────────────────────────────────
@login_required
def pantry_list(request):
    """List all PantryItem for the current user."""
    items = PantryItem.objects.filter(user=request.user).order_by('name')
    return render(request, 'tracker/pantry_list.html', {'items': items})


@login_required
def add_pantry_item(request):
    """
    Display and process the PantryItemForm to add a new pantry item.
    """
    if request.method == 'POST':
        form = PantryItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            return redirect('pantry_list')
    else:
        form = PantryItemForm()
    return render(request, 'tracker/add_item.html', {'form': form})


@login_required
def edit_pantry_item(request, pk):
    """Display and process form to edit an existing PantryItem."""
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PantryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('pantry_list')
    else:
        form = PantryItemForm(instance=item)
    return render(request, 'tracker/edit_item.html', {'form': form, 'item': item})


@login_required
def delete_pantry_item(request, pk):
    """Delete a PantryItem and redirect back to pantry_list."""
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    item.delete()
    return redirect('pantry_list')


@login_required
@require_POST
def increase_quantity(request, pk):
    """Increase a PantryItem’s quantity by 1."""
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    item.quantity += 1
    item.save()
    return redirect('pantry_list')


@login_required
@require_POST
def decrease_quantity(request, pk):
    """Decrease a PantryItem’s quantity by 1."""
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    return redirect('pantry_list')


# ─── Recipe Search & Smart Suggestions ─────────────────────────────────────────
@login_required
def combined_recipe_view(request):
    """
    For recipe search AND smart suggestions.
    Renders `tracker/recipe.html` with `results` and `smart_results`.
    """
    api_key = settings.SPOONACULAR_API_KEY
    user        = request.user
    mode        = request.GET.get("mode")
    query       = request.GET.get("ingredients", "")
    diet        = request.GET.get("diet", "")
    sort        = request.GET.get("sort", "")
    max_time    = request.GET.get("max_time", "")

    results, smart_results = [], []

    # ---------- GENERAL SEARCH ----------
    if mode != "smart" and query: 
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "query": query,
            "diet": diet,
            "sort": sort,
            "maxReadyTime": max_time,
            "number": 6,
            "apiKey": api_key,
        }
        params = {k: v for k, v in params.items() if v}
        resp = requests.get(url, params=params)
        if resp.status_code == 200:
            results = resp.json().get("results", [])

    # Smart suggestions from pantry + nutrient lows.
    # ---------------------------------------------
    # Build the ingredient list for SMART mode.
    #  • Pantry items (always used)
    #  • User ingredient query (only if they typed one)
    # ---------------------------------------------
    pantry_items = PantryItem.objects.filter(user=user)
    pantry_list = [item.name for item in pantry_items]

    if query:
        # User typed something...use that instead of the whole pantry.
        ingredients_list = [i.strip() for i in query.split(",") if i.strip()]
    else:
        # No query...fall back to pantry for smart mode.
        ingredients_list = pantry_list

    ingredients = ",".join(ingredients_list)
    
    DAILY_TARGETS = {
        "calories": 2000,
        "protein": 50,
        "fiber": 25,
        "vitamin_c": 75,
        "iron": 18,
        "vitamin_d": 20,
        "vitamin_b12": 2.4,
        "calcium": 1000,
        "magnesium": 400,
        "zinc": 11,
    }

    today = localdate()
    logs = FoodLog.objects.filter(date_logged=today)
    supplement_logs = SupplementLog.objects.filter(user=user, date=today)

    totals = {k: 0 for k in DAILY_TARGETS}
    for log in logs:
        for k in totals:
            totals[k] += getattr(log, k, 0)
    for log in supplement_logs:
        boosts = SUPPLEMENT_NUTRIENTS.get(log.time_of_day, {})
        for k, v in boosts.items():
            if k in totals:
                totals[k] += v

    low_nutrients = [k for k, v in DAILY_TARGETS.items() if totals[k] < v * 0.8]

    def ensure_working_image(recipe):
        url = recipe.get("image")
        if url and url.strip():
            return url
        fallback_url = f"https://spoonacular.com/recipeImages/{recipe['id']}-480x360.jpg"
        return fallback_url

    # Get smart recipes from pantry.
    if mode == "smart":
        smart_url = "https://api.spoonacular.com/recipes/findByIngredients"
        smart_params = {
            "ingredients": ingredients,
            "number": 6,
            "ranking": 2,
            "ignorePantry": True,
            "apiKey": api_key
        }

        if diet:
            smart_params["diet"] = diet

        smart_response = requests.get(smart_url, params=smart_params)
        if smart_response.status_code == 200:
            data = smart_response.json()
            smart_results = data.get("results", []) if isinstance(data, dict) else data

        # ───────── Better scoring? based on actual nutrition. ─────────
        if mode == "smart":
            smart_url = "https://api.spoonacular.com/recipes/findByIngredients"
            smart_params = {
                "ingredients": ingredients,
                "diet": diet,
                "number": 12,
                "ignorePantry": True,
                "apiKey": api_key
            }

            smart_response = requests.get(smart_url, params=smart_params)
            if smart_response.status_code == 200:
                data = smart_response.json()
                smart_results = data.get("results", []) if isinstance(data, dict) else data

            enriched_results = []

            for recipe in smart_results:
                info_url = f"https://api.spoonacular.com/recipes/{recipe['id']}/information"
                info = requests.get(info_url, params={"apiKey": api_key, "includeNutrition": "true"})

                if info.status_code != 200:
                    continue

                data = info.json()

                # Filter 
                if diet and diet.lower() not in [d.lower() for d in data.get("diets", [])]:
                    continue

                recipe["sourceUrl"] = data.get("sourceUrl")
                recipe["image"] = recipe.get("image") or f"https://spoonacular.com/recipeImages/{recipe['id']}-480x360.jpg"

                # These are from findByIngredients response.
                recipe["usedIngredientCount"] = recipe.get("usedIngredientCount", 0)
                recipe["missedIngredientCount"] = recipe.get("missedIngredientCount", 0)
                recipe["missedIngredients"] = recipe.get("missedIngredients", [])

                # Nutrient score.
                nutrients = {
                    n["name"].lower().replace(" ", "_"): n["amount"]
                    for n in data.get("nutrition", {}).get("nutrients", [])
                }

                coverage_points = [
                    nutrients.get(n, 0) / DAILY_TARGETS[n]
                    for n in low_nutrients
                ] if low_nutrients else []

                recipe["nutrient_score"] = round(sum(coverage_points) / len(coverage_points) * 100) if coverage_points else 0

                enriched_results.append(recipe)

            smart_results = sorted(enriched_results, key=lambda r: r["nutrient_score"], reverse=True)[:6]

    for r in results:
        r["image"] = ensure_working_image(r)
    for r in smart_results:
        r["image"] = ensure_working_image(r)

    # Remove any images that are missing or broken.
    results = [r for r in results if r.get("image") and "noimage" not in r["image"]]
    smart_results = [r for r in smart_results if r.get("image") and "noimage" not in r["image"]]

    smart_results = smart_results[:6]
    results = results[:6]

    return render(request, 'tracker/recipe.html', {
        "results": results,
        "smart_results": smart_results,
        "low_nutrients": low_nutrients,
        "query": query,
        "diet": diet,
        "sort": sort,
        "max_time": max_time,
        "diets": [
            "vegetarian", "vegan", "pescetarian",
            "gluten free", "ketogenic", "paleo", "whole30",
        ],
    })


@login_required
def recipe_search(request):
    """
    POST-based recipe search endpoint.
    """
    results = []
    query = ""
    diet = ""
    sort = ""
    max_time = ""

    if request.method == 'POST':
        query = request.POST.get('ingredients')
        diet = request.POST.get('diet')
        sort = request.POST.get('sort')
        max_time = request.POST.get('max_time')

        api_key = os.getenv('SPOONACULAR_API_KEY')
        if api_key and query:
            url = "https://api.spoonacular.com/recipes/complexSearch"
            params = {
                "query": query,
                "diet": diet,
                "sort": sort,
                "maxReadyTime": max_time,
                "number": 1,
                "apiKey": api_key
            }

            params = {k: v for k, v in params.items() if v}

            response = requests.get(url, params=params)
            if response.status_code == 200:
                results = response.json().get("results", [])
            else:
                results = [{"title": "Error fetching recipes"}]

    return render(request, 'tracker/recipe_search.html', {
        'query': query,
        'results': results,
        'diet': diet,
        'sort': sort,
        'max_time': max_time
    })


# ─── Nutrition Summary ──────────────────────────────────────────────────────────
@login_required
def nutrition_summary(request):
    """
    Show nutrient totals of a selected date range,
    today's alerts, and badges for each nutrient.
    """
    preset = request.GET.get("range", "today")

    today = localdate()

    start_str = request.GET.get("start_date")
    end_str   = request.GET.get("end_date")
    start_date = end_date = None
    if start_str and end_str:
        try:
            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date   = datetime.strptime(end_str,   "%Y-%m-%d").date()
        except ValueError:
            start_date = end_date = None

    if not (start_date and end_date):
        if preset == "today":
            start_date = end_date = today
        elif preset == "30":
            start_date = today - timedelta(days=29)
            end_date = today
        elif preset == "month":
            start_date = today.replace(day=1)
            end_date = today
        else:
            start_date = today - timedelta(days=6)
            end_date = today

    logs = FoodLog.objects.filter(date_logged__range=[start_date, end_date])


    supplement_logs = SupplementLog.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    )

    # MOCK - daily nutrient targets.
    DAILY_NUTRIENT_TARGETS = {
        "calories": 2000,
        "protein": 50,
        "fiber": 25,
        "vitamin_c": 75,
        "iron": 18,
        "vitamin_d": 20,
        "vitamin_b12": 2.4,
        "calcium": 1000,
        "magnesium": 400,
        "zinc": 11,
    }

    def sum_nutrients(logs):
        return {
            "calories": sum(log.calories for log in logs),
            "protein": sum(log.protein for log in logs),
            "carbs": sum(log.carbs for log in logs),
            "sugars": sum(log.sugars for log in logs),
            "fiber": sum(log.fiber for log in logs),
            "fat": sum(log.fat for log in logs),
            "saturated_fat": sum(log.saturated_fat for log in logs),
            "cholesterol": sum(log.cholesterol for log in logs),
            "sodium": sum(log.sodium for log in logs),
            "potassium": sum(log.potassium for log in logs),
            "calcium": sum(log.calcium for log in logs),
            "iron": sum(log.iron for log in logs),
            "vitamin_a": sum(log.vitamin_a for log in logs),
            "vitamin_c": sum(log.vitamin_c for log in logs),
            "vitamin_d": sum(log.vitamin_d for log in logs),
            "vitamin_b12": sum(log.vitamin_b12 for log in logs),
            "magnesium": sum(log.magnesium for log in logs),
            "zinc": sum(log.zinc for log in logs),
        }

    totals = sum_nutrients(logs)

    # Calculate today nutrient levels.
    today = localdate()
    today_logs = FoodLog.objects.filter(date_logged=today)
    today_totals = {nutrient: 0 for nutrient in DAILY_NUTRIENT_TARGETS}

    # Add food totals for today.
    for log in today_logs:
        for nutrient in today_totals:
            today_totals[nutrient] += getattr(log, nutrient, 0)

    # Add supplements taken today.
    today_supplements = SupplementLog.objects.filter(user=request.user, date=today)
    for log in today_supplements:
        boosts = SUPPLEMENT_NUTRIENTS.get(log.time_of_day, {})
        for nutrient, amount in boosts.items():
            if nutrient in today_totals:
                today_totals[nutrient] += amount

    # Find today's lows.
    today_lows = [
        nutrient for nutrient, target in DAILY_NUTRIENT_TARGETS.items()
        if today_totals[nutrient] < target * 0.8
    ]

    # Add supplement to totals.
    for log in supplement_logs:
        boosts = SUPPLEMENT_NUTRIENTS.get(log.time_of_day, {})
        for nutrient, amount in boosts.items():
            if nutrient in totals:
                totals[nutrient] += amount


    # Calculate average per day.
    days = (end_date - start_date).days + 1
    # Compute averages for nutrients.
    averages = {
        nutrient: totals.get(nutrient, 0) / days
        for nutrient in DAILY_NUTRIENT_TARGETS
    }

    # Determine badge state for each nutrient (Low vs Good vs High).
    badges = {}
    for nutrient, target in DAILY_NUTRIENT_TARGETS.items():
        total = totals.get(nutrient)
        if total is None:
            continue
        if total < target * 0.8:
            badges[nutrient] = "Low"
        elif total > target * 1.2:
            badges[nutrient] = "High"
        else:
            badges[nutrient] = "Good"

    # Flag deficiencies.
    deficient_nutrients = {}
    for nutrient, target in DAILY_NUTRIENT_TARGETS.items():
        avg = averages[nutrient]
        if avg < target * 0.8:
            deficient_nutrients[nutrient] = {
                "average": round(avg, 1),
                "target": target
            }

    context = {
        "totals": totals,
        "nutrients": {
            "calories": "Calories",
            "protein": "Protein (g)",
            "carbs": "Carbohydrates (g)",
            "sugars": "Sugars (g)",
            "fiber": "Fiber (g)",
            "fat": "Fat (g)",
            "saturated_fat": "Saturated Fat (g)",
            "cholesterol": "Cholesterol (mg)",
            "sodium": "Sodium (mg)",
            "potassium": "Potassium (mg)",
            "calcium": "Calcium (mg)",
            "iron": "Iron (mg)",
            "vitamin_a": "Vitamin A (mcg)",
            "vitamin_c": "Vitamin C (mg)",
            "vitamin_d": "Vitamin D (mcg)",
            "vitamin_b12": "Vitamin B12 (mcg)",
            "magnesium": "Magnesium (mg)",
            "zinc": "Zinc (mg)",
        },

        "selected_range": preset,
        "start_date": start_date,
        "end_date": end_date,
        "deficient_nutrients": deficient_nutrients,  # For totals table.
        "today_lows": today_lows,                    # For top alert.
        "badges": badges,                            # For low/good/high labels.
        "today_totals": today_totals,                # For today's card details.
        "DAILY_TARGETS": DAILY_NUTRIENT_TARGETS,     # So template can show goal per nutrient.

    }

    return render(request, "tracker/nutrition_summary.html", context)


# ─── AJAX / API endpoints ──────────────────────────────────────────────────────
@login_required
def ingredient_autocomplete(request):
    """Return JSON list of ingredient suggestions from Spoonacular."""
    query = request.GET.get("q")
    if not query:
        return JsonResponse([], safe=False)

    api_key = settings.SPOONACULAR_API_KEY
    url = "https://api.spoonacular.com/food/ingredients/autocomplete"
    params = {
        "query": query,
        "number": 5,
        "metaInformation": True,
        "apiKey": api_key
    }

    response = requests.get(url, params=params)
    results = response.json() if response.status_code == 200 else []

    suggestions = [
        {"name": item["name"], "id": item["id"]}
        for item in results
    ]

    return JsonResponse(suggestions, safe=False)


@login_required
def ingredient_nutrition(request):
    """Return JSON nutrition info for a given ingredient id."""
    from django.http import JsonResponse

    ing_id = request.GET.get("id")
    amount = request.GET.get("amount")
    unit = request.GET.get("unit")

    if not (ing_id and amount and unit):
        return JsonResponse({}, status=400)

    api_key = settings.SPOONACULAR_API_KEY
    url = f"https://api.spoonacular.com/food/ingredients/{ing_id}/information"
    params = {
        "amount": amount,
        "unit": unit,
        "apiKey": api_key
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return JsonResponse({}, status=500)

    info = response.json()
    nutrition = {n['name'].lower().replace(" ", "_"): n['amount'] for n in info.get("nutrition", {}).get("nutrients", [])}

    mapped = {
        "calories": nutrition.get("calories", 0),
        "protein": nutrition.get("protein", 0),
        "carbs": nutrition.get("carbohydrates", 0),
        "sugars": nutrition.get("sugar", 0),
        "fiber": nutrition.get("fiber", 0),
        "fat": nutrition.get("fat", 0),
        "saturated_fat": nutrition.get("saturated_fat", 0),
        "cholesterol": nutrition.get("cholesterol", 0),
        "sodium": nutrition.get("sodium", 0),
        "potassium": nutrition.get("potassium", 0),
        "calcium": nutrition.get("calcium", 0),
        "iron": nutrition.get("iron", 0),
        "vitamin_c": nutrition.get("vitamin_c", 0),
        "vitamin_d": nutrition.get("vitamin_d", 0),
        "vitamin_b12": nutrition.get("vitamin_b12", 0),
        "magnesium": nutrition.get("magnesium", 0),
        "zinc": nutrition.get("zinc", 0),
        "vitamin_a": nutrition.get("vitamin_a", 0),
    }

    return JsonResponse(mapped)

def fetch_recipe_details(recipe_id):
    """Helper to fetch recipe metadata from Spoonacular /information."""
    api_key = settings.SPOONACULAR_API_KEY
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    resp = requests.get(url, params={"apiKey": api_key})
    if resp.status_code == 200:
        data = resp.json()
        return {
            "title": data.get("title", "Unknown"),
            "image": data.get("image"),
            "source_url": data.get("sourceUrl"),
        }
    return {"title": "Unknown", "image": "", "source_url": ""}


@login_required
def save_recipe(request, recipe_id):
    """
    Save a recipe to the user’s SavedRecipe list.
    Returns JSON if AJAX...if not, redirect.
    """
    details = fetch_recipe_details(recipe_id)

    SavedRecipe.objects.get_or_create(
        user=request.user,
        spoonacular_id=recipe_id,
        defaults={
            "title": details["title"],
            "image_url": details["image"],
            "source_url": details["source_url"],
        }
    )

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"status": "ok"})

    return redirect("saved_recipes")


@login_required
def saved_recipes(request):
    """Display the current user’s SavedRecipe entries."""
    recipes = SavedRecipe.objects.filter(user=request.user).order_by("-saved_at")
    return render(request, "tracker/saved_recipes.html", {"recipes": recipes})


@login_required
@require_POST
def delete_saved_recipe(request, recipe_id):
    """Delete a SavedRecipe and redirect back to the list."""
    saved = get_object_or_404(
        SavedRecipe, 
        id=recipe_id, 
        user=request.user
    )
    saved.delete()
    return redirect('saved_recipes')