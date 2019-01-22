A Simple Dash Application to examine CMIP5 Downscaled climate model outputs over
the Northwest Territories, Canada.

All work is funded through SNAP at the University of Alaska Fairbanks.

__App is currently hosted [here](https://nwt-dash-app.herokuapp.com/).__

To run the application locally, install [pipenv](https://pipenv.readthedocs.io/en/latest/).  This app needs `python3` to run; if that's not your default python, adjust the command below (i.e. `python3` instead of `python`).

```bash
cd /path/to/this/repo
pipenv install
pipenv run python app.py
```

The application will be available at http://127.0.0.1:8050/.
