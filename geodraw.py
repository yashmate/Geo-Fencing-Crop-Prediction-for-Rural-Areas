import gmplot
import pandas as pd
import numpy as np
df=pd.read_csv('final.csv')

latitude_list = list(df['latitude'])
longitude_list=list(df['longitude'])
#longitude_list = [ 77.8701919, 78.048457, 78.0413095 ]

                                
gmap5 = gmplot.GoogleMapPlotter(21.91005,  77.95589, zoom=20)

gmap5.scatter( latitude_list, longitude_list, '# FF0000', size = 40, marker = False)

# polygon method Draw a polygon with
# the help of coordinates
gmap5.polygon(latitude_list, longitude_list, color = 'cornflowerblue')

gmap5.draw(r"/home/yash/TechGits/index.html")
