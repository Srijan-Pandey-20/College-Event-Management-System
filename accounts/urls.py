from django.urls import path

from . import views


urlpatterns = [
    path('', views.homePage),

    # Pages
    path('signup/', views.signup),
    path('login/', views.login),
    path('logout/', views.logout_view),

    # JSON APIs used by signup.html / login.html
    path('register/', views.register),
    path('loguser/', views.login_user),

    # Role-based dashboards
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('student/unregister/<int:registration_id>/', views.unregister_student_event, name='unregister_student_event'),
    path('admin/event/delete/<int:event_id>/', views.delete_event, name='delete_event'),
    path('admin/registration/manage/<int:registration_id>/', views.manage_student_registration, name='manage_student_registration'),

    # Database-backed public event information page
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),

]

# http://localhost:8000/accounts/dashboard/student/
# http://localhost:8000/accounts/dashboard/admin/
