from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^ems/', include('dictionary.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('dictionary.urls')),
]

handler404 = 'dictionary.views.show_404_page'
handler500 = 'dictionary.views.show_500_page'
