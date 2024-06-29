import transliterate
from django.core.validators import *
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from transliterate import slugify
from transliterate.utils import translit
from .validators import *
from .validators import validate_russian_input


def avatar_upload(instance, filename):
    return f"users_avatars/{filename}"


class Profile(models.Model):
    avatar = models.ImageField(
        upload_to=avatar_upload,
        default=None,
        verbose_name="Аватар",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "png"],
                message="Неправильное расширение изображения, допустимые расширения: jpg, png",
            )
        ],
    )
    user = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="profile",
    )
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name="О себе",
        validators=[
            MinLengthValidator(
                20, message="Слишком короткое описание, минимум 20 символов"
            ),
            MaxLengthValidator(
                200, message="Слишком длинное описание, максимум 1000 символов"
            ),
        ],
    )
    profile_name_slug = models.CharField(max_length=200, verbose_name="Никнейм", unique=True, null=True)

    def save(self, *args, **kwargs):
        self.profile_name_slug = slugify(self.user.username)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite')
    recipe = models.ForeignKey("Recipe", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} - {self.recipe.title}'


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    subscribed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')

    class Meta:
        unique_together = ('subscriber', 'subscribed_to')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f"Пользователь {self.subscriber.username} подписан на {self.subscribed_to.username}"


"""
A class representing a product category.

Attributes:
    name (CharField): The name of the product category.

Meta:
    verbose_name (str): A human-readable name for the model.
    verbose_name_plural (str): A human-readable plural name for the model.

Methods:
    __str__: Returns the name of the product category.

"""


class ProductCategory(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[
            MinLengthValidator(
                3, message="Слишком короткое название, минимум 5 символов"
            ),
            MaxLengthValidator(
                100, message="Слишком длинное название, максимум 100 символов"
            ),
        ],
        verbose_name="Название категории",
    )

    class Meta:
        verbose_name = "Категория продукта"
        verbose_name_plural = "Категории продуктов"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[
            MinLengthValidator(
                5, message="Слишком короткое название, минимум 5 символов"
            ),
            MaxLengthValidator(
                100, message="Слишком длинное название, максимум 100 символов"
            ),
        ],
        verbose_name="Название категории",
    )
    slug = models.SlugField(unique=True, max_length=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(viewname="category_recipes", kwargs={"category_slug": self.slug})

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        transliterated_name = translit(self.name, language_code="ru", reversed=True)
        self.slug = slugify(transliterated_name, allow_unicode=True)
        super().save(force_insert, force_update, using, update_fields)

    @classmethod
    def get_default_category(cls):
        default_category, created = Category.objects.get_or_create(name="Другое")
        return default_category


"""
A class representing a product.

Attributes:
    name (CharField): The name of the product.
    kcal (FloatField): The amount of calories in the product.
    p (FloatField): The amount of proteins in the product.
    f (FloatField): The amount of fats in the product.
    c (FloatField): The amount of carbohydrates in the product.
    category (ForeignKey): The category to which the product belongs.

Meta:
    verbose_name (str): A human-readable name for the model.
    verbose_name_plural (str): A human-readable plural name for the model.
    unique_together (tuple): Specifies that the combination of 'name' and 'category' should be unique.

Methods:
    __str__: Returns the name of the product.
    re_count: Recalculates the total calories based on proteins, fats, and carbohydrates.
    save: Overrides the save method to recalculate total calories before saving.
    check_kcal: Checks if the total calories are non-negative.
    kcal_per_grams: Calculates the nutritional values per given grams of the product.
    kcal_count: Static method to calculate nutritional values per given grams for any product.
    check_nutrients: Static method to check and recalculate nutritional values.
    units_to_grams: Static method to convert different units to grams.

"""


class Product(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="Название продукта",
        validators=[
            MinLengthValidator(
                3, message="Слишком короткое название, минимум 3 символа"
            ),
            MaxLengthValidator(
                150, message="Слишком длинное название, максимум 100 символов"
            ),
            validate_russian_input,
        ],
        blank=False,
        null=False,
        primary_key=True,
    )
    kcal = models.FloatField(
        verbose_name="Калории",
        default=0,
        blank=False,
        null=False,
        validators=[
            MinValueValidator(0, message="Калории не могут быть отрицательными")
        ],
    )
    p = models.FloatField(
        verbose_name="Белки",
        default=0,
        blank=False,
        null=False,
        validators=[MinValueValidator(0, message="Белки не могут быть отрицательными")],
    )
    f = models.FloatField(
        verbose_name="Жиры",
        default=0,
        blank=False,
        null=False,
        validators=[MinValueValidator(0, message="Жиры не могут быть отрицательными")],
    )
    c = models.FloatField(
        verbose_name="Углеводы",
        default=0,
        blank=False,
        null=False,
        validators=[
            MinValueValidator(0, message="Углеводы не могут быть отрицательными")
        ],
    )
    category = models.ForeignKey(
        ProductCategory, on_delete=models.CASCADE, related_name="products", null=True
    )

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        unique_together = ("name", "category")

    def __str__(self):
        return self.name

    def re_count(self):
        self.kcal = self.p * 4 + self.f * 9 + self.c * 4

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.re_count()
        super().save(force_insert, force_update, using, update_fields)

    def check_kcal(self) -> bool:
        self.kcal = self.p * 4 + self.f * 9 + self.c * 4
        if self.kcal < 0:
            return False
        return True

    def kcal_per_grams(self, grams: int) -> dict:
        kcal_one_gram = round(self.kcal / 100, 2)
        p_one_gram = round(self.p / 100, 2)
        f_one_gram = round(self.f / 100, 2)
        c_one_gramm = round(self.c / 100, 2)
        counted_nutrition = {
            "kcal": kcal_one_gram * grams,
            "p": p_one_gram * grams,
            "f": f_one_gram * grams,
            "c": c_one_gramm * grams,
            "weight": grams,
        }
        return counted_nutrition

    @staticmethod
    def kcal_count(grams: int | float, kcal, p, f, c) -> dict:
        kcal_per_g = round(kcal / 100, 2)
        p_per_g = round(p / 100, 2)
        f_per_g = round(f / 100, 2)
        c_per_g = round(c / 100, 2)
        counted_nutrition = {
            "kcal": kcal_per_g * grams,
            "p": p_per_g * grams,
            "f": f_per_g * grams,
            "c": c_per_g * grams,
            "weight": grams,
        }
        return counted_nutrition

    @staticmethod
    def check_nutrients(kcal, p, f, c) -> dict:
        nutrients = {"kcal": kcal, "p": p, "f": f, "c": c}
        kcal = p * 4 + f * 9 + c * 4
        nutrients["kcal"] = kcal
        return nutrients

    @staticmethod
    def units_to_grams(quantity: int | float, unit: str) -> float | int:
        grams = quantity
        if unit == "g":
            grams = quantity
        elif unit == "tsp":
            grams = quantity * 4.2
        elif unit == "tbsp":
            grams = quantity * 14
        return grams

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


def custom_recipes_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    return "recipes/{category}/{title}/main.{ext}".format(
        category=instance.category.slug, title=instance.slug, ext=ext
    )


class Recipe(models.Model):
    title = models.CharField(
        unique=True,
        max_length=200,
        validators=[
            MinLengthValidator(
                5, message="Слишком короткое название, минимум 5 символов"
            ),
            MaxLengthValidator(
                100, message="Слишком длинное название, максимум 100 символов"
            ),
            validate_chars_only,
            validate_russian_input,
        ],
        verbose_name="Название рецепта",
    )
    description = models.TextField(
        unique=True,
        validators=[
            MinLengthValidator(
                10, message="Слишком короткое описание, минимум 10 символов"
            ),
            MaxLengthValidator(
                500, message="Слишком длинное описание, максимум 200 символов"
            ),
        ],
        verbose_name="Короткое описание рецепта",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name="Категория",
        related_name="recipes",
    )
    image = models.ImageField(
        upload_to=custom_recipes_upload_to,
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "png"],
                message="Неправильное расширение файла",
            ), validate_image_size
        ],
        verbose_name="Фото рецепта",
    )
    preparation_time = models.TimeField(
        blank=True, null=True, verbose_name="Время поготовки"
    )
    cooking_time = models.TimeField(
        blank=True, null=True, verbose_name="Время приготовления"
    )
    date_published = models.DateTimeField(
        auto_now_add=True, verbose_name="Опубликовано", null=True
    )
    slug = models.SlugField(unique=True, max_length=100)
    difficulty = models.IntegerField(
        blank=True,
        choices=[(1, "Легко"), (2, "Нормально"), (3, "Сложно")],
        null=True,
        verbose_name="Сложность",
        default=2,
    )
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано?")
    has_calories = models.BooleanField(default=False, verbose_name="Есть ли калории?")
    portions = models.IntegerField(
        default=1, blank=True, null=True, verbose_name="Количество порций"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name="recipes",
        blank=True,
        null=True,
    )
    likes = models.IntegerField(default=0, verbose_name="Количество лайков")

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["date_published", "title"]

    def get_absolute_url(self):
        return reverse("recipe_view", kwargs={"category_slug": self.category.slug, "recipe_slug": self.slug})

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.slug = transliterate.slugify(self.title, language_code="ru")
        if self.calories is not None:
            self.has_calories = True
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.title


def custom_steps_upload_to(instance, filename):
    ext = filename.split(".")[-1]
    return "recipes/{category}/{title}/{step_number}.{ext}".format(
        category=instance.recipe.category.slug,
        title=instance.recipe.slug,
        step_number=instance.step_number,
        ext=ext,
    )


class Step(models.Model):
    step = models.TextField(
        validators=[
            MinLengthValidator(5, message="Слишком короткий шаг, минимум 10 символов"),
            MaxLengthValidator(
                2000, message="Слишком длинный шаг, максимум 2000 символов"
            ),
        ],
        verbose_name="Шаг",
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт", related_name="steps"
    )
    image = models.ImageField(
        upload_to=custom_steps_upload_to,
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "png"],
                message="Неправильное расширение изображения, доступные расширения: jpg, png",
            ), validate_image_size
        ],
        verbose_name="Изображение",
    )
    step_number = models.IntegerField(verbose_name="Порядок", default=1)

    class Meta:
        verbose_name = "Шаг"
        verbose_name_plural = "Шаги"
        ordering = ["step_number"]
        unique_together = ("recipe", "step_number", "step")

    def __str__(self):
        return self.step


"""
A class representing an ingredient used in a recipe.

Attributes:
    name (CharField): The name of the ingredient.
    quantity (CharField): The quantity of the ingredient.
    unit (CharField): The unit of measurement for the quantity.
    recipe (ForeignKey): The recipe to which the ingredient belongs.

Meta:
    verbose_name (str): A human-readable name for the model.
    verbose_name_plural (str): A human-readable plural name for the model.

Methods:
    __str__: Returns the name of the ingredient.

"""


class Ingredient(models.Model):
    class Units(models.TextChoices):
        GRAMS = "гр", "гр"
        TSP = "чайн.л.", "чайн.л."
        TBSP = "стол.л", "стол.л."
        ML = "мл", "мл"
        Z = "зубч.", "зубч."
        H = "шт.", "шт."

    name = models.CharField(max_length=200, verbose_name="Название")
    quantity = models.CharField(max_length=200, verbose_name="Количество")
    unit = models.CharField(
        max_length=100, verbose_name="Единица измерения", choices=Units.choices
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт", related_name="ingredients", null=True
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name
