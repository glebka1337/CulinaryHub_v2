from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from django.template.loader import render_to_string

from .forms import *

"""
Check if the username provided in the request exists in the User model.
If the request is from the register page, check if the username already exists in the database.
If the request is from the login page, check if the username exists in the database.
Return an appropriate HttpResponse based on the check results.
"""


def check_username(request: HttpRequest):
    if (
            request.POST.get("password1") is not None
            and request.POST.get("password2") is not None
    ):
        """
        means that form is sent from register page
        """
        if User.objects.filter(username=request.POST.get("username")).exists():
            response = render_to_string(
                "hub/partials/messages.html",
                {"message": "Пользователь с таким именем уже существует"},
            )
            return HttpResponse(response)
        else:
            return HttpResponse("")
    elif request.POST.get("password") is not None:
        """
        means that form is sent from login page
        """
        if not User.objects.filter(username=request.POST.get("username")).exists():
            message = "Пользователя с таким именем не существует"
            response = render_to_string(
                "hub/partials/messages.html", {"message": message}
            )
            return HttpResponse(response)
        else:
            return HttpResponse("")


def validate_password_htmx(value):
    if len(value) < 8:
        return "Пароль должен содержать не менее 8 символов"
    if not any(char.isdigit() for char in value):
        return "Пароль должен содержать хотя бы одну цифру"
    if not any(char.islower() for char in value):
        return "Пароль должен содержать хотя бы одну строчную букву"
    if not any(char.isupper() for char in value):
        return "Пароль должен содержать хотя бы одну заглавную букву"
    if not any(char in "!@#$%^&*()_+-=" for char in value):
        return "Пароль должен содержать хотя бы один из следующих символов: !@#$%^&*()_+-="
    return True


def validate_password(request: HttpRequest):
    if request.POST.get("password1") != "":
        if validate_password_htmx(request.POST.get("password1")) is not True:
            message = validate_password_htmx(request.POST.get("password1"))
            response = render_to_string(
                "hub/partials/messages.html", {"message": message}
            )
            return HttpResponse(response)


"""
Perform a search for products based on the provided name parameter in the request. If the name parameter is empty, return a HttpResponse with a button HTML. If products are found based on the search query, render a template with the product search results and return it as a HttpResponse. Limit the results to a maximum of 3 products.

Parameters:
- request (HttpRequest): The HTTP request object containing the search parameters.

Returns:
- HttpResponse: A response containing either the search results or a button HTML based on the search query.

"""


def product_search_htmx(request: HttpRequest):
    button_html = '''
                <div class="list-group mt-2">
                 <button type="button" class="list-group-item list-group-item-action" disabled>Здесь будут результаты поиска</button>
                </div>
                '''
    params = next(request.GET.items())
    field_auto_name = params[0]
    name = params[1]
    if name == '':
        return HttpResponse(button_html)
    product_founded = Product.objects.filter(name__contains=name)[:3]
    if len(product_founded) > 0:
        response = render_to_string(
            template_name="hub/partials/product_search_result.html",
            context=dict(
                products=[p.name for p in product_founded],
                field_auto_name=field_auto_name
            ),
        )
        return HttpResponse(response)
    else:
        return HttpResponse(button_html)


def get_search(request: HttpRequest):
    field_auto_name = request.GET.get("field_auto_name")
    product_name = request.GET.get("value")
    rendered = render_to_string(
        template_name="hub/partials/form_field.html",
        context=dict(
            name=product_name,
            field_auto_name=field_auto_name
        ),
    )
    return HttpResponse(rendered)


def get_recipe_search(request: HttpRequest):
    recipe_name = request.GET.get("recipe")
    recipe_objects = Recipe.objects.filter(title__contains=recipe_name)
    return render(request, "hub/partials/recipe_search_result.html", context=dict(recipes=recipe_objects))
