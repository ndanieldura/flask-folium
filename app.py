from flask import Flask, render_template, request
import os
import re
import time
import folium
from folium.plugins import Fullscreen
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/",methods = ['POST','GET'])
def get_well():
	global coord, name, info
	coord=''
	name=''
	info=''
	if request.method == 'POST' and 'well' in request.form:
		wells = request.form.get('well')
		#options to remove chrome errors
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument("--headless")
		chrome_options.add_argument("--disable-dev-shm-usage")
		chrome_options.add_argument("--no-sandbox")
		chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
		driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

		#connect to the website
		driver.get("https://factpages.npd.no/en/wellbore/PageView/Exploration/All")

		link = driver.find_element_by_link_text(wells)
		link.click()

		well = WebDriverWait(driver,5).until(
				EC.presence_of_all_elements_located(((By.XPATH, '//td[@class="a798c r7 r6"]'))))

		longitude = WebDriverWait(driver,5).until(
				EC.presence_of_all_elements_located(((By.XPATH, '//td[@class="a1386c r6"]'))))

		latitude = WebDriverWait(driver,5).until(
				EC.presence_of_all_elements_located(((By.XPATH, '//td[@class="a1373c r6"]'))))
		
		informations = WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located(((By.XPATH, '//div[@class = "uk-accordion-content uk-column-1-2@m"]'))))
		
		for (a, b, c, d) in zip(well, longitude, latitude, informations):
				coord = {
				'Long': b.text,
				'Lat': c.text
			}
				name = {'Well': a.text}
				info = {'Info': d.text}
		
		#conversion
		def dms2dd(degrees, minutes, seconds):
			dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60);
			return dd;
			
		def parse_dms(dms):
			parts = re.split('[^\d?.\w]+', dms)
			lat = dms2dd(parts[0], parts[1], parts[2])
			return (lat)

		for k, v in coord.items():
			coord[k] = parse_dms(v)

	return render_template("home.html", coord=coord, name = name, info = info)

@app.route('/map')
def well_map():
	map_NM = folium.Map([61.222303, 3.440436],
			   zoom_start=7,
			   tiles='cartodbdark_matter',
			   control_scale=True)

	label = name['Well']
	label = folium.Popup(label)
	
	folium.CircleMarker([coord['Lat'], coord['Long']],
	radius=5,
	popup=label,
	color='#ffb732',
	fill=True,
	fill_color='#FFD27F',
	fs = Fullscreen(),
	fill_opacity=0.7).add_to(map_NM) 

	return map_NM._repr_html_()

if __name__ == "__main__":
	app.run(debug=True)