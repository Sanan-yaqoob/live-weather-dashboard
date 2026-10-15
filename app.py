
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Live Weather Dashboard",
    page_icon="🌦️",
    layout="wide",
)

st.markdown(
    """
    <style>
        .stApp {
            background-color: #F7F9FC;
        }
        .block-container {
            max-width: 1400px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1 {
            color: #19324D;
            font-weight: 700;
        }
        h2, h3 {
            color: #254766;
        }
        [data-testid="stMetric"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            padding: 18px;
            border-radius: 10px;
        }
        [data-testid="stMetricLabel"] {
            color: #526579;
        }
        [data-testid="stMetricValue"] {
            color: #19324D;
        }
        section[data-testid="stSidebar"] {
            background-color: #EEF3F8;
        }
        .stButton button {
            border-radius: 8px;
            font-weight: 500;
        }
        hr {
            border-color: #DCE4ED;
        }
        .forecast-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 16px 8px;
            text-align: center;
            min-height: 180px;
        }
        .forecast-day {
            color: #526579;
            font-size: 14px;
            font-weight: 600;
        }
        .forecast-icon {
            font-size: 30px;
            margin: 10px 0;
        }
        .forecast-condition {
            color: #526579;
            font-size: 12px;
            min-height: 32px;
        }
        .forecast-temp {
            color: #19324D;
            font-weight: 600;
            font-size: 14px;
            margin-top: 8px;
        }
        .insight-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 16px;
            min-height: 110px;
        }
        .insight-label {
            color: #526579;
            font-size: 13px;
        }
        .insight-value {
            color: #19324D;
            font-size: 23px;
            font-weight: 700;
            margin-top: 6px;
        }
        .insight-detail {
            color: #718096;
            font-size: 12px;
            margin-top: 4px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# API URLS & Weather Codes

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "🌨️"),
    80: ("Rain showers", "🌦️"),
    81: ("Moderate showers", "🌧️"),
    82: ("Heavy showers", "⛈️"),
    85: ("Snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Severe thunderstorm with hail", "⛈️"),
}

# Helper Functions & API Requests

def api_get(url, params):
    """Request JSON data from an API."""
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=900, show_spinner=False)
def find_city(city_name):
    """Find matching cities and their coordinates."""
    data = api_get(
        GEOCODING_URL,
        {
            "name": city_name,
            "count": 10,
            "language": "en",
            "format": "json",
        },
    )
    return data.get("results", [])

@st.cache_data(ttl=900, show_spinner=False)
def get_weather(latitude, longitude):
    """Retrieve current, hourly and daily weather data."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,precipitation,"
            "weather_code,wind_speed_10m"
        ),
        "hourly": (
            "temperature_2m,precipitation_probability"
        ),
        "daily": (
            "weather_code,temperature_2m_max,"
            "temperature_2m_min,precipitation_probability_max,"
            "sunrise,sunset"
        ),
        "timezone": "auto",
        "forecast_days": 7,
    }

    return api_get(FORECAST_URL, params)

def describe_weather(code):
    """Convert a weather code into a description and emoji."""
    return WEATHER_CODES.get(
        int(code),
        ("Conditions unavailable", "🌡️"),
    )

def style_chart(fig, y_title):
    """Apply consistent styling to Plotly charts."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial, sans-serif",
            color="#254766",
            size=12,
        ),
        margin=dict(l=15, r=15, t=45, b=15),
        hovermode="x unified",
        xaxis_title="Local time",
        yaxis_title=y_title,
        legend_title_text="",
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="#DCE4ED",
    )
    fig.update_yaxes(
        gridcolor="#E8EDF3",
        zeroline=False,
    )

    return fig


# Sidebar

with st.sidebar:
    st.title("🌦️ Weather")
    st.caption("Explore current conditions and forecasts.")

    city = st.text_input(
        "Enter a city",
        value="London",
    )

    refresh = st.button(
        "🔄 Refresh weather",
        use_container_width=True,
    )

if refresh:
    st.cache_data.clear()

if not city.strip():
    st.info("Enter a city name in the sidebar to view its weather.")
    st.stop()


# Main Weather Dashboard

st.title("Live Weather Dashboard")

st.caption(
    "Current conditions, hourly trends and a weekly forecast."
)

try:
    with st.spinner(f"Finding locations matching {city.strip()}..."):
        locations = find_city(city.strip())

    if not locations:
        st.error(
            "City not found. Check the spelling or try a larger nearby city."
        )
        st.stop()

    # Let the user choose when multiple locations match.
    if len(locations) > 1:
        options = {}

        for place in locations:
            label = ", ".join(
                part
                for part in [
                    place.get("name"),
                    place.get("admin1"),
                    place.get("country"),
                ]
                if part
            )

            # Avoid overwriting results with identical labels.
            unique_label = label
            suffix = 2

            while unique_label in options:
                unique_label = f"{label} ({suffix})"
                suffix += 1

            options[unique_label] = place

        selected_label = st.selectbox(
            "Select the correct location",
            list(options.keys()),
        )

        location = options[selected_label]

    else:
        location = locations[0]

    weather = get_weather(
        location["latitude"],
        location["longitude"],
    )

    current = weather["current"]
    hourly = pd.DataFrame(weather["hourly"])
    daily = pd.DataFrame(weather["daily"])

    condition, emoji = describe_weather(
        current["weather_code"]
    )

    place_label = ", ".join(
        part
        for part in [
            location.get("name"),
            location.get("admin1"),
            location.get("country"),
        ]
        if part
    )

    # Current Weather

    st.subheader(f"{emoji} {place_label}")

    local_time = current.get("time", "N/A").replace("T", " ")
    st.caption(f"Local date and time: {local_time}")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🌡️ Temperature",
        f"{current['temperature_2m']:.1f} °C",
    )

    c2.metric(
        "🤗 Feels like",
        f"{current['apparent_temperature']:.1f} °C",
    )

    c3.metric(
        "💧 Humidity",
        f"{current['relative_humidity_2m']}%",
    )

    c4.metric(
        "💨 Wind speed",
        f"{current['wind_speed_10m']:.1f} km/h",
    )

    st.markdown(f"### {emoji} {condition}")

    st.caption(
        f"Current precipitation: {current['precipitation']} mm"
    )

    st.divider()

    # Hourly Data

    hourly["time"] = pd.to_datetime(hourly["time"])

    # Keep the next 24 forecast hours.
    next_24 = hourly.head(24).copy()

    # Replace missing values for charting only.
    next_24["precipitation_probability"] = (
        next_24["precipitation_probability"].fillna(0)
    )

    # Insights

    st.subheader("Weather insights")

    warmest_hour = next_24.loc[
        next_24["temperature_2m"].idxmax()
    ]

    highest_rain_hour = next_24.loc[
        next_24["precipitation_probability"].idxmax()
    ]

    i1, i2 = st.columns(2)

    with i1:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">Warmest upcoming hour</div>
                <div class="insight-value">
                    {warmest_hour["temperature_2m"]:.1f} °C
                </div>
                <div class="insight-detail">
                    {warmest_hour["time"].strftime("%a, %H:%M")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with i2:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-label">
                    Highest hourly precipitation probability
                </div>
                <div class="insight-value">
                    {highest_rain_hour["precipitation_probability"]:.0f}%
                </div>
                <div class="insight-detail">
                    {highest_rain_hour["time"].strftime("%a, %H:%M")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "Insights are calculated from the next 24 forecast hours."
    )

    st.divider()

    # Charts

    left, right = st.columns(2)

    with left:
        st.subheader("Hourly temperature")

        temp_fig = px.line(
            next_24,
            x="time",
            y="temperature_2m",
            markers=True,
            labels={
                "time": "Local time",
                "temperature_2m": "Temperature (°C)",
            },
            title="Temperature over the next 24 hours",
        )

        temp_fig.update_traces(
            line=dict(color="#3984D6", width=3),
            marker=dict(size=5),
        )

        temp_fig = style_chart(
            temp_fig,
            "Temperature (°C)",
        )

        st.plotly_chart(
            temp_fig,
            use_container_width=True,
        )

    with right:
        st.subheader("Chance of precipitation")

        rain_fig = px.bar(
            next_24,
            x="time",
            y="precipitation_probability",
            labels={
                "time": "Local time",
                "precipitation_probability": "Chance (%)",
            },
            title="Hourly precipitation probability",
        )

        rain_fig.update_traces(
            marker_color="#65A9E8",
            marker_line_width=0,
        )

        rain_fig.update_yaxes(
            range=[0, 100],
            ticksuffix="%",
        )

        rain_fig = style_chart(
            rain_fig,
            "Precipitation probability (%)",
        )

        st.plotly_chart(
            rain_fig,
            use_container_width=True,
        )

    st.divider()

    # Weekly Forcast

    st.subheader("Seven-day forecast")

    daily["time"] = pd.to_datetime(daily["time"])

    daily["Conditions"] = daily["weather_code"].apply(
        lambda code: describe_weather(code)[0]
    )

    daily["Icon"] = daily["weather_code"].apply(
        lambda code: describe_weather(code)[1]
    )

    daily["Day"] = daily["time"].dt.strftime("%a, %d %b")

    forecast_columns = st.columns(7)

    for index, (_, row) in enumerate(daily.iterrows()):
        with forecast_columns[index]:
            st.markdown(
                f"""
                <div class="forecast-card">
                    <div class="forecast-day">{row["Day"]}</div>
                    <div class="forecast-icon">{row["Icon"]}</div>
                    <div class="forecast-condition">
                        {row["Conditions"]}
                    </div>
                    <div class="forecast-temp">
                        {row["temperature_2m_max"]:.0f}°
                        /
                        {row["temperature_2m_min"]:.0f}°C
                    </div>
                    <div class="forecast-condition">
                        Rain: {row["precipitation_probability_max"]}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # Extra Weather Information

    with st.expander("Sunrise and sunset times"):
        sun_columns = st.columns(2)

        sunrise = weather["daily"]["sunrise"][0]
        sunset = weather["daily"]["sunset"][0]

        sun_columns[0].metric(
            "🌅 Sunrise",
            sunrise.split("T")[-1],
        )

        sun_columns[1].metric(
            "🌇 Sunset",
            sunset.split("T")[-1],
        )

    with st.expander("View forecast data"):
        display = daily[
            [
                "Day",
                "Icon",
                "Conditions",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max",
            ]
        ].rename(
            columns={
                "temperature_2m_max": "High (°C)",
                "temperature_2m_min": "Low (°C)",
                "precipitation_probability_max": "Rain chance (%)",
            }
        )

        st.dataframe(
            display,
            hide_index=True,
            use_container_width=True,
        )

    st.divider()

    st.subheader("About this project")

    st.markdown(
        """
        This dashboard retrieves weather data from the Open-Meteo API
        and presents current conditions, hourly trends and a seven-day
        forecast in an interactive format.
        """
    )

except requests.RequestException:
    st.error(
        "Couldn't connect to the weather service. "
        "Check your internet connection and try refreshing."
    )

except (KeyError, ValueError, TypeError, IndexError) as error:
    st.error(
        "The weather service returned unexpected data. "
        "Please refresh and try again."
    )
    st.caption(f"Technical detail: {error}")
