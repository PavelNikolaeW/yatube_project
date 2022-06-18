from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# Функция get_user_model() обращается именно к той модели,
# которая зарегистрирована в качестве основной модели
# пользователей в конфиге проекта.
User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        """Указываем модель и  порядок полей которые хотим видеть в форме"""
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
