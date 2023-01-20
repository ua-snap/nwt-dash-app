"""
NWT Climate Explorer
"""
# pylint: disable=invalid-name, import-error, line-too-long, too-many-arguments
from datetime import datetime
import plotly.graph_objs as go
from dash import dcc, html
import dash_dangerously_set_inner_html as ddsih
import luts


# Helper functions for GUI.
def wrap_in_section(content, section_classes="", container_classes="", div_classes=""):
    """
    Helper function to wrap sections.
    Accepts an array of children which will be assigned within
    this structure:
    <section class="section">
        <div class="container">
            <div>[children]...
    """
    return html.Section(
        className="section " + section_classes,
        children=[
            html.Div(
                className="container " + container_classes,
                children=[html.Div(className=div_classes, children=content)],
            )
        ],
    )


def wrap_in_field(label, control, className=""):
    """
    Returns the control wrapped
    in Bulma-friendly markup.
    """
    return html.Div(
        className="field " + className,
        children=[
            html.Label(label, className="label"),
            html.Div(className="control", children=control),
        ],
    )


map_figure = go.Figure(data=luts.places_trace, layout=luts.map_layout)

header = ddsih.DangerouslySetInnerHTML(
    f"""
<div class="bannerstrip">University of Alaska Fairbanks&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;Scenarios Network for Alaska + Arctic Planning</div>
<header>
    <div class="container">
        <div class="titles">
            <h1 class="title is-1">Northwest Territories<br> Climate Explorer</h1>
            <h2 class="subtitle is-2">See climate projections for NWT locations under different scenarios</h2>
        </div>
    </div>
</header>
<section class="introduction section">
    <div class="container content is-size-4">
        <p>See climate projections&mdash;including very long&ndash;term extrapolations&mdash;for 46 communities in the Northwest Territories of Canada.</p>
        <p>You can look at each of five different climate models or a model average, choosing only selected months if you wish. For example, you can chart projected precipitation in May and June for Fort McPherson, years 2000&ndash;2300, using a five-model average.</p>
        <p>The tool also explains how different levels of greenhouse gas emissions create the various paths to future climates known as RCPs and ECPs.</p>
        <p class="camera-icon">Click the <span>
            <svg viewBox="0 0 1000 1000" class="icon" height="1em" width="1em"><path d="m500 450c-83 0-150-67-150-150 0-83 67-150 150-150 83 0 150 67 150 150 0 83-67 150-150 150z m400 150h-120c-16 0-34 13-39 29l-31 93c-6 15-23 28-40 28h-340c-16 0-34-13-39-28l-31-94c-6-15-23-28-40-28h-120c-55 0-100-45-100-100v-450c0-55 45-100 100-100h800c55 0 100 45 100 100v450c0 55-45 100-100 100z m-400-550c-138 0-250 112-250 250 0 138 112 250 250 250 138 0 250-112 250-250 0-138-112-250-250-250z m365 380c-19 0-35 16-35 35 0 19 16 35 35 35 19 0 35-16 35-35 0-19-16-35-35-35z" transform="matrix(1 0 0 -1 0 850)"></path></svg>
        </span> icon in the upper-right of each chart to download it.</p>
    </div>
</section>
"""
)

current_year = datetime.now().year
footer = ddsih.DangerouslySetInnerHTML(
    f"""
<footer class="footer">
    <div class="container">
        <div class="columns">
            <div class="logos column is-one-fifth">
                <a href="https://www.gov.nt.ca/">
                    <img src="{luts.path_prefix}assets/NWT.svg" />
                </a>
                <br>
                <a href="https://uaf.edu/uaf/">
                    <img src="{luts.path_prefix}assets/UAF.svg" />
                </a>
            </div>
            <div class="column content is-size-5">
                <p>This tool is part of an ongoing collaboration between the <a href="https://uaf-snap.org">Scenarios Network for Alaska + Arctic Planning</a> and the Government of Northwest Territories. We are working to make a wide range of downscaled climate products that are easily accessible, flexibly usable, and fully interpreted and understandable to users in the Northwest Territories, while making these products relevant at a broad geographic scale.
                </p>
                <p>Please contact <a href="mailto:uaf-snap-data-tools@alaska.edu">uaf-snap-data-tools@alaska.edu</a> if you have questions or would like to provide feedback for this tool. <a href="https://uaf-snap.org/tools-overview/">Visit the SNAP Climate + Weather Tools page</a> to see our full suite of interactive web tools.</p>
                <p>Copyright &copy; {current_year} University of Alaska Fairbanks.  All rights reserved.</p>
                <p>UA is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual.  <a href="https://www.alaska.edu/nondiscrimination/">Statement of Nondiscrimination</a> and <a href="https://www.alaska.edu/records/records/compliance/gdpr/ua-privacy-statement/">Privacy Statement</a>.</p>
                <p>UA is committed to providing accessible websites. <a href="https://www.alaska.edu/webaccessibility/">Learn more about UA&rsquo;s notice of web accessibility</a>.  If we can help you access this website&rsquo;s content, <a href="mailto:uaf-snap-data-tools@alaska.edu">email us!</a></p>
                <p>Photo &copy; Robert Wilson Photography</p>
            </div>
        </div>
    </div>
</footer>
"""
)

communities_dropdown_field = html.Div(
    className="field",
    children=[
        html.Label("Location", className="label"),
        html.Div(
            className="control",
            children=[
                dcc.Dropdown(
                    id="communities-dropdown",
                    options=[
                        {"label": community[0], "value": index}
                        for index, community in luts.communities.iterrows()
                    ],
                    value=[45],  # yellowknife
                )
            ],
        ),
    ],
)

scenarios_checkbox_field = wrap_in_field(
    "Scenarios (RCPs/ECPs)",
    dcc.Checklist(
        labelClassName="checkbox",
        className="control",
        id="scenario-check",
        options=list(
            map(
                lambda k: {"label": luts.scenarios_lut[k], "value": k},
                luts.scenarios_lut,
            )
        ),
        value=["rcp60", "rcp85"],
    ),
)

variable_toggle_field = wrap_in_field(
    "Variable",
    dcc.RadioItems(
        labelClassName="radio",
        className="control",
        id="variable-toggle",
        options=list(
            map(
                lambda k: {"label": luts.variables_lut[k], "value": k},
                luts.variables_lut,
            )
        ),
        value="tas",
    ),
)

# Not quite the ideal Bulma structure, but it's functional.
months_field = html.Div(
    className="field",
    children=[
        html.Label("Months", className="label"),
        dcc.Checklist(
            labelClassName="checkbox",
            className="control",
            id="all-month-check",
            options=[{"label": " All months", "value": "all"}],
            value=[],
        ),
        html.Div(
            className="control",
            children=[
                dcc.Dropdown(
                    id="month-dropdown",
                    options=list(
                        map(
                            lambda k: {"label": luts.months_lut[k], "value": k},
                            luts.months_lut,
                        )
                    ),
                    value=[12, 1, 2],
                    multi=True,
                    disabled=False,
                )
            ],
        ),
    ],
)

models_field = wrap_in_field(
    "Model(s)",
    dcc.Dropdown(
        id="model-dropdown",
        options=list(
            map(lambda k: {"label": luts.models_lut[k], "value": k}, luts.models_lut)
        ),
        value=["NCAR-CCSM4"],
        multi=True,
    ),
)

form_fields = html.Div(
    className="columns form",
    children=[
        html.Div(
            className="column is-two-thirds",
            children=[
                communities_dropdown_field,
                dcc.Graph(
                    id="minesites-map",
                    figure=map_figure,
                    config={"displayModeBar": False, "scrollZoom": False},
                ),
            ],
        ),
        html.Div(
            className="column",
            children=[
                variable_toggle_field,
                months_field,
                models_field,
                scenarios_checkbox_field,
            ],
        ),
    ],
)

main_layout = wrap_in_section(
    html.Div(
        children=[
            html.Div(
                className="section section--form",
                children=[
                    form_fields,
                ],
            ),
            html.Div(
                className="graph",
                children=[
                    dcc.Graph(
                        id="my-graph",
                        config={
                            "toImageButtonOptions": {
                                "title": "Export to PNG",
                                "format": "png",
                                "filename": "CommunityChart",
                                "height": 600,
                                "width": 1600,
                                "scale": 1,
                            },

                            "modeBarButtonsToRemove": [
                                "zoom2d",
                                "zoomIn2d",
                                "zoomOut2d",
                                "sendToCloud",
                                "autoScale2d",
                                "resetScale2d",
                                "pan2d",
                                "select2d",
                                "hoverClosestCartesian",
                                "hoverCompareCartesian",
                                "lasso2d",
                                "toggleSpikelines",
                            ],
                            "scrollZoom": False,
                            "displaylogo": False,
                        },
                    ),
                    html.Div(
                        className="form date-range-selector",
                        children=[
                            html.Label("Date range", className="label"),
                            dcc.RangeSlider(
                                className="control",
                                id="range-slider",
                                marks={i: i for i in range(2000, 2320, 20)},
                                min=2000,
                                max=2300,
                                step=20,
                                value=[2000, 2300],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
)

help_text = wrap_in_section(
    dcc.Markdown(
        """

## Climate scenarios

### Representative Concentration Pathways (RCPs)

RCPs describe paths to future climates based on atmospheric greenhouse gas concentrations. They represent climate futures—scenarios—extrapolated out to the year 2100, based on a range of possible future human behaviors. RCPs provide a basis for comparison and a “common language” for modelers to share their work.

The RCP values 4.5, 6.0, and 8.5 indicate projected radiative forcing values—the difference between solar energy absorbed by Earth vs. energy radiated back to space—measured in watts per square meter. RCP X projects that in 2100 the concentration of greenhouse gases will be such that each square meter of Earth will absorb X times more solar energy than it did in 1750.

 * RCP 4.5 — “low” scenario. Assumes that new technologies and socioeconomic strategies cause emissions to peak in 2040 and radiative forcing to stabilize after 2100.
 * RCP 6.0 — “medium” scenario. Assumes that emissions peak in 2080 and radiative forcing stabilizes after 2100.
 * RCP 8.5 — “high” scenario. Emissions increase through the 21st century.

### Extended Concentration Pathways (ECPs)

These scenarios allow extensions of RCPs for 2100–2300 by expanding the data series for greenhouse gas and land use. ECPs are intended to provide rough estimations of what climate and ocean systems might look like in a few centuries regardless of the driving forces of emissions (demography, policies, technology, and investment).

### Source data

Source data used in this tool can be downloaded [here](https://catalog.snap.uaf.edu/geonetwork/srv/eng/catalog.search#/metadata/815c6708-b6cf-4a46-b5c8-344851063117).

                """,
    ),
    container_classes="is-size-5 content",
)

layout = html.Div(children=[header, main_layout, help_text, footer])
