from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.core import serializers
from django.forms import formset_factory
from django.http import HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import *

from .forms import *


class RecipeListView(ListView):
    model = Recipe
    view_name = "category_recipes"
    template_name = "hub/index.html"
    context_object_name = "recipes"
    ordering = ["title"]
    paginate_by = 6

    def get_queryset(self):
        category_slug = self.kwargs.get("category_slug", None)
        if category_slug is not None:
            return Recipe.objects.filter(category__slug=category_slug, is_published=True)
        else:
            category_slug = self.request.GET.get("category_slug", None)
            if category_slug is not None:
                return Recipe.objects.filter(category__slug=category_slug, is_published=True)
        return Recipe.objects.filter(is_published=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        category_slug = self.kwargs.get("category_slug", None)
        if category_slug is not None:
            context["title"] = Category.objects.get(slug=category_slug).name
            context["category_name"] = Category.objects.get(slug=category_slug).name
        else:
            category_slug = self.request.GET.get("category_slug", None)
            if category_slug is not None:
                context["title"] = Category.objects.get(slug=category_slug).name
                context["category_name"] = Category.objects.get(slug=category_slug).name
        return context


@login_required(login_url="login")
@require_POST
def add_favorite(request):
    if request.method == "POST":
        recipe_to_add = Recipe.objects.get(id=request.POST.get("recipe_id"))
        new_favorite = Favorite(recipe=recipe_to_add, user=request.user)
        new_favorite.save()
        return redirect("recipe_view", category_slug=recipe_to_add.category.slug, recipe_slug=recipe_to_add.slug)


@login_required(login_url="login")
@require_POST
def remove_favorite(request: HttpRequest):
    if request.method == "POST":
        recipe_to_remove = Recipe.objects.get(id=request.POST.get("recipe_id"))
        Favorite.objects.filter(recipe=recipe_to_remove, user=request.user).delete()
        return redirect("recipe_view", category_slug=recipe_to_remove.category.slug, recipe_slug=recipe_to_remove.slug)


def register(request: HttpRequest):
    title = "Регистрация"
    description = "Здесь можно зарегистрироваться"
    form = UserRegistrationForm()
    context = {
        "title": title,
        "description": description,
        "form": form,
    }
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Вы успешно зарегистрировались, войдите в свою учетную запись, что бы открыть полный функционал сайта",
                extra_tags="alert-success mt-2",
            )
            return redirect("login")
        for error in list(form.non_field_errors()):
            messages.error(request, error, extra_tags="alert-danger mt-2")
        for error in list(form.errors.values()):
            for e in error:
                messages.error(request, e, extra_tags="alert-danger mt-2")
        context["form"] = form
    return render(request, "hub/register.html", context=context)


def login_user(request: HttpRequest):
    next_url = request.GET.get('next', request.POST.get('next', ''))

    if next_url and next_url.strip():
        messages.info(request, 'Войдите в свою учетную запись, чтобы открыть полный функционал сайта')
    form = UserLoginForm()
    context = {
        "title": "Вход в профиль",
        "form": form,
        "description": "Войдите в свою учетную запись",
    }
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user: User = authenticate(
                request, username=cd["username"], password=cd["password"]
            )
            if user and user.is_active:
                login(request, user)
                messages.success(
                    request,
                    "Вы успешно вошли в свою учетную запись",
                    extra_tags="alert-success mt-2",
                )
                return redirect("profile")
        context["form"] = form
    return render(request, "hub/login.html", context=context)


@login_required(login_url="login")
def profile(request: HttpRequest):
    profile_form = UserProfileForm()
    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            user = request.user
            profile, created = Profile.objects.get_or_create(user=user)
            profile.bio = profile_form.cleaned_data["bio"]
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            profile.save()
            user.save()
            messages.success(
                request, "Ваш профиль обновлен", extra_tags="alert-success mt-2"
            )
            return redirect("profile")

    context = {
        "title": f"Добро пожаловать, {request.user.username} !!!",
        "description": "Ваш профиль, здесь вы можете редактировать свой профиль, добавлять рецепты и просматривать их",
        "profile_form": profile_form,
        "favorite": request.user.favorite.all(),
    }
    return render(request, "hub/profile.html", context=context)


def logout_user(request):
    request.session.flush()
    logout(request)
    messages.success(
        request, "Вы вышли из своей учетной записи", extra_tags="alert-success mt-2"
    )
    return redirect("index")


def user_profile_view(request, profile_name_slug):
    user_profile = get_object_or_404(Profile, profile_name_slug=profile_name_slug)
    user = user_profile.user
    context = {"user": user, "viewer": request.user}
    return render(request, "hub/user_profile.html", context)


@login_required(login_url="login")
@require_POST
def add_subscriber(request):
    if request.method == "POST":
        subscriber = request.user
        author = User.objects.get(id=request.POST.get("author_id"))
        subscription = Subscription(subscriber=subscriber, subscribed_to=author)
        subscription.save()
        return redirect("user_profile_view", profile_name_slug=author.profile.profile_name_slug)


@login_required(login_url="login")
@require_POST
def remove_subscriber(request):
    if request.method == "POST":
        subscriber = request.user
        author = User.objects.get(id=request.POST.get("author_id"))
        subscription = Subscription.objects.get(subscriber=subscriber, subscribed_to=author)
        subscription.delete()
        return redirect("user_profile_view", profile_name_slug=author.profile.profile_name_slug)


class RecipeFormView(LoginRequiredMixin, FormView):
    form_class = RecipeForm
    template_name = "hub/add_recipe.html"
    login_url = "/users/login/"
    success_url = "/add_ingredients/"

    def get(self, request: HttpRequest, *args, **kwargs):
        if request.session.get("recipe_title") is not None:
            title = request.session.get("recipe_title")
            recipe = Recipe.objects.filter(title=title)
            self.form_class = RecipeForm(instance=recipe)
        else:
            self.form_class = RecipeForm()
        return render(
            request,
            self.template_name,
            dict(form=self.form_class),
        )

    def form_valid(self, form: RecipeForm):
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.image = form.cleaned_data["image"]
            recipe.author = self.request.user
            recipe.save()
            self.request.session["recipe_title"] = form.cleaned_data["title"]
            self.request.session["ingredient_count"] = form.cleaned_data["ingredient_count"]
            self.request.session["step_count"] = form.cleaned_data["step_count"]
            self.request.session["has_calories"] = form.cleaned_data["has_calories"]
            return redirect(self.success_url)
        else:
            self.form_class = RecipeForm(
                data=self.request.POST, files=self.request.FILES
            )
            return render(request=self.request,
                          template_name=self.template_name,
                          context=dict(recipe_form=form))


@login_required(login_url="/users/login/")
def add_ingredients(request: HttpRequest):
    ingredient_form_set = formset_factory(IngredientForm, extra=1)
    if request.session.get("ingredient_count") is not None:
        ingredient_form_set = formset_factory(IngredientForm, extra=request.session.get("ingredient_count"))
    if request.method == "POST":
        ingredient_form_set = ingredient_form_set(request.POST)
        if ingredient_form_set.is_valid():
            ingredients = [Ingredient(name=form.cleaned_data["name"],
                                      quantity=form.cleaned_data["quantity"],
                                      unit=form.cleaned_data["unit"])
                           for form in ingredient_form_set]
            request.session["ingredients"] = serializers.serialize("json", ingredients)
            messages.success(
                request=request,
                message="Все ингредиенты добавлены!",
                extra_tags="alert-success mt-2",
            )
            return redirect("add_steps")
    return render(request, "hub/add_ingredients.html", context=dict(formset=ingredient_form_set))


@login_required(login_url="/users/login/")
def add_steps(request: HttpRequest):
    step_form_set = formset_factory(StepForm, extra=0)
    if request.session.get("step_count") is not None:
        step_form_set = formset_factory(StepForm, extra=request.session.get("step_count"))
    else:
        messages.error(
            request=request,
            message="Нужно добавить хотя бы один шаг!",
            extra_tags="alert-danger mt-2",
        )
        return redirect("add_recipe")
    if request.method == "POST":
        step_form_set = step_form_set(request.POST, files=request.FILES)
        if step_form_set.is_valid():
            title = request.session.get("recipe_title")
            recipe = Recipe.objects.get(title=title)
            for step_form in enumerate(step_form_set, start=1):
                step = Step(
                    step_number=step_form[0],
                    step=step_form[1].cleaned_data["step"],
                    image=step_form[1].cleaned_data["image"],
                    recipe=recipe
                )
                step.save()
            ingredients = request.session.get("ingredients")
            ingredients = serializers.deserialize('json', ingredients)
            ingredients = [ingredient.object for ingredient in ingredients]
            for ingredient in ingredients:
                ingredient.recipe = recipe
                ingredient.save()
            messages.success(
                request=request,
                message="Все шаги добавлены!",
                extra_tags="alert-success mt-2",
            )
            return render(request, "hub/add_steps.html", context=dict(formset=step_form_set))

    return render(request, "hub/add_steps.html", context=dict(formset=step_form_set))


def recipe_view(request, category_slug, recipe_slug):
    recipe = get_object_or_404(Recipe, slug=recipe_slug, category__slug=category_slug)
    return render(request, "hub/recipe.html", context=dict(recipe=recipe))


@login_required(login_url="/users/login/")
def product_search(request):
    search_form = ProductSearchForm()
    select_form = None
    products = None
    additional_info_form = AdditionalInfoForm()
    selected_products = request.session.get("selected_products", [])
    if request.method == "POST":
        search_form = ProductSearchForm(request.POST)
        if search_form.is_valid():
            product_name = search_form.cleaned_data["name"]
            product_category = search_form.cleaned_data["category"]
            cat_obj = ProductCategory.objects.get(name=product_category)
            if cat_obj.name == "Все":
                products = Product.objects.filter(name__icontains=product_name)
            else:
                products = Product.objects.filter(category=cat_obj, name__icontains=product_name)
            product_select_form = ProductSelectForm(queryset=products)
            select_form = product_select_form
            products = products

    if request.method == "POST" and "product" in request.POST:
        selected_prod = request.POST.get("product")
        weight = request.POST.get("weight")
        selected_products.append({"name": selected_prod, "weight": int(weight)})
        request.session["selected_products"] = selected_products
    context = {
        'search_form': search_form,
        'select_form': select_form,
        'selected_products': selected_products,
        'additional_info_form': additional_info_form,
    }
    return render(request, "hub/product_search.html", context=context)


@login_required(login_url="/users/login/")
@require_POST
def delete_product(request):
    if request.method == "POST":
        product_name = request.POST.get("product")
        product_name = product_name.replace("_", " ")
        selected_products = request.session.get("selected_products", [])
        selected_products = [d for d in selected_products if d.get("name") != product_name]
        request.session["selected_products"] = selected_products
        return redirect("product_search")


def unpack_products_nutrition(selected_products: list, after_weight: int, portions: int):
    total_weight = sum([d.get("weight") for d in selected_products])
    '''
    calculating calories for a given product
    for a certain weight
    total nutrients dict is returned
    '''
    total_nutrients = {
        "kcal": 0,
        "p": 0,
        "f": 0,
        "c": 0
    }
    prod_data: dict
    for prod_data in selected_products:
        product_obj = Product.objects.get(name=prod_data["name"])
        nutrients: dict = product_obj.kcal_per_grams(grams=prod_data["weight"])
        total_nutrients["kcal"] += nutrients["kcal"]
        total_nutrients["p"] += nutrients["p"]
        total_nutrients["f"] += nutrients["f"]
        total_nutrients["c"] += nutrients["c"]
    '''
    having a weight after cooking,
    we can calculate shrinkage
    '''
    if after_weight > 0:
        kcal_per_gram_recipe = total_nutrients["kcal"] / after_weight
        p_per_gram_recipe = total_nutrients["p"] / after_weight
        f_per_gram_recipe = total_nutrients["f"] / after_weight
        c_per_gram_recipe = total_nutrients["c"] / after_weight
    else:
        kcal_per_gram_recipe = total_nutrients["kcal"] / total_weight
        p_per_gram_recipe = total_nutrients["p"] / total_weight
        f_per_gram_recipe = total_nutrients["f"] / total_weight
        c_per_gram_recipe = total_nutrients["c"] / total_weight

    nutrients_per_100 = {
        "kcal": round(kcal_per_gram_recipe * 100, 2),
        "p": round(p_per_gram_recipe * 100, 2),
        "f": round(f_per_gram_recipe * 100, 2),
        "c": round(c_per_gram_recipe * 100, 2)
    }
    if portions > 1:
        calories_per_portion = {
            "kcal": round(total_nutrients["kcal"] / portions, 2),
            "p": round(total_nutrients["p"] / portions, 2),
            "f": round(total_nutrients["f"] / portions, 2),
            "c": round(total_nutrients["c"] / portions, 2)
        }
        return [calories_per_portion, nutrients_per_100]
    return [None, nutrients_per_100]


@login_required(login_url="/users/login/")
def calculate_calories(request: HttpRequest):
    if request.method == "POST":
        selected_products = request.session.get("selected_products", [])
        portions = request.POST.get("portions")
        after_weight = request.POST.get("after_weight", 0)
        if portions is None or portions == "":
            portions = 1
        else:
            portions = int(portions)
        if request.POST.get("after_weight") != "":
            after_weight = request.POST.get('after_weight')
        else:
            after_weight = 0
        recipe_calories = {
            "kcal": 0,
            "p": 0,
            "f": 0,
            "c": 0
        }
        recipe_nutrients = unpack_products_nutrition(selected_products, after_weight, portions)
        context = {
            "recipe_nutrients": recipe_nutrients,
            "portions": portions,
            "after_weight": after_weight,
        }
        del request.session["selected_products"]
        return render(request, "hub/recipe_nutrients.html", context=context)
    return redirect("product_search")


class PasswordChangeView(PasswordChangeView):
    template_name = "hub/password_change_form.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("profile")


def recipe_search(request):
    recipes = Recipe.objects.all()
    return render(request, "hub/recipe_search.html", context=dict(recipes=recipes))


def page_not_found(request, exception):
    return render(request, "hub/404.html")
