doc = """
GEOPLOT
=======

Geoplot is a web service producing high quality maps.

Where possible it follows the same interface as the Google 
static maps API:
(http://code.google.com/apis/maps/documentation/staticmaps/)






"""
import time

from django.http import HttpResponse, HttpResponseServerError 
from django.shortcuts import render_to_response
from django.template import RequestContext
from PIL import Image, ImageDraw

import metrics
import geoplot


import settings

params = [
	#Param, Default, parser
	('size', (200,100), geoplot.parse_size),
	('zoom', 0, geoplot.parse_zoom),
	('center', (0.0, 0.0), geoplot.parse_latlong),
	('markers', [], geoplot.parse_markers),	
	('inset', False, geoplot.parse_inset),
	('path', {}, geoplot.parse_path),	
]
		

def canonical_request(values):
	"""
	Encode a map request as a compressed string, for logs in the shorterm and storage later?
	"""
	out = ""
	out += "s%s&" % "x".join(map(str, values['size']))
	out += "i%s&" % (values['inset'] and '1' or '0')
	out += "c%s&" % ",".join(map(str, values['center']))
	out += "z%s&" % values['zoom']
	#out += "m%s&" % "|".join(["%s,%s,%s" % (x['location'][0], x['location'][1], x['color'])for x in values['markers']])
	#out += "p%s-%s&" % ("|".join(map( ",".join, values['path'].get('points', "!"))), values['path'].get('color', "!"))
	out += "nm%s&" % len(values['markers'])
	out += "np%s&" % len(values['path'].get('points', []))
	
	return out
	
def geoPlot(request):
	"""
	Plot a map with stuff marked on it. 
	ASSUME WGS84 MAP DATUM  
	
	Attempt to Follow the Google static maps API where practicable:
	http://code.google.com/apis/maps/documentation/staticmaps/
	
	"""
	start_time = time.time()

	try:		
		values = {}
		for i in params:
			if request.GET.get(i[0]) and len(i)>1 and callable(i[2]):
				values[i[0]] = i[2](request.GET.get(i[0], i[1]))
			else:
				values[i[0]] = request.GET.get(i[0], i[1])
				
		
		response = make_image(values)
		
		metrics.log(metrics.codes['Geoplot'][0], metrics.ip_log(request), canonical_request(values), str(time.time()- start_time))
		return response 
	
		
	except (ValueError, AssertionError, NotImplementedError), e:
		r = HttpResponse("<h1>Bad Args - could not create image</h1>" + str(e))
		r.status_code = 400
		return r


def make_image(values):
	im, gd, offset = geoplot.get_map_image(values['size'], values['center'], values['zoom']) 
	geoplot.plot_markers(im, values['markers'], gd, offset)
	geoplot.plot_path(im, values['path'].get('points'), "", gd, offset)
	if values['inset']: 
		geoplot.draw_inset(im, gd, offset)
	
	# serialize to HTTP response
	response = HttpResponse(mimetype="image/png")
	im.save(response, "PNG")
	return response


def about(request):
	return render_to_response("about_geoplot.html", {}, context_instance = RequestContext(request, {}))
		