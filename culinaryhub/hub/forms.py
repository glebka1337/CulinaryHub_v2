from django import forms
from django.core.exceptions import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import *
from django.forms import modelformset_factory, BaseModelFormSet

from .validators import *
from .models import *


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(label='Ваш псевдоним', widget=forms.TextInput(attrs={'class': 'form-control m-2'}, ),
                               validators=[validate_unique_username,
                                           MaxLengthValidator(100,
                                                              message="Слишком длинный псевдоним, максимум 100 символов"),
                                           MinLengthValidator(5,
                                                              message="Слишком короткий псевдоним, минимум 5 символов"),
                                           ]
                               )
    email = forms.EmailField(label='Ваша почта', widget=forms.EmailInput(attrs={'class': 'form-control m-2'}),
                             validators=[validate_unique_email])
    first_name = forms.CharField(label='Ваше имя', widget=forms.TextInput(attrs={'class': 'form-control m-2'}))
    last_name = forms.CharField(label='Ваша фамилия', widget=forms.TextInput(attrs={'class': 'form-control m-2'}))
    password1 = forms.CharField(label='Придумайте надёжный пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control m-2'}),
                                validators=[validate_password],
                                help_text='Пароль должен содержать буквы, цифры и специальные символы')
    password2 = forms.CharField(label='Повторите пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control m-2'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
        }

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким почтовым адресом уже существует')
        if User.objects.filter(first_name=first_name, last_name=last_name).exists():
            raise ValidationError('Пользователь с таким именем и фамилией уже существует')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            raise ValidationError('Пароли не совпадают, попробуйте ещё раз')
        return cleaned_data


class UserLoginForm(forms.Form):
    username = forms.CharField(label='Ваш псевдоним', widget=forms.TextInput(attrs={'class': 'form-control m-2'}),
                               validators=[
                                   MinLengthValidator(5, message="Слишком короткий псевдоним, минимум 5 символов"),
                                   MaxLengthValidator(100, message="Слишком длинный псевдоним, максимум 100 символов")])
    password = forms.CharField(label='Ваш пароль', widget=forms.PasswordInput(attrs={'class': 'form-control m-2'}),
                               validators=[validate_password])

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if not User.objects.filter(username=username).exists():
            self.add_error('username', 'Пользователь с таким именем не существует')
            return cleaned_data
        user = User.objects.get(username=username)
        if user and not user.check_password(password):
            self.add_error('password', 'Неправильный пароль')
            return cleaned_data
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
        labels = {
            'bio': 'Изменить описание',
            'avatar': 'Изменить аватар',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
            'avatar': forms.FileInput(attrs={'class': 'form-control form-control-sm'}),
        }


class RecipeForm(forms.ModelForm):
    preparation_time = forms.TimeField(label='Время приготовления',
                                       widget=forms.TimeInput(
                                           attrs={'class': 'form-control form-control-sm mx-2 p-2 mt-2',
                                                  'type': 'time'}),
                                       initial="05:00")
    cooking_time = forms.TimeField(label='Время приготовления',
                                   widget=forms.TimeInput(
                                       attrs={'class': 'form-control form-control-sm mx-2 p-2 mt-2', 'type': 'time'}),
                                   initial="05:00")
    ingredient_count = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm mx-2 p-2 mt-2'}),
        required=True,
        initial=1,
        validators=[MinValueValidator(1)], label="Количество ингредиентов")
    step_count = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm mx-2 p-2 mt-2'}), required=True,
        initial=1,
        validators=[MinValueValidator(1)],
        label="Количество шагов")

    class Meta:
        model = Recipe
        fields = ['title', 'description',
                  'category',
                  'preparation_time', 'cooking_time',
                  'difficulty', 'has_calories', 'image', 'portions']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 2}),
            'category': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 0}),
            'proteins': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 0}),
            'fats': forms.NumberInput(attrs={'class': 'form-control form-control-sm', 'min': 0}),
            'carbohydrates': forms.NumberInput(attrs={'class': 'form-control form-control-sm mx-2 p-2 mt-2'}),
            'difficulty': forms.Select(attrs={'class': 'form-control form-select-sm', 'initial': 1}),
            'has_calories': forms.CheckboxInput(attrs={'class': 'form-check-input p-2 mt-2'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file p-2 mt-2'}),
        }
        labels = {
            "has_calories": 'Нужно ли учитывать калории?'
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        if Recipe.objects.filter(title=title).exists():
            self.add_error('title', 'Рецепт с таким названием уже существует')
            return cleaned_data
        return cleaned_data


class RecipeImageForm(forms.Form):
    main_image = forms.ImageField(label='Окончательное фото рецепта',
                                  widget=forms.FileInput(attrs={'class': 'form-control-file'}),
                                  validators=[FileExtensionValidator(['png', 'jpg', 'jpeg']), validate_image_size],
                                  required=True)


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['step_number', 'step', 'image']
        widgets = {
            'step_number': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm p-2 mt-2', 'min': 1, 'initial': 1, 'max': 10,
                       'disabled': True}),
            'step': forms.Textarea(
                attrs={'class': 'form-control form-control-sm p-2 mt-2', 'rows': 2, 'min': 6, 'max': 500,
                       'required': True}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'step_number': 'Номер шага',
            'image': 'Изображение',
        }


class IngredientForm(forms.Form):
    UNIT_CHOICES = (
        ('g', 'г'),
        ('tsp', 'ч.л.'),
        ('tbsp', 'ст.л.'),
    )

    name = forms.CharField(label='Название ингредиента', widget=forms.TextInput(
        attrs={'class': 'form-control form-control-sm', 'min': 6, 'max': 50, 'required': True}),
                           validators=[MinLengthValidator(3,
                                                          message="Слишком короткое название ингредиента, минимум 3 символов"),
                                       MaxLengthValidator(50,
                                                          message="Слишком длинное название ингредиента, максимум 50 символов"),
                                       ], required=True)
    quantity = forms.CharField(label='Количество', widget=forms.TextInput(
        attrs={'class': 'form-control form-control-sm', 'min': 0, 'required': True}),
                               validators=[integer_validator, ], required=True)
    unit = forms.ChoiceField(label='Единица измерения', choices=UNIT_CHOICES,
                             widget=forms.Select(attrs={'class': 'form-control form-control-sm form-select-sm'}))

class ProductSearchForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'category': forms.Select(attrs={'class': 'form-control form-control-sm'}),
        }
        labels = {
            'name': 'Продукт',
            'category': 'Категория',
        }

class ProductSelectForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.none(), label='Выберите продукт')
    weight = forms.IntegerField(label='Вес', widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
                              validators=[MinLengthValidator(0, message="Вес не может быть отрицательным")],
                              required=True)
    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super().__init__(*args, **kwargs)
        if queryset:
            self.fields['product'].queryset = queryset

class AdditionalInfoForm(forms.Form):
    after_weight = forms.IntegerField(label='Вес после приготовления', widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
                              validators=[MinLengthValidator(0, message="Вес не может быть отрицательным")],
                              required=False,
                              help_text='Вес в граммах после приготовления рецепта (если рецепт не уменьшается, оставьте поле пустым)')
    portions = forms.IntegerField(label='Количество порций', widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
                              validators=[MinLengthValidator(0, message="Количество порций не может быть отрицательным")],
                              required=False, help_text='Количество порций (Если не указано, расчёт калорийности будет на 100 грамм рецепта)')
