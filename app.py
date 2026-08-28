import pandas as pd
import geopandas as gpd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv("Dashboard_data.csv")

gdf = gpd.read_file("WEST_BENGAL_DISTRICT_WEB.geojson")

# ============================================================
# STATE-LEVEL VALUES
# ============================================================

state_values = {

    "LPG User": {
        "2015-16": 25.00,
        "2019-21": 40.00
    },

    "No Toilet": {
        "2015-16": 25.00,
        "2019-21": 12.00
    },

    "Bank A/C Holder": {
        "2015-16": 85.00,
        "2019-21": 95.00
    },

    "Kachha/Semi-Kachha House": {
        "2015-16": 49.00,
        "2019-21": 44.00

    }
}
# ============================================================
# 2. BASIC CLEANING
# ============================================================

# Make sure district names are strings
df["District"] = df["District"].astype(str).str.strip()
gdf["DISTRICT"] = gdf["DISTRICT"].astype(str).str.strip()

# Make sure value is numeric
df["value"] = pd.to_numeric(df["value"], errors="coerce")


# ============================================================
# 3. DROPDOWN VALUES
# ============================================================

years = ["2015-16", "2019-21"]

indicators = sorted(df["indicator"].dropna().unique())


# ============================================================
# 4. CREATE DASH APP
# ============================================================

app = Dash(__name__)

app.title = "West Bengal Dashboard"


# ============================================================
# 5. DASHBOARD LAYOUT
# ============================================================

app.layout = html.Div(

    [

        # ====================================================
        # HEADER
        # ====================================================

        html.Div(

            [

                html.H1(
                    "West Bengal Dashboard",
                    className="dashboard-title"
                ),

                html.Div(
                    "District-level Socio-economic Indicators",
                    className="dashboard-subtitle"
                )

            ],

            className="dashboard-header"

        ),


        # ====================================================
        # CONTROLS
        # ====================================================

        html.Div(

            [

                html.Div(

                    [

                        html.Label(
                            "Year",
                            className="control-label"
                        ),

                        dcc.Dropdown(

                            id="year-dropdown",

                            options=[

                                {
                                    "label": "2015-16",
                                    "value": "2015-16"
                                },

                                {
                                    "label": "2019-21",
                                    "value": "2019-21"
                                }

                            ],

                            value="2019-21",

                            clearable=False

                        )

                    ],

                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "marginRight": "3%"
                    }

                ),


                html.Div(

                    [

                        html.Label(
                            "Indicator",
                            className="control-label"
                        ),

                        dcc.Dropdown(

                            id="indicator-dropdown",

                            options=[

                                {
                                    "label": indicator,
                                    "value": indicator
                                }

                                for indicator in indicators

                            ],

                            value=indicators[0],

                            clearable=False

                        )

                    ],

                    style={
                        "width": "30%",
                        "display": "inline-block"
                    }

                )

            ],

            className="control-panel"

        ),


        # ====================================================
        # SELECTED DISTRICT STORE
        # ====================================================

        dcc.Store(

            id="selected-district",

            data=None

        ),


        # ====================================================
        # MAP + INFORMATION PANEL
        # ====================================================

        html.Div(

            [

                html.Div(

                    [

                        dcc.Graph(

                            id="district-map",

                            style={
                                "height": "100%",
                                "width":"100%"
                            },

                            config={
                                "displayModeBar": False,
                                "scrollZoom": False
                            }

                        )

                    ],

                    className="map-container"

                ),


                html.Div(

                    [

                        html.H3(
                            "State Summary",
                            className="panel-heading"
                        ),

                        html.Div(
                            id="state-summary"
                        ),

                        html.Hr(
                            className="panel-divider"
                        ),

                        html.H3(
                            "Selected District Summary",
                            className="panel-heading"
                        ),

                        html.Div(
                            id="district-summary"
                        )

                    ],

                    className="info-panel"

                )

            ],

            className="main-content"

        ),


        # ====================================================
        # TREND
        # ====================================================

        html.Div(

            [

                html.H3(
                    "State Comparison",
                    className="trend-heading"
                ),

                html.Div(
                    id="trend-title",
                    className="trend-subtitle"
                ),

                html.Div(

                    [

                        # --------------------------------------------
                        # TREND PLOT
                        # --------------------------------------------

                        html.Div(

                            [

                                dcc.Graph(

                                    id="trend-plot",

                                    style={
                                        "height": "320px",
                                        "width": "100%"
                                    },

                                    config={
                                        "displayModeBar": False
                                    }

                                )

                            ],

                            className="trend-graph-container"

                        ),


                        # --------------------------------------------
                        # CUSTOM LEGEND
                        # --------------------------------------------

                        html.Div(

                            id="trend-legend",

                            className="trend-custom-legend"

                        )

                    ],

                    className="trend-content"

                )

            ],

            className="trend-container"

        )

    ],

    className="dashboard-container"

)

        
# ============================================================
# 6. UPDATE MAP + STATE SUMMARY
# ============================================================

@app.callback(
    Output("district-map", "figure"),
    Output("state-summary", "children"),

    Input("year-dropdown", "value"),
    Input("indicator-dropdown", "value")
)
def update_map(selected_year, selected_indicator):

    # --------------------------------------------------------
    # FILTER INDICATOR DATA
    # --------------------------------------------------------

    filtered = df[
        (df["Year"] == selected_year) &
        (df["indicator"] == selected_indicator)
    ].copy()


    # --------------------------------------------------------
    # CREATE A DICTIONARY OF DISTRICT VALUES
    # --------------------------------------------------------

    value_dict = dict(
        zip(
            filtered["District"],
            filtered["value"]
        )
    )


    # --------------------------------------------------------
    # COPY GEOMETRY
    # --------------------------------------------------------

    map_data = gdf.copy()


    # --------------------------------------------------------
    # ADD INDICATOR VALUE TO GEOMETRY
    # --------------------------------------------------------

    map_data["value"] = map_data["DISTRICT"].map(
        value_dict
    )

    # --------------------------------------------------------
    # MAP EXTENT
    # --------------------------------------------------------

    minx, miny, maxx, maxy = gdf.total_bounds

    center_lon = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2

    # --------------------------------------------------------
    # CREATE MAP
    # --------------------------------------------------------

    fig = px.choropleth_map(

        map_data,

        geojson=gdf.__geo_interface__,

        locations="DISTRICT",

        featureidkey="properties.DISTRICT",

        color="value",

        color_continuous_scale="Reds",

        hover_name="DISTRICT",

        hover_data={
            "value": ":.0f",
            "DISTRICT": False
        },

        map_style="white-bg",

        center={
            "lat": center_lat,
            "lon": center_lon
        },

        zoom=5.2,

        labels={
            "value": selected_indicator
        }
    )


    # --------------------------------------------------------
    # DISTRICT BOUNDARIES
    # --------------------------------------------------------

    fig.update_traces(

        marker_line_color="black",

        marker_line_width=1.2

    )


    # --------------------------------------------------------
    # MAP LAYOUT
    # --------------------------------------------------------

    fig.update_layout(

        margin={
            "r": 0,
            "t": 10,
            "l": 0,
            "b": 0
        },

    coloraxis_colorbar={
        "title": {
            "text": selected_indicator+" (%)",
            "font": {
                "size": 13,
                "family": "Arial",
                "color": "black"
            }
        },

        "thickness": 15,

        "len": 0.45,

        "x": 0.7,

        "y": 0.3,


        "tickfont": {
            "size": 12,
            "family": "Arial",
            "color": "black"
        },

        "outlinecolor": "black",
        "outlinewidth": 1
    }   

    )


    # --------------------------------------------------------
    # STATE SUMMARY
    # --------------------------------------------------------

    state_value = state_values[selected_indicator][selected_year]


    state_summary = [

        html.Div(
            selected_indicator,
            className="summary-indicator"
        ),

        html.Div(
            f"{state_value:.0f}%",
            className="state-value"
        ),

        html.Div(
            selected_year,
            className="summary-year"
        )

    ]

    return fig, state_summary

# ============================================================
# SELECT DISTRICT BY CLICK
# ============================================================

@app.callback(

    Output(
        "selected-district",
        "data"
    ),

    Input(
        "district-map",
        "clickData"
    ),

    prevent_initial_call=True

)

def select_district(click_data):

    if click_data is None:
        return None

    try:

        district = click_data["points"][0]["location"]

        return district

    except (KeyError, IndexError):

        return None

# ============================================================
# STATE + DISTRICT TREND
# ============================================================


# ============================================================
# TREND APPEARANCE
# ============================================================

TREND_STATE_COLOR = "#1f4e79"
TREND_DISTRICT_COLOR = "#c55a11"

TREND_AXIS_TITLE_SIZE = 14
TREND_TICK_SIZE = 15
TREND_LINE_WIDTH = 1
TREND_MARKER_SIZE = 5

@app.callback(

    Output(
        "trend-plot",
        "figure"
    ),

    Output(
        "trend-title",
        "children"
    ),

    Output(
    "trend-legend",
    "children"
    ),

    Input(
        "selected-district",
        "data"
    ),

    Input(
        "indicator-dropdown",
        "value"
    )

)

def update_trend(
    selected_district,
    selected_indicator
):

    # --------------------------------------------------------
    # YEARS
    # --------------------------------------------------------

    trend_years = [
        "2015-16",
        "2019-21"
    ]


    # --------------------------------------------------------
    # STATE VALUES
    # --------------------------------------------------------

    state_y = [

        state_values[selected_indicator][year]

        for year in trend_years

    ]


    # --------------------------------------------------------
    # TREND DATA
    # --------------------------------------------------------

    trend_data = pd.DataFrame({

        "Year": trend_years,

        "West Bengal": state_y

    })


    # --------------------------------------------------------
    # ADD SELECTED DISTRICT
    # --------------------------------------------------------

    if selected_district is not None:

        district_data = df[
            (df["District"] == selected_district) &
            (df["indicator"] == selected_indicator)
        ].copy()


        district_values = []

        for year in trend_years:

            match = district_data[
                district_data["Year"] == year
            ]


            if match.empty:

                district_values.append(None)

            else:

                district_values.append(
                    match.iloc[0]["value"]
                )


        trend_data[selected_district] = district_values


    # --------------------------------------------------------
    # CREATE LINE PLOT
    # --------------------------------------------------------

    y_columns = ["West Bengal"]

    if selected_district is not None:

        y_columns.append(selected_district)


    fig = px.line(

        trend_data,

        x="Year",

        y=y_columns,

        markers=True

    )

    fig.update_xaxes(
        title_text="Year",
        title_font={
            "size": TREND_AXIS_TITLE_SIZE,
            "family": "Arial Bold",
            "color": "black"
        },
        tickfont={
            "size": TREND_TICK_SIZE,
            "family": "Arial Bold",
            "color": "black"
        }
    )

    fig.update_yaxes(
        title_text=f"{selected_indicator} (%)",
        title_font={
            "size": TREND_AXIS_TITLE_SIZE,
            "family": "Arial Bold",
            "color": "black"
        },
        tickfont={
            "size": TREND_TICK_SIZE,
            "family": "Arial Bold",
            "color": "black"
        }
    )

    fig.update_xaxes(
        showline=True,
        linewidth=1.5,
        linecolor="#d61a75",
        mirror=True
    )

    fig.update_yaxes(
        showline=True,
        linewidth=1.5,
        linecolor="#d61a75",
        mirror=True
    )
    # --------------------------------------------------------
    # CUSTOM TRACE COLORS
    # --------------------------------------------------------

    fig.update_traces(
        line={
            "width": 3
        },
        marker={
            "size": 9,
            "line": {
                "width": 2,
                "color": "white"
            }
        }
    )


    # West Bengal
    fig.update_traces(

        selector={
            "name": "West Bengal"
        },

        line={
            "color": TREND_STATE_COLOR,
            "width": 3
        },

        marker={
            "size": 10,
            "color": TREND_STATE_COLOR,

            "line": {
                "color": "black",
                "width": 1.5
            }
        }

    )


    # Selected district
    if selected_district is not None:

        fig.update_traces(

            selector={
                "name": selected_district
            },

            line={
                "color": TREND_DISTRICT_COLOR,
                "width": 3
            },

            marker={
                "size": 10,
                "color": TREND_DISTRICT_COLOR,

                "line": {
                    "color": "black",
                    "width": 1.5
                }
            }

        )

    # --------------------------------------------------------
    # AXIS
    # --------------------------------------------------------

    fig.update_yaxes(
        title=f"{selected_indicator} (%)"
    )

    fig.update_xaxes(
        title="Year"
    )


    # --------------------------------------------------------
    # LAYOUT
    # --------------------------------------------------------

    fig.update_layout(

        margin={
            "l": 50,
            "r": 30,
            "t": 20,
            "b": 50
        },

        showlegend=False,

        legend_title_text=""

    )


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    if selected_district is None:

        title = (
            f"{selected_indicator} — West Bengal"
        )

    else:

        title = (
            f"{selected_indicator} — "
            f"{selected_district} vs West Bengal"
        )


    # --------------------------------------------------------
    # CUSTOM LEGEND
    # --------------------------------------------------------

    legend_items = [

        html.Div(

            [

                html.Span(
                    className="legend-dot state-dot"
                ),

                html.Span(
                    "West Bengal",
                    className="legend-name state-name"
                )

            ],

            className="legend-item"

        )

    ]


    if selected_district is not None:

        legend_items.append(

            html.Div(

                [

                    html.Span(
                        className="legend-dot district-dot"
                    ),

                    html.Span(
                        selected_district,
                        className="legend-name district-name-legend"
                    )

                ],

                className="legend-item"

            )

        )
    return fig, title, legend_items
# ============================================================
# 7. UPDATE DISTRICT HOVER SUMMARY
# ============================================================

@app.callback(

    Output("district-summary", "children"),

    Input("district-map", "hoverData"),

    Input("year-dropdown", "value"),

    Input("indicator-dropdown", "value")

)

def update_district_summary(
    hover_data,
    selected_year,
    selected_indicator
):

    if hover_data is None:

        return html.Div(
            "Hover over a district on the map.",
            className="hover-instruction"
        )


    try:

        district = hover_data["points"][0]["location"]

    except (KeyError, IndexError):

        return html.Div(
            "Hover over a district on the map.",
            className="hover-instruction"
        )


    result = df[
        (df["District"] == district) &
        (df["Year"] == selected_year) &
        (df["indicator"] == selected_indicator)
    ]


    if result.empty:

        return html.Div(
            "No data available.",
            className="hover-instruction"
        )


    value = result.iloc[0]["value"]


    return html.Div(
        [

            html.Div(
                district,
                className="district-name"
            ),

            html.Div(
                f"{value:.0f}%",
                className="district-value"
            ),

            html.Div(
                selected_year,
                className="summary-year"
            )

        ],

        className="district-summary-content"
    )
# ============================================================
# 8. RUN APPLICATION
# ============================================================

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8050)),
        debug=False
    )