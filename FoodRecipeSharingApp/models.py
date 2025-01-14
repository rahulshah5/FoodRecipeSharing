from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db.models import Avg

class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name,gender, country,password=None,password2=None):

        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            full_name=full_name,
            gender=gender,
            country=country
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name,gender,country, password=None):
        user = self.create_user(
            email,
            password=password,
            full_name=full_name,
            gender=gender,
            country=country
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    gender_choices=(('male','male'),('female','female'),('other','other'))

    email = models.EmailField(verbose_name="email address", max_length=255, unique=True,)
    full_name=models.CharField(max_length=200)
    gender=models.CharField(choices=gender_choices,default=None,max_length=10)
    country=models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

   
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name",'gender','password','country']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        
        return True

    @property
    def is_staff(self):
        return self.is_admin

class TokenBlacklist(models.Model):
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=100,unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    
    def __init__(self, *args, **kwargs):
        super(Ingredient, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname, None)
        if value:
            value = value.upper()
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(Ingredient, self).pre_save(model_instance, add)
        

class RecipeImage(models.Model):
    image = models.ImageField(upload_to='recipe_images/')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
class Recipe(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000,default=' ')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField('Ingredient')
    cooking_time = models.PositiveIntegerField()
    difficulty_level = models.CharField(max_length=100)
    tags = models.ManyToManyField('Tag')
    servings= models.IntegerField(default=1)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    image = models.OneToOneField(RecipeImage, on_delete=models.CASCADE,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def update_average_rating(self):
        average_rating = Rating.objects.filter(recipe=self).aggregate(Avg('rating'))['rating__avg']
        if average_rating is not None:
            self.average_rating = round(average_rating, 2)
            self.save()

class RecipeStep(models.Model):
    recipe_name = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    step_number = models.IntegerField()
    description = models.TextField()
    time_in_minutes = models.PositiveIntegerField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.recipe_name.title

class Tag(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    country=models.CharField(max_length=50,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('recipe', 'user')
class Review(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('recipe', 'user')

class Favourite(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'user'], name='unique_recipe_user')
        ]
    def __str__(self):
        return f"{self.user} - {self.recipe}"



