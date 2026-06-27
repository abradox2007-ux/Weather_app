"""
╔══════════════════════════════════════════════════════════╗
║          SkyCheck — Single-File Weather App              ║
║                                                          ║
║  Install:  pip install fastapi uvicorn httpx             ║
║  Run:      python weather_app.py                         ║
║  Opens:    http://localhost:8000  (auto-launched)        ║
╚══════════════════════════════════════════════════════════╝
"""

# ── Standard library ────────────────────────────────────────────────────────
import os
import sys
import threading
import webbrowser

# ── Third-party ─────────────────────────────────────────────────────────────
try:
    import httpx
    import uvicorn
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
except ImportError:
    print("\n❌  Missing dependencies. Run this first:\n")
    print("    pip install fastapi uvicorn httpx\n")
    sys.exit(1)


# ════════════════════════════════════════════════════════════════════════════
#  FRONTEND  — the entire UI lives in this string
# ════════════════════════════════════════════════════════════════════════════

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>SkyCheck — Live Weather</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&display=swap" rel="stylesheet"/>
<style>
/* ── Reset & base ─────────────────────────────────────────────── */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:       #05080f;
  --bg-glow:  #0d2a4a;
  --surface:  #131c35;
  --card:     #0f172a;
  --card-hdr: #0d1f3c;
  --border:   rgba(255,255,255,0.09);
  --accent:   #38bdf8;
  --accent-d: #0ea5e9;
  --accent-t: rgba(56,189,248,0.08);
  --accent-b: rgba(56,189,248,0.18);
  --text:     #f1f5f9;
  --muted:    #64748b;
  --muted2:   #334155;
  --red:      #f87171;
  --font-d:   'Space Grotesk', sans-serif;
  --font-b:   'Inter', sans-serif;
  --radius:   1rem;
  --shadow:   0 8px 40px rgba(0,0,0,0.55);
  --glow:     0 0 40px rgba(56,189,248,0.22);
}
html{font-size:16px}
body{
  font-family:var(--font-b);
  background:var(--bg);
  background-image:
    radial-gradient(ellipse 90% 55% at 50% -5%, var(--bg-glow) 0%, transparent 65%),
    radial-gradient(circle at 85% 85%, #06101f 0%, transparent 55%);
  min-height:100vh;
  display:flex;
  flex-direction:column;
  align-items:center;
  padding:4rem 1rem 3rem;
  color:var(--text);
}

/* ── Typography ───────────────────────────────────────────────── */
.font-d{font-family:var(--font-d)}
h1{font-family:var(--font-d);font-size:clamp(2.5rem,6vw,3.5rem);font-weight:700;letter-spacing:-0.03em;line-height:1}
h1 span{color:var(--accent)}

/* ── Header ───────────────────────────────────────────────────── */
header{text-align:center;margin-bottom:3rem}
.live-badge{
  display:inline-flex;align-items:center;gap:0.45rem;
  margin-bottom:0.8rem;
  font-family:var(--font-d);font-size:0.7rem;font-weight:600;
  letter-spacing:0.15em;text-transform:uppercase;color:var(--accent);
}
.dot{position:relative;width:8px;height:8px}
.dot-ring{
  position:absolute;inset:0;border-radius:50%;background:var(--accent);
  animation:ping 1.5s ease-in-out infinite;
}
.dot-core{position:absolute;inset:0;border-radius:50%;background:var(--accent)}
@keyframes ping{0%,100%{transform:scale(1);opacity:0.8}50%{transform:scale(2.2);opacity:0}}
.subtitle{color:var(--muted);font-size:0.88rem;margin-top:0.55rem}

/* ── Search ───────────────────────────────────────────────────── */
.search-wrap{width:100%;max-width:26rem;margin-bottom:2rem}
.search-row{display:flex;gap:0.6rem}
.input-wrap{position:relative;flex:1}
.search-icon{
  position:absolute;left:0.9rem;top:50%;transform:translateY(-50%);
  width:16px;height:16px;stroke:var(--muted);pointer-events:none;
}
input[type=text]{
  width:100%;background:var(--surface);color:var(--text);
  border:1px solid var(--border);border-radius:var(--radius);
  padding:0.85rem 1rem 0.85rem 2.5rem;
  font-family:var(--font-b);font-size:0.9rem;
  transition:box-shadow .2s,border-color .2s;
  outline:none;
}
input[type=text]::placeholder{color:var(--muted)}
input[type=text]:focus{
  border-color:var(--accent);
  box-shadow:0 0 0 2px var(--accent), 0 0 18px rgba(56,189,248,0.2);
}
.btn{
  background:var(--accent);color:#05080f;
  font-family:var(--font-d);font-weight:600;font-size:0.88rem;
  border:none;border-radius:var(--radius);padding:0.85rem 1.3rem;
  cursor:pointer;white-space:nowrap;
  transition:background .15s, transform .1s, box-shadow .2s;
  box-shadow:var(--glow);
}
.btn:hover{background:var(--accent-d)}
.btn:active{transform:scale(0.96)}
.btn:disabled{opacity:0.5;cursor:not-allowed;transform:none}

/* ── Error ────────────────────────────────────────────────────── */
.error{
  display:none;margin-top:0.75rem;
  font-size:0.84rem;color:var(--red);
  align-items:center;gap:0.4rem;
  padding-left:0.25rem;
}
.error.show{display:flex}
.err-icon{width:15px;height:15px;stroke:var(--red);flex-shrink:0}

/* ── Spinner ──────────────────────────────────────────────────── */
.spinner{
  display:none;flex-direction:column;align-items:center;gap:0.75rem;
  margin-bottom:1.5rem;
}
.spinner.show{display:flex}
.spin-svg{width:42px;height:42px;animation:spin 1.1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.spin-label{color:var(--muted);font-size:0.84rem}

/* ── Card ─────────────────────────────────────────────────────── */
.card{
  display:none;width:100%;max-width:26rem;
  background:var(--card);border:1px solid var(--border);
  border-radius:1.25rem;overflow:hidden;
  box-shadow:var(--shadow);
  animation:fadeUp .45s ease forwards;
}
.card.show{display:block}
@keyframes fadeUp{
  from{opacity:0;transform:translateY(18px)}
  to  {opacity:1;transform:translateY(0)}
}

/* Card header band */
.card-hdr{
  background:linear-gradient(135deg, #0d2240 0%, #050d1a 100%);
  padding:1.6rem 1.6rem 1.4rem;
  border-bottom:1px solid var(--border);
}
.city-row{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;margin-bottom:0.25rem}
.city-name{font-family:var(--font-d);font-size:1.9rem;font-weight:700;line-height:1.1}
.city-sub{font-size:0.82rem;color:var(--muted);margin-top:0.2rem}
.wx-icon{font-size:3.2rem;line-height:1;user-select:none;flex-shrink:0}
.condition-pill{
  display:inline-block;margin-top:0.85rem;
  font-family:var(--font-d);font-size:0.7rem;font-weight:600;
  letter-spacing:0.12em;text-transform:uppercase;
  color:rgba(56,189,248,0.85);
  background:rgba(56,189,248,0.08);
  border:1px solid rgba(56,189,248,0.2);
  border-radius:999px;padding:0.28rem 0.9rem;
}

/* Card body */
.card-body{padding:1.5rem 1.6rem}

/* Temperature */
.temp-row{display:flex;align-items:flex-end;gap:0.4rem;margin-bottom:1.2rem}
.temp-num{
  font-family:var(--font-d);font-size:5.5rem;font-weight:700;
  line-height:1;letter-spacing:-0.04em;color:var(--text);
}
.temp-unit{font-family:var(--font-d);font-size:1.5rem;color:var(--muted);margin-bottom:0.4rem}

/* Pill row */
.pills{display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:1.4rem}
.pill{
  background:var(--accent-t);border:1px solid var(--accent-b);
  border-radius:999px;padding:0.3rem 0.85rem;
  font-family:var(--font-d);font-size:0.8rem;font-weight:500;
  color:#7dd3fc;white-space:nowrap;
}

/* Compass section */
.compass-section{display:flex;align-items:center;gap:1.2rem;margin-bottom:1.4rem}
.compass-svg{width:64px;height:64px;flex-shrink:0}
.compass-label{font-family:var(--font-d);font-size:0.65rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:var(--muted);margin-bottom:0.2rem}
.compass-val{font-family:var(--font-d);font-size:1.1rem;font-weight:600}
#compass-needle{
  transform-origin:32px 32px;
  transition:transform .65s cubic-bezier(.34,1.56,.64,1);
}

/* Divider */
.divider{border:none;border-top:1px solid var(--border);margin-bottom:1.2rem}

/* Footer row */
.card-foot{display:flex;align-items:center;justify-content:space-between}
.daynight{display:flex;align-items:center;gap:0.5rem;font-size:0.85rem;color:#cbd5e1}
.fetch-time{font-size:0.72rem;color:var(--muted2)}

/* ── Footer ───────────────────────────────────────────────────── */
footer{margin-top:3.5rem;font-size:0.75rem;color:var(--muted2);text-align:center}
footer a{color:var(--muted);text-decoration:underline;text-underline-offset:2px}
footer a:hover{color:var(--text)}
</style>
</head>
<body>

<!-- Header -->
<header>
  <div class="live-badge">
    <span class="dot"><span class="dot-ring"></span><span class="dot-core"></span></span>
    Live Weather
  </div>
  <h1>Sky<span>Check</span></h1>
  <p class="subtitle">Real-time conditions powered by Open-Meteo</p>
</header>

<!-- Search -->
<div class="search-wrap">
  <div class="search-row">
    <div class="input-wrap">
      <svg class="search-icon" fill="none" viewBox="0 0 24 24" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      <input id="city-input" type="text" placeholder="Search any city…" autocomplete="off"/>
    </div>
    <button class="btn" id="search-btn">Search</button>
  </div>

  <!-- Error -->
  <p class="error" id="error-msg">
    <svg class="err-icon" fill="none" viewBox="0 0 24 24" stroke-width="2">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/>
      <line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
    <span id="error-text"></span>
  </p>
</div>

<!-- Spinner -->
<div class="spinner" id="spinner">
  <svg class="spin-svg" fill="none" viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="10" stroke="#38bdf8" stroke-width="3" opacity="0.18"/>
    <path d="M4 12a8 8 0 018-8v3a5 5 0 00-5 5H4z" fill="#38bdf8"/>
  </svg>
  <span class="spin-label">Fetching weather…</span>
</div>

<!-- Weather card -->
<div class="card" id="weather-card">

  <div class="card-hdr">
    <div class="city-row">
      <div>
        <div class="city-name font-d" id="city-name"></div>
        <div class="city-sub" id="region-country"></div>
      </div>
      <span id="wx-icon" class="wx-icon"></span>
    </div>
    <span class="condition-pill" id="condition-pill"></span>
  </div>

  <div class="card-body">
    <!-- Temperature -->
    <div class="temp-row">
      <span class="temp-num font-d" id="temperature"></span>
      <span class="temp-unit font-d">°C</span>
    </div>

    <!-- Pills -->
    <div class="pills">
      <span class="pill" id="pill-wind"></span>
      <span class="pill" id="pill-dir"></span>
      <span class="pill" id="pill-coords"></span>
    </div>

    <!-- Compass -->
    <div class="compass-section">
      <svg class="compass-svg" viewBox="0 0 64 64">
        <circle cx="32" cy="32" r="30" fill="none" stroke="rgba(56,189,248,0.13)" stroke-width="1.5"/>
        <text x="32" y="9.5" text-anchor="middle" fill="#64748b" font-size="7" font-family="Space Grotesk">N</text>
        <text x="32" y="60"  text-anchor="middle" fill="#64748b" font-size="7" font-family="Space Grotesk">S</text>
        <text x="7"  y="35"  text-anchor="middle" fill="#64748b" font-size="7" font-family="Space Grotesk">W</text>
        <text x="57" y="35"  text-anchor="middle" fill="#64748b" font-size="7" font-family="Space Grotesk">E</text>
        <g id="compass-needle">
          <polygon points="32,14 35,32 29,32" fill="#38bdf8" opacity="0.92"/>
          <polygon points="32,50 35,32 29,32" fill="#334155" opacity="0.7"/>
          <circle cx="32" cy="32" r="2.8" fill="#38bdf8"/>
        </g>
      </svg>
      <div>
        <div class="compass-label">Wind direction</div>
        <div class="compass-val font-d" id="wind-dir-text">—</div>
      </div>
    </div>

    <hr class="divider"/>

    <div class="card-foot">
      <div class="daynight">
        <span id="daynight-icon"></span>
        <span id="daynight-label"></span>
      </div>
      <span class="fetch-time" id="fetch-time"></span>
    </div>
  </div>
</div>

<footer>
  Data from <a href="https://open-meteo.com" target="_blank">Open-Meteo</a> &middot; Free &amp; Open Source
</footer>

<script>
// ── DOM refs ─────────────────────────────────────────────────────
const $  = id => document.getElementById(id);
const input      = $('city-input');
const btn        = $('search-btn');
const spinner    = $('spinner');
const card       = $('weather-card');
const errBox     = $('error-msg');
const errText    = $('error-text');

// ── Helpers ──────────────────────────────────────────────────────
function compass(deg) {
  const d = ["N","NNE","NE","ENE","E","ESE","SE","SSE",
             "S","SSW","SW","WSW","W","WNW","NW","NNW"];
  return d[Math.round(((deg % 360) + 360) % 360 / 22.5) % 16];
}

function showErr(msg) {
  errText.textContent = msg;
  errBox.classList.add('show');
  card.classList.remove('show');
}
function clearErr() { errBox.classList.remove('show'); }

function setLoading(on) {
  spinner.classList.toggle('show', on);
  btn.disabled = on;
}

// ── Fetch weather ─────────────────────────────────────────────────
async function fetchWeather() {
  const city = input.value.trim();
  if (!city) { showErr('Please enter a city name.'); return; }

  clearErr();
  card.classList.remove('show');
  setLoading(true);

  try {
    const res = await fetch('/api/weather?city=' + encodeURIComponent(city));

    let data;
    try { data = await res.json(); }
    catch { throw new Error('Server returned an unexpected response.'); }

    if (!res.ok) {
      showErr(data.detail || 'Error ' + res.status + '. Please try again.');
      return;
    }

    // ── Populate card ─────────────────────────────────────────────
    $('city-name').textContent      = data.city;
    $('region-country').textContent = [data.region, data.country].filter(Boolean).join(', ');
    $('wx-icon').textContent        = data.icon;
    $('condition-pill').textContent = data.condition;
    $('temperature').textContent    = data.temperature != null ? Math.round(data.temperature) : '—';

    $('pill-wind').textContent    = data.windspeed != null ? '💨 ' + data.windspeed + ' km/h' : '💨 —';
    $('pill-coords').textContent  = '📍 ' + data.latitude + ', ' + data.longitude;

    const dir = data.wind_direction;
    $('pill-dir').textContent = dir != null ? '🧭 ' + compass(dir) : '🧭 —';

    if (dir != null) {
      $('compass-needle').style.transform = 'rotate(' + dir + 'deg)';
      $('wind-dir-text').textContent = compass(dir) + ' · ' + dir + '°';
    } else {
      $('compass-needle').style.transform = 'rotate(0deg)';
      $('wind-dir-text').textContent = 'Not available';
    }

    $('daynight-icon').textContent  = data.is_day ? '🌅' : '🌙';
    $('daynight-label').textContent = data.is_day ? 'Daytime' : 'Night-time';
    $('fetch-time').textContent     = 'Updated ' + new Date().toLocaleTimeString();

    // Re-trigger animation
    card.classList.remove('show');
    void card.offsetWidth;
    card.classList.add('show');

  } catch (err) {
    showErr(err.message || 'Network error — make sure the app is running.');
    console.error(err);
  } finally {
    setLoading(false);
  }
}

// ── Events ────────────────────────────────────────────────────────
btn.addEventListener('click', fetchWeather);
input.addEventListener('keydown', e => { if (e.key === 'Enter') fetchWeather(); });
input.focus();
</script>
</body>
</html>"""


# ════════════════════════════════════════════════════════════════════════════
#  BACKEND  — FastAPI app + Open-Meteo integration
# ════════════════════════════════════════════════════════════════════════════

from contextlib import asynccontextmanager

# Shared async HTTP client
_client: httpx.AsyncClient | None = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=10,
            headers={"User-Agent": "SkyCheck/1.0 (weather app)"},
            follow_redirects=True,
        )
    return _client

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Cleanly close the shared HTTP client on shutdown if it was initialized."""
    yield
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()

app = FastAPI(title="SkyCheck", docs_url=None, redoc_url=None, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# ── WMO weather codes ────────────────────────────────────────────────────────
WMO: dict[int, dict] = {
    0:  {"description": "Clear sky",            "icon": "☀️"},
    1:  {"description": "Mainly clear",         "icon": "🌤️"},
    2:  {"description": "Partly cloudy",        "icon": "⛅"},
    3:  {"description": "Overcast",             "icon": "☁️"},
    45: {"description": "Foggy",               "icon": "🌫️"},
    48: {"description": "Icy fog",             "icon": "🌫️"},
    51: {"description": "Light drizzle",       "icon": "🌦️"},
    53: {"description": "Drizzle",             "icon": "🌦️"},
    55: {"description": "Heavy drizzle",       "icon": "🌧️"},
    61: {"description": "Slight rain",         "icon": "🌧️"},
    63: {"description": "Rain",                "icon": "🌧️"},
    65: {"description": "Heavy rain",          "icon": "🌧️"},
    71: {"description": "Slight snow",         "icon": "🌨️"},
    73: {"description": "Snow",                "icon": "❄️"},
    75: {"description": "Heavy snow",          "icon": "❄️"},
    80: {"description": "Slight showers",      "icon": "🌦️"},
    81: {"description": "Showers",             "icon": "🌧️"},
    82: {"description": "Violent showers",     "icon": "⛈️"},
    95: {"description": "Thunderstorm",        "icon": "⛈️"},
    96: {"description": "Thunderstorm+hail",   "icon": "⛈️"},
    99: {"description": "Thunderstorm+hail",   "icon": "⛈️"},
}

GEO_URL     = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# ── Route: frontend ──────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=HTML)


# ── Route: weather API ───────────────────────────────────────────────────────
@app.get("/api/weather")
async def get_weather(city: str = Query(..., min_length=1)):
    """GET /api/weather?city=Chennai — returns current weather."""

    # Step 1: Geocode
    try:
        client = get_client()
        geo = await client.get(GEO_URL, params={"name": city, "count": 1, "language": "en"})
        geo.raise_for_status()
        geo_data = geo.json()
    except httpx.TimeoutException:
        raise HTTPException(504, "Geocoding service timed out. Please try again.")
    except httpx.HTTPStatusError as e:
        raise HTTPException(502, f"Geocoding service error ({e.response.status_code}).")
    except httpx.RequestError as e:
        raise HTTPException(502, f"Could not reach geocoding service: {e}")
    except Exception:
        raise HTTPException(502, "Unexpected geocoding error.")

    if not geo_data.get("results"):
        raise HTTPException(404, f"City '{city}' not found. Check the spelling and try again.")

    loc     = geo_data["results"][0]
    lat     = loc["latitude"]
    lon     = loc["longitude"]
    name    = loc.get("name", city)
    country = loc.get("country", "")
    region  = loc.get("admin1", "")

    # Step 2: Weather
    try:
        client = get_client()
        wx = await client.get(WEATHER_URL, params={
            "latitude":        lat,
            "longitude":       lon,
            "current_weather": "true",
            "wind_speed_unit": "kmh",
            "current":         "temperature_2m,wind_speed_10m,wind_direction_10m,weather_code,is_day",
        })
        wx.raise_for_status()
        wx_data = wx.json()
    except httpx.TimeoutException:
        raise HTTPException(504, "Weather service timed out. Please try again.")
    except httpx.HTTPStatusError as e:
        raise HTTPException(502, f"Weather service error ({e.response.status_code}).")
    except httpx.RequestError as e:
        raise HTTPException(502, f"Could not reach weather service: {e}")
    except Exception:
        raise HTTPException(502, "Unexpected weather fetch error.")

    if "current" in wx_data:
        c = wx_data["current"]
        temp, wind_spd = c.get("temperature_2m"), c.get("wind_speed_10m")
        wind_dir, wmo_code, is_day = c.get("wind_direction_10m"), c.get("weather_code"), c.get("is_day", 1)
    elif "current_weather" in wx_data:
        c = wx_data["current_weather"]
        temp, wind_spd = c.get("temperature"), c.get("windspeed")
        wind_dir, wmo_code, is_day = c.get("winddirection"), c.get("weathercode"), c.get("is_day", 1)
    else:
        raise HTTPException(502, "Unexpected response format from weather service.")

    wmo_info = WMO.get(int(wmo_code), {"description": "Unknown", "icon": "🌡️"}) if wmo_code is not None else {"description": "Unknown", "icon": "🌡️"}

    return {
        "city":           name,
        "region":         region,
        "country":        country,
        "latitude":       round(float(lat), 4),
        "longitude":      round(float(lon), 4),
        "temperature":    temp,
        "windspeed":      wind_spd,
        "wind_direction": round(float(wind_dir)) if wind_dir is not None else None,
        "condition":      wmo_info["description"],
        "icon":           wmo_info["icon"],
        "is_day":         bool(is_day),
    }


# ════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    PORT = 8082
    URL  = f"http://localhost:{PORT}"

    # Ensure terminal supports UTF-8 characters on Windows
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    print(f"""
╔══════════════════════════════════════════════╗
║           SkyCheck is starting up…           ║
╠══════════════════════════════════════════════╣
║  Open in browser → {URL:<25}║
║  Stop the server  → Ctrl + C                 ║
╚══════════════════════════════════════════════╝
""")

    # Auto-open browser after a short delay so the server is ready
    def _open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open(URL)

    threading.Thread(target=_open_browser, daemon=True).start()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="warning",   # suppress noisy request logs
    )
