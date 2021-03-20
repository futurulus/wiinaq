from django.urls import include, path
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    path(r'', include('dictionary.urls')),
    path(r'ems/', include('dictionary.urls')),
    path(r'admin/', admin.site.urls),
]

handler404 = 'dictionary.views.show_404_page'
handler500 = 'dictionary.views.show_500_page'
