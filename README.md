# Live Weather Dashboard

A beginner-friendly data science project built with Python, Streamlit, Pandas and Plotly. The dashboard retrieves live weather and forecast data from the Open-Meteo API and presents it through interactive charts and visual summaries.

## Features

- Search for a city and select the correct location.
- View current temperature, feels-like temperature, humidity and wind speed.
- Explore hourly temperature and precipitation probability.
- View a seven-day weather forecast.
- Review simple insights calculated from forecast data.
- Refresh weather data when needed.

## Technologies Used

- **Python** — application logic
- **Streamlit** — interactive dashboard
- **Pandas** — data preparation and analysis
- **Plotly Express** — interactive charts
- **Requests** — API requests
- **Open-Meteo API** — weather and forecast data

## Run Locally

1. Clone this repository.
2. Open the project folder in your terminal.
3. Create and activate a virtual environment.
4. Install the dependencies.
5. Run the dashboard.

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the application:

```bash
python -m streamlit run app.py
```

The dashboard should open in your browser, usually at `http://localhost:8501`.

## Data Source

Weather data is provided by [Open-Meteo](https://open-meteo.com/).

## Project Purpose

This project demonstrates working with an external API, preparing data with Pandas, creating interactive visualisations, and presenting weather information through a simple dashboard.

## Future Improvements

- Deploy the dashboard online.
- Add historical weather comparisons.
- Improve data insights and user controls.