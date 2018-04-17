A Simple Dash Application to examine CMIP5 Downscaled climate model outputs over
the Northwest Territories, Canada. 

All work is funded through SNAP at the University of Alaska Fairbanks.

__App is currently hosted [here](https://nwt-dash-app.herokuapp.com/).__

To run the application locally, follow the shell commands below.  Not tested on Windows.

```bash

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
pip install dash-core-components==0.13.0-rc5
pip install plotly --upgrade
pip install gunicorn

# clone the source of this package to your local machine
git clone git@github.com:ua-snap/nwt-dash-app.git
cd nwt-dash-app/

# run most up-to-date version of the application
python app.py

# navigate to http://127.0.0.1:8050/

```
