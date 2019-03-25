A simple Dash application to examine CMIP5 downscaled climate model outputs over the Northwest Territories, Canada.

All work is funded through SNAP at the University of Alaska, Fairbanks.

To run the application locally, install [pipenv](https://pipenv.readthedocs.io/en/latest/).  This app needs `python3` to run; if that's not your default python, adjust the command below (i.e. `python3` instead of `python`).

```bash
cd /path/to/this/repo
pipenv install
pipenv run python application.py
```

The application will be available at [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

## Deployment on AWS

When deploying on AWS Elastic Beanstalk, a few environment variables must be set:

 * `MAPBOX_ACCESS_TOKEN`: token for API access for Mapbox, no default value
 * `GTAG_ID`: property ID for Google Analytics, no default value
 * `REQUESTS_PATHNAME_PREFIX`: Path prefix on host, should be `/` for local development and `/tools/nwt-climate-explorer/` for current deploy on AWS
