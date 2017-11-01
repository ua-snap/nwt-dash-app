#### INSTALLATION

A Simple Dash Application to examine CMIP5 Downscaled climate model outputs over
the Northwest Territories, Canada. 

All work is funded through SNAP at the University of Alaska Fairbanks.

```
# make a virtualenv

python3 -m venv myvenv

# activate it
source myvenv/bin/activate

# install the needed packages
pip install pandas
pip install geopandas
pip install numpy
pip install dash==0.18.3
pip install dash-renderer==0.11.0
pip install dash-html-components==0.8.0
pip install dash-core-components==0.13.0
pip install plotly --upgrade
pip install gunicorn

# run most up-to-date version of the application
python app.py

# navigate to http://127.0.0.1:8050/

```
