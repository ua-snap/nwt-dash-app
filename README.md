A simple Dash application to examine CMIP5 downscaled climate model outputs over the Northwest Territories, Canada.

All work is funded through SNAP at the University of Alaska, Fairbanks.

To extract the data for NWT locations, run `data_prep/extract_profile_snap_deltadownscaled_rasters.py` on Atlas. The `data.pickle` file should be generated locally with `make_pickle.py` after the extraction is complete.

To run the application locally, install [pipenv](https://pipenv.readthedocs.io/en/latest/).  This app needs `python3` to run; if that's not your default python, adjust the command below (i.e. `python3` instead of `python`).

```bash
cd /path/to/this/repo
pipenv install
export REQUESTS_PATHNAME_PREFIX='/' # see below for more info
export MAPBOX_ACCESS_TOKEN='' # <-- insert a valid mapbox token here
pipenv run python application.py
```

The application will be available at [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

## Deployment on AWS

Before deploying, update the `requirements.txt` file:

```sh
pipenv clean
pipenv run pip freeze > requirements.txt
git commit -am'updating requirements.txt'
```

When deploying on AWS Elastic Beanstalk, a few environment variables must be set using `eb setenv`:

 * `MAPBOX_ACCESS_TOKEN`: token for API access for Mapbox, no default value.
 * `REQUESTS_PATHNAME_PREFIX`: Path prefix on host, should be `/` for local development and `/tools/nwt-climate-explorer/` for current deploy on AWS.
 * `DASH_REQUESTS_PATHNAME_PREFIX`: URL for file requests, must start and end with `/`. Should be `/tools/nwt-climate-explorer/` for current deploy on AWS.
 * `eb printenv` displays the current environment variables.
 * `eb deploy` deploys the source bundle from the initialized project directory to the running application (e.g. `bob-nwt-dash-app-dev`).
 * `eb open` will open the URL in your browser.

