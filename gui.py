"""
NWT Mine site future climate tool
"""
# pylint: disable=invalid-name, import-error, line-too-long, too-many-arguments
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
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

# We want this HTML structure to get the full-width background color:
# <div class="header">
#   <div class="container"> gives us the centered column
#     <div class="section"> a bit more padding to stay consistent with form
header_section = html.Div(
    className="header",
    children=[
        html.Div(
            className="container",
            children=[
                html.Div(
                    className="section header--section",
                    children=[
                        html.Div(
                            className="header--logo",
                            children=[
                                html.A(
                                    className="header--snap-link",
                                    href="https://snap.uaf.edu",
                                    rel="external",
                                    target="_blank",
                                    children=[
                                        html.Img(
                                            src=luts.path_prefix
                                            + "assets/SNAP_acronym_color_square.svg"
                                        )
                                    ],
                                )
                            ],
                        ),
                        html.Div(
                            className="header--titles",
                            children=[
                                html.H1(
                                    "Northwest Territories Climate Explorer",
                                    className="title is-3",
                                ),
                                html.H2(
                                    "See climate projections for NWT locations under different scenarios.  Choose a location and variables to get started.",
                                    className="subtitle is-5",
                                ),
                            ],
                        ),
                    ],
                )
            ],
        )
    ],
)

footer = html.Footer(
    className="footer has-text-centered",
    children=[
        html.Div(
            children=[
                html.A(
                    href="https://snap.uaf.edu",
                    target="_blank",
                    className="level-item",
                    children=[html.Img(src=luts.path_prefix + "assets/SNAP_color_all.svg")],
                ),
                html.A(
                    href="https://uaf.edu/uaf/",
                    target="_blank",
                    className="level-item",
                    children=[html.Img(src=luts.path_prefix + "assets/UAF.svg")],
                ),
                html.A(
                    href="https://www.gov.nt.ca/",
                    target="_blank",
                    className="level-item",
                    children=[html.Img(src=luts.path_prefix + "assets/NWT.svg")],
                ),
            ]
        ),
        dcc.Markdown(
            """
This tool is part of an ongoing collaboration between SNAP and the Government of Northwest Territories. We are working to make a wide range of downscaled climate products that are easily accessible, flexibly usable, and fully interpreted and understandable to users in the Northwest Territories, while making these products relevant at a broad geographic scale.

UA is an AA/EO employer and educational institution and prohibits illegal discrimination against any individual. [Statement of Nondiscrimination](https://www.alaska.edu/nondiscrimination/)
            """,
            className="content is-size-6",
        ),
    ],
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
                        {"label": i, "value": i}
                        for i in luts.communities.index
                    ],
                    value="Yellowknife",
                )
            ],
        ),
    ],
)

scenarios_checkbox_field = html.Div(
    className="field",
    children=[
        html.Label("Scenarios (RCPs/ECPs)", className="label"),
        dcc.Checklist(
            labelClassName="checkbox",
            className="control",
            id="scenario-check",
            options=list(
                map(lambda k: {"label": luts.scenarios_lut[k], "value": k}, luts.scenarios_lut)
            ),
            value=["rcp60", "rcp85"],
        ),
    ],
)

variable_toggle_field = html.Div(
    className="field",
    children=[
        html.Label("Variable", className="label"),
        dcc.RadioItems(
            labelClassName="radio",
            className="control",
            id="variable-toggle",
            options=list(
                map(lambda k: {"label": luts.variables_lut[k], "value": k}, luts.variables_lut)
            ),
            value="tas",
        ),
    ],
)

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
                        map(lambda k: {"label": luts.months_lut[k], "value": k}, luts.months_lut)
                    ),
                    value=[12, 1, 2],
                    multi=True,
                    disabled=False,
                )
            ],
        ),
    ],
)

models_field = html.Div(
    className="field",
    children=[
        html.Label("Models(s)", className="label"),
        dcc.Dropdown(
            id="model-dropdown",
            options=list(
                map(lambda k: {"label": luts.models_lut[k], "value": k}, luts.models_lut)
            ),
            value=["NCAR-CCSM4"],
            multi=True,
        ),
    ],
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

main_layout = html.Div(
    className="container",
    children=[
        html.Div(
            className="section section--form",
            children=[
                form_fields,
            ],
        ),
        html.Div(
            className="section graph",
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
                            "sendToCloud",
                            "pan2d",
                            "select2d",
                            "lasso2d",
                            "toggleSpikeLines",
                        ],
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

help_text = html.Div(
    className="container",
    children=[
        html.Div(
            className="section",
            children=[
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


                """,
                    className="is-size-5 content",
                )
            ],
        )
    ],
)

layout = html.Div(children=[header_section, main_layout, help_text, footer])
