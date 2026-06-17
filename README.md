# 🏃 Running Course Analyzer

A Streamlit web application that helps runners in Seoul explore and compare running courses by terrain, weather suitability, and difficulty — all from a single interactive dashboard.

**Live app:** _add your Streamlit Cloud URL here_

---

## What This App Does

Planning a run usually means checking a map for the route, a separate tool for elevation, and a weather app — before you even put your shoes on. This app consolidates all of that into one screen:

- **Course Filter & Selection** — filter by difficulty (Beginner / Intermediate / Advanced) and pick a course from the sidebar.
- **Key Metrics** — distance, elevation gain, estimated time, and average pace at a glance.
- **Elevation Profile** — an interactive Plotly chart showing how the course climbs and descends over its full distance.
- **Course Map** — the actual route plotted on real OpenStreetMap tiles, with start and finish markers.
- **Weather Suitability Score** — a 0–100 "Runability Score" combining temperature, humidity, wind, and sky condition, adjusted by course difficulty.
- **Course Comparison Dashboard** — a color-coded table and grouped bar chart comparing all filtered courses side by side.
- **External Links** — one-tap links to Google Maps, Instagram, and a Spotify playlist for each course.

---

## Project Structure

```
running-course-analyzer/
├── app.py                # Main Streamlit application
├── data/
│   └── courses.csv       # Course dataset (distance, elevation, surface, coordinates, route waypoints)
├── requirements.txt      # Python dependencies
└── README.md
```

---

## Running Locally

```bash
git clone https://github.com/<your-username>/running-course-analyzer.git
cd running-course-analyzer
pip install -r requirements.txt
streamlit run app.py
```

The app reads course data directly from `data/courses.csv`, so no database or API key is required to run it.

---

## Data Sources

| Data | Source | Notes |
|---|---|---|
| Course distance, surface, location | Generated with AI assistance (Claude), then verified for plausibility against known characteristics of each real Seoul location (e.g. the Han River path being flat, Bukhansan being a steep mountain trail) | `data/courses.csv` |
| Course coordinates & route waypoints | Approximate coordinates for each real location, used to render the route on the map | `data/courses.csv` |
| Elevation profile shape | Modeled programmatically (NumPy) per course to reflect each route's real terrain pattern | Generated at runtime in `app.py` |
| Weather conditions | Simulated using realistic ranges based on Seoul's seasonal climate averages | Generated at runtime in `app.py` |

An earlier version of this project attempted to integrate the OpenWeatherMap API directly. The request failed with a `403 Host not in allowlist` error, because Streamlit Cloud's free tier restricts outbound network requests to non-whitelisted domains. The weather module was kept as a realistic simulation so the app remains fully functional without external API dependencies; the function signature is designed so a live API could be substituted in directly if deployed on infrastructure without that restriction.

---

## Tech Stack

- **[Streamlit](https://streamlit.io/)** — UI framework, sidebar, layout, metrics
- **[Pandas](https://pandas.pydata.org/)** — DataFrame handling, styled comparison tables
- **[NumPy](https://numpy.org/)** — elevation profile generation
- **[Plotly](https://plotly.com/python/)** — interactive elevation chart, course map (`Scattermapbox` over OpenStreetMap tiles, no API key required), and comparison bar chart

---

## Possible Future Improvements

- Replace simulated weather with a live API call when deployed outside Streamlit Cloud's free-tier network restrictions
- Allow users to upload their own GPX file and have the app generate a real elevation profile and map route from it
- Add more Seoul courses and let users submit their own via a form

---

## Author's Note

This project was built as a course final assignment. The application code and dataset were generated with AI assistance, in line with course guidelines permitting AI-assisted development as long as data sources are understood and disclosed. All course data was reviewed for real-world plausibility before being included.
