from django.urls import path

from users.views import (BlockUserView, CustomUserLoginView, CustomUserLogoutView, CustomUserProfileDeleteView,
                         CustomUserProfileEditView, CustomUserProfileView, RegisterView, UserListView, confirm_email)

app_name = "users"

urlpatterns = [
    path(
        "login/",
        CustomUserLoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "logout/",
        CustomUserLogoutView.as_view(next_page=""),
        name="logout",
    ),
    path("user_register/", RegisterView.as_view(), name="register"),
    path("confirm-email/<str:token>/", confirm_email, name="confirm_email"),
    path("<int:pk>/block/", BlockUserView.as_view(), name="block_user"),
    path("profile/", CustomUserProfileView.as_view(), name="profile"),
    path("profile/edit/", CustomUserProfileEditView.as_view(), name="edit_profile"),
    path(
        "profile/delete/", CustomUserProfileDeleteView.as_view(), name="delete_profile"
    ),
    path("users/", UserListView.as_view(), name="user_list"),
]
