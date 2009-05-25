from django.conf.urls.defaults import patterns, url

urlpatterns = patterns("geoplot",
	url(r'/about$', 'views.about', name = 'geoplot_about'),
	url(r'/$', 'views.geoPlot', name = 'geoplot'),
)