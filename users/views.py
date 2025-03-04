from django.views.generic import ListView
from users.models import User

class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'