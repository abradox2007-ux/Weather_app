"""
╔══════════════════════════════════════════════════════════════╗
║         SkyCheck PREMIUM — Single-File Weather App           ║
║                                                              ║
║  Install:  pip install fastapi uvicorn httpx                 ║
║  Run:      python weather_app_premium.py                     ║
║  Opens:    http://localhost:8082                             ║
╚══════════════════════════════════════════════════════════════╝
"""

import os, sys, threading, webbrowser, asyncio

try:
    import httpx
    import uvicorn
    from fastapi import FastAPI, HTTPException, Query, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
except ImportError:
    print("\n❌  Missing dependencies. Run:\n    pip install fastapi uvicorn httpx\n")
    sys.exit(1)


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>SkyCheck — Premium Weather & Live Ambient Cinema</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#060a12;
  --surface:rgba(13,20,37,0.65);
  --surface2:rgba(17,24,39,0.85);
  --card:rgba(10,18,32,0.6);
  --border:rgba(255,255,255,0.1);
  --border2:rgba(255,255,255,0.15);
  --accent:#60a5fa;
  --accent-d:#3b82f6;
  --accent-t:rgba(96,165,250,0.12);
  --accent-b:rgba(96,165,250,0.25);
  --text:#f8fafc;
  --text2:#cbd5e1;
  --text3:#94a3b8;
  --red:#f87171;
  --green:#34d399;
  --yellow:#fbbf24;
  --font:'DM Sans',sans-serif;
  --mono:'DM Mono',monospace;
  --r:14px;
  --r2:20px;
  --shadow:0 24px 80px rgba(0,0,0,0.6);
  --glow:0 0 60px rgba(96,165,250,0.2);
}
html,body{height:100%}
body{
  font-family:var(--font);background:#04070d;
  color:var(--text);min-height:100vh;
  display:flex;flex-direction:column;align-items:center;
  padding:2.5rem 1rem 4rem;
  overflow-x:hidden;
  position:relative;
}

/* ── FULL HOMEPAGE BACKGROUND VIDEO LAYER ─── */
.home-bg-video-wrap{
  position:fixed;inset:0;width:100vw;height:100vh;
  z-index:0;pointer-events:none;overflow:hidden;
}
#home-bg-video{
  width:100%;height:100%;object-fit:cover;
  filter:brightness(0.85) contrast(1.05);
  transition:opacity 1s ease-in-out, filter 1s ease-in-out;opacity:0.85;
}
.home-bg-overlay{
  position:absolute;inset:0;
  background:radial-gradient(circle at 50% 30%, rgba(4,7,13,0.15), rgba(4,7,13,0.65) 80%),
             linear-gradient(to bottom, rgba(4,7,13,0.3), rgba(4,7,13,0.75));
  transition:background 1s ease-in-out;
}
.home-bg-video-wrap.night-active #home-bg-video{
  filter:brightness(1.35) contrast(1.15) saturate(1.2);
  opacity:0.95;
}
.home-bg-video-wrap.night-active .home-bg-overlay{
  background:radial-gradient(circle at 50% 30%, rgba(4,7,13,0.05), rgba(4,7,13,0.4) 80%),
             linear-gradient(to bottom, rgba(4,7,13,0.15), rgba(4,7,13,0.5));
}

/* ── APP LAYOUT ─── */
.app-layout{
  position:relative;z-index:2;
  width:100%;max-width:1320px;
  display:flex;flex-direction:row;
  align-items:flex-start;justify-content:space-between;
  gap:2.5rem;padding:0 1rem;
}
.page{position:relative;flex:1;width:100%;max-width:680px;display:flex;flex-direction:column;align-items:center}

/* ── MY FAVOURITE SPOTS BOX ─── */
.spots-box{
  width:100%;max-width:480px;
  background:rgba(13,20,37,0.55);
  backdrop-filter:blur(16px);
  border:1px solid rgba(255,255,255,0.18);
  border-radius:var(--r2);
  padding:28px 24px;
  box-shadow:var(--shadow);
  position:sticky;top:2.5rem;
  animation:fadeIn .6s ease-out;
}
.spots-header{
  display:flex;align-items:center;gap:12px;
  margin-bottom:20px;padding-bottom:14px;
  border-bottom:1px solid var(--border);
}
.spots-header h2{
  font-size:1.3rem;font-weight:700;color:var(--text);
  letter-spacing:-0.01em;
}
.spots-header-icon{font-size:1.5rem}
.spots-grid{
  display:grid;grid-template-columns:repeat(2,1fr);
  gap:12px;
}
.spot-btn{
  background:rgba(255,255,255,0.06);
  border:1px solid var(--border2);
  border-radius:var(--r);
  color:var(--text);
  font-family:var(--font);
  font-size:0.95rem;font-weight:600;
  padding:12px 16px;
  cursor:pointer;
  display:flex;align-items:center;justify-content:space-between;
  transition:all .2s cubic-bezier(0.16,1,0.3,1);
}
.spot-btn:hover{
  background:rgba(96,165,250,0.22);
  border-color:var(--accent);
  transform:translateY(-2px);
  box-shadow:0 6px 20px rgba(96,165,250,0.3);
}
.spot-btn:active{transform:translateY(0)}
.spot-arrow{font-size:0.85rem;color:var(--accent);opacity:0.6;transition:opacity .2s,transform .2s}
.spot-btn:hover .spot-arrow{opacity:1;transform:translateX(4px)}

@media(max-width:1024px){
  .app-layout{flex-direction:column;align-items:center;justify-content:center}
  .spots-box{max-width:680px;position:static}
}

/* ── Header ─── */
header{text-align:center;margin-bottom:1.5rem}
.badge{
  display:inline-flex;align-items:center;gap:6px;
  margin-bottom:10px;
  font-size:0.68rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;
  color:var(--accent);background:rgba(96,165,250,0.15);
  border:1px solid rgba(96,165,250,0.3);border-radius:999px;
  padding:4px 12px;backdrop-filter:blur(8px);
}
.pulse{width:6px;height:6px;border-radius:50%;background:var(--accent);
  box-shadow:0 0 0 0 rgba(96,165,250,0.7);animation:pulseA 2s infinite}
@keyframes pulseA{
  0%{box-shadow:0 0 0 0 rgba(96,165,250,0.7)}
  70%{box-shadow:0 0 0 8px rgba(96,165,250,0)}
  100%{box-shadow:0 0 0 0 rgba(96,165,250,0)}
}
h1{font-size:clamp(2.6rem,7vw,3.6rem);font-weight:700;letter-spacing:-0.04em;line-height:1;text-shadow:0 4px 20px rgba(0,0,0,0.6)}
h1 em{font-style:normal;
  background:linear-gradient(135deg,#60a5fa,#818cf8 50%,#a78bfa);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.sub{color:var(--text2);font-size:0.88rem;margin-top:6px;letter-spacing:0.01em;text-shadow:0 2px 8px rgba(0,0,0,0.6)}

/* ── Search Bar (Placed Above Local Climate) ─── */
.search-block{width:100%;margin-bottom:1.8rem;position:relative}
.search-inner{display:flex;gap:8px;align-items:stretch}
.inp-wrap{position:relative;flex:1}
.search-ico{
  position:absolute;left:14px;top:50%;transform:translateY(-50%);
  width:16px;height:16px;stroke:var(--text2);pointer-events:none;
  transition:stroke .2s;
}
.inp-wrap:focus-within .search-ico{stroke:var(--accent)}
input{
  width:100%;background:rgba(13,20,37,0.55);color:var(--text);
  border:1px solid var(--border2);border-radius:var(--r);
  padding:13px 14px 13px 40px;
  font-family:var(--font);font-size:0.95rem;
  transition:border-color .2s,box-shadow .2s;outline:none;
  backdrop-filter:blur(12px);box-shadow:0 8px 32px rgba(0,0,0,0.3);
}
input::placeholder{color:var(--text3)}
input:focus{
  border-color:var(--accent);
  box-shadow:0 0 0 3px rgba(96,165,250,0.2),var(--glow);
}
.btn{
  background:var(--accent-d);color:#fff;
  font-family:var(--font);font-weight:600;font-size:0.88rem;
  border:none;border-radius:var(--r);
  padding:0 20px;cursor:pointer;white-space:nowrap;
  transition:background .15s,transform .1s,box-shadow .2s;
  box-shadow:0 4px 20px rgba(59,130,246,0.4);
  letter-spacing:0.01em;
}
.btn:hover{background:#2563eb;box-shadow:0 4px 28px rgba(59,130,246,0.6)}
.btn:active{transform:scale(0.96)}
.btn:disabled{opacity:0.45;cursor:not-allowed;transform:none}

/* ── Autocomplete dropdown ─── */
.dropdown{
  position:absolute;top:calc(100% + 6px);left:0;right:0;
  background:rgba(17,24,39,0.92);border:1px solid var(--border2);
  border-radius:var(--r);overflow:hidden;
  box-shadow:0 12px 48px rgba(0,0,0,0.6);backdrop-filter:blur(16px);
  z-index:100;display:none;
}
.dropdown.open{display:block}
.dd-item{
  display:flex;align-items:center;gap:10px;
  padding:11px 14px;cursor:pointer;
  transition:background .12s;font-size:0.9rem;
  border-bottom:1px solid var(--border);
}
.dd-item:last-child{border-bottom:none}
.dd-item:hover,.dd-item.active{background:rgba(96,165,250,0.15)}
.dd-flag{font-size:1.1rem;flex-shrink:0}
.dd-name{font-weight:500}
.dd-region{color:var(--text2);font-size:0.8rem}
.dd-country{margin-left:auto;font-size:0.76rem;color:var(--text3);font-family:var(--mono)}

/* ── Error ─── */
.error{
  display:none;margin-top:8px;font-size:0.83rem;color:var(--red);
  align-items:center;gap:6px;padding-left:2px;
}
.error.show{display:flex}

/* ── HERO GENERAL CLIMATE REPORT CARD ─── */
.hero-report-card{
  width:100%;
  border:1px solid rgba(255,255,255,0.18);border-radius:var(--r2);
  padding:20px;margin-bottom:1.8rem;
  box-shadow:0 20px 60px rgba(0,0,0,0.5);
  position:relative;overflow:hidden;
  animation:fadeIn .6s ease-out;
  background:rgba(13,20,37,0.55);
  backdrop-filter:blur(14px);
}
.hero-content{position:relative;z-index:2}

.report-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
.report-title-group{display:flex;align-items:center;gap:8px}
.report-icon{font-size:1.5rem;filter:drop-shadow(0 2px 8px rgba(0,0,0,0.4))}
.report-title{font-size:0.95rem;font-weight:700;letter-spacing:-0.01em;color:var(--text)}
.report-loc{font-size:0.75rem;color:var(--accent);font-weight:600}

.hero-actions{display:flex;align-items:center;gap:6px}
.action-btn{
  background:rgba(255,255,255,0.1);border:1px solid var(--border2);
  color:var(--text);font-family:var(--font);font-size:0.72rem;font-weight:600;
  padding:4px 10px;border-radius:999px;cursor:pointer;
  transition:all .2s;display:inline-flex;align-items:center;gap:4px;
}
.action-btn:hover{background:rgba(96,165,250,0.25);border-color:var(--accent)}

/* Interactive Navigation Tabs inside Hero Card */
.hero-tabs{display:flex;gap:6px;margin-bottom:14px;background:rgba(0,0,0,0.3);padding:4px;border-radius:12px;border:1px solid var(--border)}
.tab-btn{
  flex:1;background:transparent;border:none;color:var(--text2);
  font-family:var(--font);font-size:0.75rem;font-weight:600;
  padding:6px 8px;border-radius:8px;cursor:pointer;transition:all .2s;text-align:center;
}
.tab-btn.active{background:var(--accent-d);color:#fff;box-shadow:0 2px 10px rgba(59,130,246,0.4)}

/* Tab Contents */
.tab-content{display:none}
.tab-content.active{display:flex;flex-direction:column;gap:12px}

.report-main-row{display:flex;align-items:center;justify-content:space-between;background:rgba(255,255,255,0.06);padding:14px 16px;border-radius:var(--r);border:1px solid var(--border);backdrop-filter:blur(8px)}
.report-temp-box{display:flex;align-items:baseline;gap:4px}
.report-temp-num{font-size:2.5rem;font-weight:700;line-height:1;letter-spacing:-0.03em}
.report-temp-unit{font-size:1.1rem;color:var(--accent);font-weight:600;cursor:pointer}
.report-cond-box{text-align:right}
.report-cond-desc{font-size:0.95rem;font-weight:600;color:var(--text)}
.report-cond-sub{font-size:0.76rem;color:var(--text2)}

/* General Climate Text Block */
.report-summary-box{
  background:rgba(96,165,250,0.1);border:1px dashed rgba(96,165,250,0.3);
  border-radius:var(--r);padding:12px 14px;font-size:0.84rem;color:var(--text);line-height:1.48;
  backdrop-filter:blur(8px);
}
.report-summary-box strong{color:#fff;font-weight:700}

/* Clocks Section inside Hero */
.hero-clocks{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:2px}
.clock-box{
  background:rgba(6,10,18,0.55);border:1px solid var(--border);border-radius:var(--r);
  padding:8px 6px;text-align:center;backdrop-filter:blur(8px);
}
.clock-label{font-size:0.64rem;color:var(--text2);text-transform:uppercase;letter-spacing:0.08em;font-weight:600;margin-bottom:3px}
.clock-val{font-family:var(--mono);font-size:0.78rem;font-weight:600;color:var(--accent)}

/* Interactive Gauges Grid (Tab 2) */
.gauges-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.gauge-card{
  background:rgba(6,10,18,0.55);border:1px solid var(--border);
  border-radius:var(--r);padding:12px 10px;text-align:center;backdrop-filter:blur(8px);
}
.gauge-val{font-family:var(--mono);font-size:1.1rem;font-weight:700;color:var(--green);margin:4px 0 2px}
.gauge-lbl{font-size:0.65rem;color:var(--text2);text-transform:uppercase;letter-spacing:0.08em}

/* ── Spinner ─── */
.spinner{display:none;flex-direction:column;align-items:center;gap:10px;margin-bottom:1.5rem}
.spinner.show{display:flex}
.spin-ring{
  width:40px;height:40px;border:3px solid rgba(96,165,250,0.2);
  border-top-color:var(--accent);border-radius:50%;
  animation:spin 0.9s linear infinite;
}
@keyframes spin{to{transform:rotate(360deg)}}
.spin-lbl{color:var(--text);font-size:0.83rem;text-shadow:0 2px 8px rgba(0,0,0,0.6)}

/* ── Weather Card ─── */
.card{
  display:none;width:100%;
  border-radius:var(--r2);overflow:hidden;
  border:1px solid rgba(255,255,255,0.18);
  box-shadow:var(--shadow);
  background:rgba(13,20,37,0.55);
  backdrop-filter:blur(14px);
  animation:slideUp .5s cubic-bezier(0.16,1,0.3,1) forwards;
}
.card.show{display:block}
@keyframes slideUp{
  from{opacity:0;transform:translateY(24px) scale(0.98)}
  to{opacity:1;transform:translateY(0) scale(1)}
}

/* Canvas animation panel */
.wx-canvas-wrap{
  position:relative;height:210px;overflow:hidden;
  background:transparent;
}
#wx-canvas{display:block;width:100%;height:100%}
.canvas-overlay{
  position:absolute;inset:0;
  display:flex;flex-direction:column;justify-content:flex-end;
  padding:18px 20px;
  background:linear-gradient(to top, rgba(6,10,18,0.75) 0%, transparent 70%);
}
.overlay-cond{font-size:0.68rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:var(--accent);margin-bottom:4px}
.overlay-city{font-size:1.65rem;font-weight:700;letter-spacing:-0.03em}
.overlay-sub{font-size:0.8rem;color:var(--text2);margin-top:2px}
.wx-emoji{
  position:absolute;top:18px;right:20px;font-size:3.2rem;
  filter:drop-shadow(0 4px 12px rgba(0,0,0,0.5));
  animation:floatIcon 3s ease-in-out infinite;
}
@keyframes floatIcon{
  0%,100%{transform:translateY(0)}
  50%{transform:translateY(-6px)}
}

/* Card body */
.card-body{background:rgba(10,18,32,0.55);padding:20px}

/* Temp display */
.temp-block{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:18px}
.temp-main{display:flex;align-items:flex-start;gap:4px}
.temp-num{font-size:4.8rem;font-weight:300;letter-spacing:-0.05em;line-height:1}
.temp-unit{font-size:1.4rem;color:var(--accent);margin-top:8px;cursor:pointer;font-weight:600}
.feels-col{text-align:right;padding-top:8px}
.feels-lbl{font-size:0.7rem;color:var(--text2);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:3px}
.feels-val{font-size:1.1rem;font-weight:600;color:var(--text)}

/* Card Clocks Section */
.card-clocks-section{
  background:rgba(13,20,37,0.5);border:1px solid var(--border);
  border-radius:var(--r);padding:12px 14px;margin-bottom:18px;
}
.clocks-header{font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--text2);font-weight:600;margin-bottom:8px}
.clocks-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.c-clock-item{background:rgba(6,10,18,0.6);border:1px solid var(--border);border-radius:10px;padding:8px 6px;text-align:center}
.c-clock-title{font-size:0.62rem;color:var(--text2);margin-bottom:2px}
.c-clock-time{font-family:var(--mono);font-size:0.76rem;font-weight:600;color:var(--accent)}

/* Stats grid */
.stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:18px}
.stat-card{
  background:rgba(13,20,37,0.5);border:1px solid var(--border);
  border-radius:var(--r);padding:12px 10px;text-align:center;
  transition:border-color .2s,background .2s;
}
.stat-card:hover{border-color:var(--accent-b);background:var(--accent-t)}
.stat-ico{font-size:1.2rem;margin-bottom:4px}
.stat-val{font-family:var(--mono);font-size:0.88rem;font-weight:500;color:var(--text)}
.stat-lbl{font-size:0.66rem;color:var(--text2);text-transform:uppercase;letter-spacing:0.08em;margin-top:3px}

/* Wind bar */
.wind-section{
  background:rgba(13,20,37,0.5);border:1px solid var(--border);
  border-radius:var(--r);padding:14px 16px;margin-bottom:18px;
}
.wind-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.wind-title{font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;color:var(--text2)}
.wind-val{font-family:var(--mono);font-size:0.9rem;color:var(--accent)}
.compass-row{display:flex;align-items:center;gap:14px}
#compass-svg{width:56px;height:56px;flex-shrink:0}
.wind-bar-wrap{flex:1}
.wind-dir-lbl{font-size:0.78rem;color:var(--text2);margin-bottom:6px}
.wind-bar-bg{height:5px;background:var(--border2);border-radius:999px;overflow:hidden}
.wind-bar-fill{height:100%;background:linear-gradient(90deg,var(--accent-d),var(--accent));border-radius:999px;transition:width 1s cubic-bezier(0.34,1.56,0.64,1)}

/* Footer strip */
.card-foot{
  display:flex;align-items:center;justify-content:space-between;
  padding-top:14px;border-top:1px solid var(--border);
}
.daynight{display:flex;align-items:center;gap:6px;font-size:0.83rem;color:var(--text2)}
.foot-time{font-family:var(--mono);font-size:0.7rem;color:var(--text2)}

/* Footer */
footer{margin-top:3rem;font-size:0.73rem;color:var(--text2);text-align:center;text-shadow:0 2px 8px rgba(0,0,0,0.6)}
footer a{color:#fff;text-decoration:none;font-weight:600}
footer a:hover{color:var(--accent)}

@media(prefers-reduced-motion:reduce){
  *{animation-duration:0.01ms!important;transition-duration:0.01ms!important}
}
</style>
</head>
<body>

<!-- FULL HOMEPAGE BACKGROUND VIDEO LAYER USING PROJECT VIDEOS -->
<div class="home-bg-video-wrap">
  <video id="home-bg-video" autoplay loop muted playsinline src="/videos/sunny.mp4"></video>
  <div class="home-bg-overlay"></div>
</div>

<div class="app-layout">
<div class="page">

<header>
  <div class="badge"><span class="pulse"></span>Live Weather</div>
  <h1>Sky<em>Check</em></h1>
  <p class="sub">Real-time conditions &amp; Ambient Weather Cinema · Powered by Open-Meteo</p>
</header>

<!-- SEARCH BAR (Placed above General Climate Report) -->
<div class="search-block">
  <div class="search-inner">
    <div class="inp-wrap">
      <svg class="search-ico" fill="none" viewBox="0 0 24 24" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      <input id="city-input" type="text" placeholder="Search any city for climate & time…" autocomplete="off" spellcheck="false"/>
      <div class="dropdown" id="dropdown"></div>
    </div>
    <button class="btn" id="search-btn">Go</button>
  </div>
  <p class="error" id="error-msg">
    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
      <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
    <span id="error-text"></span>
  </p>
</div>

<!-- HERO GENERAL CLIMATE REPORT CARD WITH GLASSMORPHISM OVER VIDEO -->
<div class="hero-report-card" id="hero-report">
  <div class="hero-content">
    <div class="report-header">
      <div class="report-title-group">
        <span class="report-icon" id="h-icon">📍</span>
        <div>
          <div class="report-title">General Climate Report</div>
          <div class="report-loc" id="h-loc">Detecting location…</div>
        </div>
      </div>
      
      <div class="hero-actions">
        <button class="action-btn" id="unit-toggle-btn" title="Toggle °C / °F">🌡️ <span id="unit-lbl">°C</span></button>
        <button class="action-btn" id="refresh-loc-btn" title="Refresh Location">🔄 Sync</button>
      </div>
    </div>
    
    <!-- Interactive Tabs -->
    <div class="hero-tabs">
      <button class="tab-btn active" data-tab="tab-overview">📍 Overview</button>
      <button class="tab-btn" data-tab="tab-gauges">⚡ Comfort &amp; Radar</button>
    </div>

    <!-- TAB 1: Overview & Clocks -->
    <div class="tab-content active" id="tab-overview">
      <div class="report-main-row">
        <div class="report-temp-box">
          <span class="report-temp-num" id="h-temp">—</span>
          <span class="report-temp-unit" id="h-unit-display">°C</span>
        </div>
        <div class="report-cond-box">
          <div class="report-cond-desc" id="h-cond">Loading…</div>
          <div class="report-cond-sub" id="h-sub">Updating report</div>
        </div>
      </div>

      <div class="report-summary-box" id="h-report">
        <strong>General Climate:</strong> Analyzing live atmospheric conditions for your current location…
      </div>

      <div class="hero-clocks">
        <div class="clock-box">
          <div class="clock-label">Local Time</div>
          <div class="clock-val" id="h-clock-local">—:—:—</div>
        </div>
        <div class="clock-box">
          <div class="clock-label">IST (India)</div>
          <div class="clock-val" id="h-clock-ist">—:—:—</div>
        </div>
        <div class="clock-box">
          <div class="clock-label">UTC (Global)</div>
          <div class="clock-val" id="h-clock-utc">—:—:—</div>
        </div>
      </div>
    </div>

    <!-- TAB 2: Interactive Comfort & Radar Gauges -->
    <div class="tab-content" id="tab-gauges">
      <div class="gauges-grid">
        <div class="gauge-card">
          <div class="gauge-lbl">Air Comfort</div>
          <div class="gauge-val" id="g-comfort">Optimal</div>
        </div>
        <div class="gauge-card">
          <div class="gauge-lbl">Humidity Level</div>
          <div class="gauge-val" id="g-humidity" style="color:var(--accent)">—%</div>
        </div>
        <div class="gauge-card">
          <div class="gauge-lbl">UV Safety</div>
          <div class="gauge-val" id="g-uv" style="color:var(--yellow)">Moderate</div>
        </div>
      </div>
    </div>

  </div>
</div>

<div class="spinner" id="spinner">
  <div class="spin-ring"></div>
  <span class="spin-lbl">Fetching conditions &amp; animated scene…</span>
</div>

<!-- SEARCHED CITY WEATHER CARD -->
<div class="card" id="weather-card">
  <!-- Canvas animation representing corresponding climate -->
  <div class="wx-canvas-wrap">
    <canvas id="wx-canvas"></canvas>
    <div class="canvas-overlay">
      <div class="overlay-cond" id="o-cond"></div>
      <div class="overlay-city" id="o-city"></div>
      <div class="overlay-sub"  id="o-sub"></div>
    </div>
    <span class="wx-emoji" id="wx-emoji"></span>
  </div>

  <div class="card-body">
    <div class="temp-block">
      <div class="temp-main">
        <span class="temp-num" id="temp-num">—</span>
        <span class="temp-unit" id="c-unit-display">°C</span>
      </div>
      <div class="feels-col">
        <div class="feels-lbl">Feels like</div>
        <div class="feels-val" id="feels-val">—°</div>
      </div>
    </div>

    <!-- Live Clocks Panel for Searched City -->
    <div class="card-clocks-section">
      <div class="clocks-header">🕒 Real-Time World Clocks</div>
      <div class="clocks-grid">
        <div class="c-clock-item">
          <div class="c-clock-title">City Local Time</div>
          <div class="c-clock-time" id="c-clock-local">—:—:—</div>
        </div>
        <div class="c-clock-item">
          <div class="c-clock-title">IST (India)</div>
          <div class="c-clock-time" id="c-clock-ist">—:—:—</div>
        </div>
        <div class="c-clock-item">
          <div class="c-clock-title">UTC (Global)</div>
          <div class="c-clock-time" id="c-clock-utc">—:—:—</div>
        </div>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-ico">💨</div>
        <div class="stat-val" id="s-wind">—</div>
        <div class="stat-lbl">Wind km/h</div>
      </div>
      <div class="stat-card">
        <div class="stat-ico">💧</div>
        <div class="stat-val" id="s-hum">—</div>
        <div class="stat-lbl">Humidity %</div>
      </div>
      <div class="stat-card">
        <div class="stat-ico">🌐</div>
        <div class="stat-val" id="s-lat">—</div>
        <div class="stat-lbl">Latitude</div>
      </div>
    </div>

    <div class="wind-section">
      <div class="wind-header">
        <span class="wind-title">Wind Direction</span>
        <span class="wind-val" id="wind-dir-val">—</span>
      </div>
      <div class="compass-row">
        <svg id="compass-svg" viewBox="0 0 56 56">
          <circle cx="28" cy="28" r="26" fill="none" stroke="rgba(96,165,250,0.2)" stroke-width="1.5"/>
          <circle cx="28" cy="28" r="26" fill="none" stroke="rgba(96,165,250,0.08)" stroke-width="8"/>
          <text x="28" y="8"  text-anchor="middle" fill="#94a3b8" font-size="6" font-family="DM Mono">N</text>
          <text x="28" y="53" text-anchor="middle" fill="#94a3b8" font-size="6" font-family="DM Mono">S</text>
          <text x="5"  y="30" text-anchor="middle" fill="#94a3b8" font-size="6" font-family="DM Mono">W</text>
          <text x="51" y="30" text-anchor="middle" fill="#94a3b8" font-size="6" font-family="DM Mono">E</text>
          <g id="needle" style="transform-origin:28px 28px;transition:transform 1s cubic-bezier(.34,1.56,.64,1)">
            <polygon points="28,12 30.5,28 25.5,28" fill="#60a5fa" opacity="0.95"/>
            <polygon points="28,44 30.5,28 25.5,28" fill="#475569" opacity="0.7"/>
            <circle cx="28" cy="28" r="2.5" fill="#60a5fa"/>
          </g>
        </svg>
        <div class="wind-bar-wrap">
          <div class="wind-dir-lbl" id="wind-dir-lbl">—</div>
          <div class="wind-bar-bg"><div class="wind-bar-fill" id="wind-bar" style="width:0%"></div></div>
        </div>
      </div>
    </div>

    <div class="card-foot">
      <div class="daynight"><span id="dn-icon"></span><span id="dn-lbl"></span></div>
      <span class="foot-time" id="foot-time"></span>
    </div>
  </div>
</div>

<footer>Data from <a href="https://open-meteo.com" target="_blank">Open-Meteo</a> · Free &amp; Open</footer>

</div><!-- .page -->

<!-- MY FAVOURITE SPOTS BOX -->
<div class="spots-box">
  <div class="spots-header">
    <span class="spots-header-icon">⭐</span>
    <h2>My Favourite Spots</h2>
  </div>
  <div class="spots-grid">
    <button class="spot-btn" data-spot="Chennai" data-query="Chennai">
      <span>🇮🇳 Chennai</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="Mumbai" data-query="Mumbai">
      <span>🇮🇳 Mumbai</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="Delhi" data-query="Delhi">
      <span>🇮🇳 Delhi</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="Kolkatta" data-query="Kolkata">
      <span>🇮🇳 Kolkatta</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="Tokyo" data-query="Tokyo">
      <span>🇯🇵 Tokyo</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="Shibuya" data-query="Shibuya">
      <span>🇯🇵 Shibuya</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="New York" data-query="New York">
      <span>🇺🇸 New York</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="London" data-query="London">
      <span>🇬🇧 London</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="Denmark" data-query="Denmark">
      <span>🇩🇰 Denmark</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="Los Angeles" data-query="Los Angeles">
      <span>🇺🇸 Los Angeles</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="Los Vegas" data-query="Las Vegas">
      <span>🇺🇸 Los Vegas</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="Paris" data-query="Paris">
      <span>🇫🇷 Paris</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="Mexico" data-query="Mexico City">
      <span>🇲🇽 Mexico</span><span class="spot-arrow">→</span>
    </button>
    <button class="spot-btn" data-spot="Chicago" data-query="Chicago">
      <span>🇺🇸 Chicago</span><span class="spot-arrow">→</span>
    </button>
  </div>
</div>

</div><!-- .app-layout -->

<script>
// ── DOM References ────────────────────────────────────────────────
const $=id=>document.getElementById(id);
const input=$('city-input'), btn=$('search-btn'), spinner=$('spinner');
const card=$('weather-card'), errBox=$('error-msg'), errText=$('error-text');
const dropdown=$('dropdown');
const homeVideo=$('home-bg-video');

// Temperature Unit state (°C / °F)
let isFahrenheit = false;
let heroRawTempC = null;
let heroRawFeelsC = null;
let cardRawTempC = null;
let cardRawFeelsC = null;

// Active Timezones for Clocks
let heroTimezone = 'UTC';
let cardTimezone = 'UTC';

// ── Interactive Unit Switcher (°C / °F) ───────────────────────────
function convertTemp(tempC) {
  if (tempC == null) return '—';
  if (isFahrenheit) return Math.round((tempC * 9/5) + 32);
  return Math.round(tempC);
}

function toggleUnit() {
  isFahrenheit = !isFahrenheit;
  const unitStr = isFahrenheit ? '°F' : '°C';
  $('unit-lbl').textContent = unitStr;
  $('h-unit-display').textContent = unitStr;
  $('c-unit-display').textContent = unitStr;
  
  if (heroRawTempC != null) $('h-temp').textContent = convertTemp(heroRawTempC);
  if (cardRawTempC != null) $('temp-num').textContent = convertTemp(cardRawTempC);
  if (cardRawFeelsC != null) $('feels-val').textContent = convertTemp(cardRawFeelsC) + '°';
}
$('unit-toggle-btn').addEventListener('click', toggleUnit);
$('h-unit-display').addEventListener('click', toggleUnit);
$('c-unit-display').addEventListener('click', toggleUnit);


// ── Interactive Hero Tabs ──────────────────────────────────────────
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    $(btn.getAttribute('data-tab')).classList.add('active');
  });
});


// ── Local Project Video Background Switcher ───────────────────────
const LOCAL_VIDEOS = {
  sunny:   '/videos/sunny.mp4',
  cloudy:  '/videos/cloudy.mp4',
  rain:    '/videos/rain.mp4',
  night:   '/videos/night.mp4',
  thunder: '/videos/thunder_storm.mp4',
  snow:    '/videos/snow.mp4',
  fog:     '/videos/fog.mp4'
};

function updatePageBackgroundVideo(code, isDay) {
  let key = 'sunny';
  if ([95, 96, 99].includes(code)) key = 'thunder';
  else if ([71, 73, 75].includes(code)) key = 'snow';
  else if ([45, 48].includes(code)) key = 'fog';
  else if ([51,53,55,61,63,65,80,81,82].includes(code)) key = 'rain';
  else if (!isDay) key = 'night';
  else if ([1, 2, 3].includes(code)) key = 'cloudy';
  else key = 'sunny';

  const targetSrc = LOCAL_VIDEOS[key];
  const wrap = document.querySelector('.home-bg-video-wrap');
  if (wrap) {
    if (key === 'night') {
      wrap.classList.add('night-active');
    } else {
      wrap.classList.remove('night-active');
    }
  }
  
  if (homeVideo && !homeVideo.src.endsWith(targetSrc)) {
    homeVideo.style.opacity = '0.3';
    setTimeout(() => {
      homeVideo.src = targetSrc;
      homeVideo.play().catch(()=>{});
      homeVideo.style.opacity = (key === 'night') ? '0.95' : '0.85';
    }, 300);
  } else if (homeVideo) {
    homeVideo.style.opacity = (key === 'night') ? '0.95' : '0.85';
  }
}


// ── Global Clocks Ticker (IST, UTC & Local) ────────────────────────
function tickClocks() {
  const now = new Date();
  
  const istStr = now.toLocaleTimeString('en-US', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
  $('h-clock-ist').textContent = istStr;
  $('c-clock-ist').textContent = istStr;

  const utcStr = now.toLocaleTimeString('en-US', { timeZone: 'UTC', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
  $('h-clock-utc').textContent = utcStr;
  $('c-clock-utc').textContent = utcStr;

  try {
    const hLocal = now.toLocaleTimeString('en-US', { timeZone: heroTimezone, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
    $('h-clock-local').textContent = hLocal;
  } catch(e) { $('h-clock-local').textContent = utcStr; }

  try {
    const cLocal = now.toLocaleTimeString('en-US', { timeZone: cardTimezone, hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true });
    $('c-clock-local').textContent = cLocal;
  } catch(e) { $('c-clock-local').textContent = utcStr; }
}
setInterval(tickClocks, 1000);
tickClocks();


// ── User Location & General Climate Report ────────────────────────
async function initHeroReport() {
  $('h-loc').textContent = 'Syncing location…';
  if ('geolocation' in navigator) {
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        fetchHeroWeather('My Location', pos.coords.latitude, pos.coords.longitude);
      },
      (err) => { fetchHeroWeather('Chennai'); },
      { timeout: 8000 }
    );
  } else { fetchHeroWeather('Chennai'); }
}

$('refresh-loc-btn').addEventListener('click', initHeroReport);

async function fetchHeroWeather(city, lat=null, lon=null) {
  let url = '/api/weather?city=' + encodeURIComponent(city);
  if (lat != null && lon != null) url += '&lat=' + lat + '&lon=' + lon;
  try {
    const r = await fetch(url);
    if (!r.ok) return;
    const d = await r.json();
    populateHeroReport(d);
  } catch(e){}
}

function populateHeroReport(d) {
  $('h-icon').textContent = d.icon;
  $('h-loc').textContent  = d.city + (d.country ? ', ' + d.country : '');
  
  heroRawTempC = d.temperature;
  heroRawFeelsC = d.feels_like != null ? d.feels_like : d.temperature;
  
  $('h-temp').textContent = convertTemp(heroRawTempC);
  $('h-cond').textContent = d.condition;
  $('h-sub').textContent  = 'Feels like ' + convertTemp(heroRawFeelsC) + (isFahrenheit?'°F':'°C') + ' · Wind ' + (d.windspeed||0) + ' km/h';
  $('h-report').innerHTML = '<strong>General Climate Report:</strong> ' + d.report;
  
  if (d.humidity != null) $('g-humidity').textContent = d.humidity + '%';
  
  if (d.timezone) heroTimezone = d.timezone;
  updatePageBackgroundVideo(d.weather_code, d.is_day);
  tickClocks();
}

window.addEventListener('DOMContentLoaded', () => {
  initHeroReport();
  document.querySelectorAll('.spot-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const spotName = btn.getAttribute('data-spot');
      const queryName = btn.getAttribute('data-query');
      input.value = spotName;
      fetchWeather(queryName);
      if (window.innerWidth <= 880) {
        const card = $('weather-card');
        if (card) card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    });
  });
});


// ── Autocomplete ─────────────────────────────────────────────────
let acTimer=null, acIdx=-1, acResults=[];

input.addEventListener('input', ()=>{
  clearTimeout(acTimer);
  const q=input.value.trim();
  if(q.length<2){closeDropdown();return}
  acTimer=setTimeout(()=>fetchSuggestions(q), 260);
});

input.addEventListener('keydown', e=>{
  if(!dropdown.classList.contains('open')){
    if(e.key==='Enter') fetchWeather(input.value.trim());
    return;
  }
  const items=dropdown.querySelectorAll('.dd-item');
  if(e.key==='ArrowDown'){e.preventDefault();setAcIdx(acIdx+1,items)}
  else if(e.key==='ArrowUp'){e.preventDefault();setAcIdx(acIdx-1,items)}
  else if(e.key==='Enter'){
    e.preventDefault();
    if(acIdx>=0&&acIdx<acResults.length) selectResult(acResults[acIdx]);
    else {closeDropdown();fetchWeather(input.value.trim());}
  }
  else if(e.key==='Escape') closeDropdown();
});

function setAcIdx(i,items){
  acIdx=((i%items.length)+items.length)%items.length;
  items.forEach((el,idx)=>el.classList.toggle('active',idx===acIdx));
}

document.addEventListener('click', e=>{
  if(!e.target.closest('.search-block')) closeDropdown();
});

async function fetchSuggestions(q){
  try{
    const r=await fetch('/api/suggest?q='+encodeURIComponent(q));
    if(!r.ok) return;
    const data=await r.json();
    acResults=data;
    renderDropdown(data);
  }catch{}
}

function countryFlag(cc){
  if(!cc||cc.length!==2) return '🌍';
  return String.fromCodePoint(...[...cc.toUpperCase()].map(c=>127397+c.charCodeAt(0)));
}

function renderDropdown(items){
  if(!items.length){closeDropdown();return}
  acIdx=-1;
  dropdown.innerHTML=items.map((it,i)=>`
    <div class="dd-item" data-idx="${i}">
      <span class="dd-flag">${countryFlag(it.country_code)}</span>
      <span>
        <span class="dd-name">${it.name}</span>
        ${it.region?`<span class="dd-region">, ${it.region}</span>`:''}
      </span>
      <span class="dd-country">${it.country||''}</span>
    </div>`).join('');
  dropdown.querySelectorAll('.dd-item').forEach((el,i)=>{
    el.addEventListener('mousedown', e=>{e.preventDefault(); selectResult(acResults[i]);});
  });
  dropdown.classList.add('open');
}

function closeDropdown(){dropdown.classList.remove('open');acIdx=-1}

function selectResult(res){
  input.value=res.name+(res.region?', '+res.region:'')+(res.country?', '+res.country:'');
  closeDropdown();
  fetchWeather(res.name, res.latitude, res.longitude, res.country_code);
}


// ── Weather fetch ─────────────────────────────────────────────────
async function fetchWeather(city, lat=null, lon=null, cc=null){
  if(!city){showErr('Enter a city name.');return}
  clearErr(); card.classList.remove('show'); setLoading(true);
  let url;
  if(lat!=null&&lon!=null)
    url='/api/weather?city='+encodeURIComponent(city)+'&lat='+lat+'&lon='+lon;
  else
    url='/api/weather?city='+encodeURIComponent(city);
  try{
    const r=await fetch(url);
    let d; try{d=await r.json();}catch{throw new Error('Unexpected server response.')}
    if(!r.ok){showErr(d.detail||'Error '+r.status);return}
    populateCard(d);
  }catch(err){
    showErr(err.message||'Network error.');
  }finally{setLoading(false)}
}

// ── Compass helper ────────────────────────────────────────────────
function compassDir(deg){
  const dirs=['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
  return dirs[Math.round(((deg%360)+360)%360/22.5)%16];
}

// ── Populate Card ─────────────────────────────────────────────────
function populateCard(d){
  $('o-city').textContent  = d.city;
  $('o-sub').textContent   = [d.region,d.country].filter(Boolean).join(', ');
  $('o-cond').textContent  = d.condition;
  $('wx-emoji').textContent= d.icon;

  cardRawTempC = d.temperature;
  cardRawFeelsC = d.feels_like != null ? d.feels_like : d.temperature;

  $('temp-num').textContent = convertTemp(cardRawTempC);
  $('feels-val').textContent = convertTemp(cardRawFeelsC)+'°';

  $('s-wind').textContent = d.windspeed!=null?d.windspeed:'—';
  $('s-hum').textContent  = d.humidity!=null?d.humidity:'—';
  $('s-lat').textContent  = d.latitude;

  if (d.timezone) cardTimezone = d.timezone;
  updatePageBackgroundVideo(d.weather_code, d.is_day);
  tickClocks();

  const dir=d.wind_direction;
  if(dir!=null){
    $('needle').style.transform='rotate('+dir+'deg)';
    $('wind-dir-val').textContent=compassDir(dir)+' · '+dir+'°';
    $('wind-dir-lbl').textContent='Blowing from '+compassDir((dir+180)%360);
    const pct=Math.min(100,d.windspeed||0)*100/120;
    $('wind-bar').style.width=pct+'%';
  }

  $('dn-icon').textContent = d.is_day?'🌅':'🌙';
  $('dn-lbl').textContent  = d.is_day?'Daytime':'Night-time';
  $('foot-time').textContent='Updated '+new Date().toLocaleTimeString();

  card.classList.remove('show');
  void card.offsetWidth;
  card.classList.add('show');

  setTimeout(() => startCanvasScene(d), 50);
}


// ═══════════════════════════════════════════════════════════════
//  CANVAS WEATHER ANIMATIONS (TRANSPARENT PARTICLE OVERLAY)
// ═══════════════════════════════════════════════════════════════
let animFrame=null;
const cvs=$('wx-canvas');
const ctx=cvs.getContext('2d');

function resizeCanvas(){
  const w = cvs.offsetWidth || 480;
  const h = cvs.offsetHeight || 210;
  const dpr = window.devicePixelRatio || 1;
  cvs.width = w * dpr;
  cvs.height = h * dpr;
  ctx.scale(dpr, dpr);
}

function startCanvasScene(d){
  if(animFrame){cancelAnimationFrame(animFrame);animFrame=null}
  resizeCanvas();
  const W = cvs.offsetWidth || 480;
  const H = cvs.offsetHeight || 210;
  if(W <= 0 || H <= 0) return;
  
  const code=d.weather_code||0;
  const isDay=d.is_day;

  let scene='clear';
  if([0].includes(code))           scene=isDay?'sunny':'starry';
  else if([1,2].includes(code))    scene=isDay?'partlyCloud':'nightCloud';
  else if([3].includes(code))      scene='overcast';
  else if([45,48].includes(code))  scene='fog';
  else if([51,53,55,61,63,65,80,81,82].includes(code)) scene='rain';
  else if([71,73,75].includes(code)) scene='snow';
  else if([95,96,99].includes(code)) scene='thunder';

  if(scenes[scene]) scenes[scene](W,H);
}

const scenes={
  sunny(W,H){
    if(W <= 0 || H <= 0) return;
    let t=0;
    const rays=Array.from({length:12},(_,i)=>({angle:i*30,len:0}));
    function draw(){
      t+=0.012;
      ctx.clearRect(0,0,W,H);
      
      const hgR = Math.max(10, W*0.55);
      const hg=ctx.createRadialGradient(W*0.7,H*0.6,0,W*0.7,H*0.6,hgR);
      hg.addColorStop(0,'rgba(251,191,36,0.3)');hg.addColorStop(1,'transparent');
      ctx.fillStyle=hg;ctx.fillRect(0,0,W,H);
      
      const sx=W*0.72,sy=H*0.32,sr=28;
      [60,45,32].forEach((r,i)=>{
        const outerR = Math.max(sr + 1, r + sr);
        const g=ctx.createRadialGradient(sx,sy,sr,sx,sy,outerR);
        g.addColorStop(0,`rgba(251,191,36,${0.1-i*0.02})`);g.addColorStop(1,'transparent');
        ctx.fillStyle=g;ctx.beginPath();ctx.arc(sx,sy,outerR,0,Math.PI*2);ctx.fill();
      });
      
      const disk=ctx.createRadialGradient(sx-4,sy-4,2,sx,sy,sr);
      disk.addColorStop(0,'#fef3c7');disk.addColorStop(0.5,'#fbbf24');disk.addColorStop(1,'#f59e0b');
      ctx.fillStyle=disk;ctx.beginPath();ctx.arc(sx,sy,sr,0,Math.PI*2);ctx.fill();
      
      rays.forEach((ray,i)=>{
        const a=(ray.angle+t*15)*Math.PI/180;
        ray.len=sr+18+Math.sin(t*2+i)*6;
        ctx.save();ctx.translate(sx,sy);ctx.rotate(a);
        ctx.strokeStyle=`rgba(251,191,36,${0.35+Math.sin(t+i)*0.1})`;
        ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(sr+4,0);ctx.lineTo(ray.len+sr,0);ctx.stroke();
        ctx.restore();
      });
      drawClouds(W,H,t,0.65);
      animFrame=requestAnimationFrame(draw);
    }
    draw();
  },

  partlyCloud(W,H){
    if(W <= 0 || H <= 0) return;
    let t=0;
    function draw(){
      t+=0.008;
      ctx.clearRect(0,0,W,H);
      
      const sx=W*0.72,sy=H*0.28,sr=20;
      const g2=ctx.createRadialGradient(sx,sy,0,sx,sy,50);
      g2.addColorStop(0,'rgba(251,191,36,0.45)');g2.addColorStop(1,'transparent');
      ctx.fillStyle=g2;ctx.fillRect(0,0,W,H);
      ctx.fillStyle='#fbbf24';ctx.beginPath();ctx.arc(sx,sy,sr,0,Math.PI*2);ctx.fill();
      drawClouds(W,H,t,0.9);
      animFrame=requestAnimationFrame(draw);
    }
    draw();
  },

  starry(W,H){
    if(W <= 0 || H <= 0) return;
    const stars=Array.from({length:80},()=>({
      x:Math.random()*W,y:Math.random()*H,
      r:Math.random()*1.5+0.3,
      phase:Math.random()*Math.PI*2,speed:Math.random()*0.02+0.008
    }));
    const moon={x:W*0.72,y:H*0.28};
    let t=0;
    function draw(){
      t+=0.01;
      ctx.clearRect(0,0,W,H);
      const mg=ctx.createRadialGradient(moon.x,moon.y,10,moon.x,moon.y,60);
      mg.addColorStop(0,'rgba(219,234,254,0.25)');mg.addColorStop(1,'transparent');
      ctx.fillStyle=mg;ctx.fillRect(0,0,W,H);
      ctx.fillStyle='#dbeafe';ctx.beginPath();ctx.arc(moon.x,moon.y,22,0,Math.PI*2);ctx.fill();
      ctx.fillStyle='#060d1a';ctx.beginPath();ctx.arc(moon.x+8,moon.y-4,18,0,Math.PI*2);ctx.fill();
      stars.forEach(s=>{
        const alpha=0.5+Math.sin(t*s.speed*100+s.phase)*0.45;
        ctx.fillStyle=`rgba(219,234,254,${alpha})`;
        ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);ctx.fill();
      });
      animFrame=requestAnimationFrame(draw);
    }
    draw();
  },

  nightCloud(W,H){
    if(W <= 0 || H <= 0) return;
    let t=0;
    const stars=Array.from({length:40},()=>({
      x:Math.random()*W,y:Math.random()*H*0.5,
      r:Math.random()*1.2+0.3,phase:Math.random()*Math.PI*2
    }));
    function draw(){
      t+=0.008;
      ctx.clearRect(0,0,W,H);
      stars.forEach(s=>{
        const a=0.4+Math.sin(t*0.8+s.phase)*0.3;
        ctx.fillStyle=`rgba(219,234,254,${a})`;
        ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);ctx.fill();
      });
      drawClouds(W,H,t,'#1c2840',0.95);
      animFrame=requestAnimationFrame(draw);
    }
    draw();
  },

  overcast(W,H){
    if(W <= 0 || H <= 0) return;
    let t=0;
    function draw(){
      t+=0.005;
      ctx.clearRect(0,0,W,H);
      drawHeavyClouds(W,H,t);
      animFrame=requestAnimationFrame(draw);
    }
    draw();
  },

  rain(W,H){
    if(W <= 0 || H <= 0) return;
    const drops=Array.from({length:130},()=>resetDrop(W,H,true));
    let t=0;
    function draw(){
      t+=1;
      ctx.clearRect(0,0,W,H);
      drawHeavyClouds(W,H,t*0.005);
      ctx.strokeStyle='rgba(147,197,253,0.7)';ctx.lineWidth=1.2;
      drops.forEach(d=>{
        ctx.beginPath();
        ctx.moveTo(d.x,d.y);
        ctx.lineTo(d.x+d.vx*3,d.y+d.len);
        ctx.stroke();
        d.x+=d.vx;d.y+=d.vy;
        if(d.y>H) Object.assign(d,resetDrop(W,H));
      });
      if(t%8===0){
        const px=Math.random()*W;
        ctx.strokeStyle='rgba(147,197,253,0.35)';ctx.lineWidth=1;
        ctx.beginPath();ctx.ellipse(px,H-4,6,2,0,0,Math.PI*2);ctx.stroke();
      }
      animFrame=requestAnimationFrame(draw);
    }
    draw();
  },

  snow(W,H){
    if(W <= 0 || H <= 0) return;
    const flakes=Array.from({length:90},()=>resetFlake(W,H,true));
    let t=0;
    function draw(){
      t+=0.012;
      ctx.clearRect(0,0,W,H);
      drawClouds(W,H,t*0.4,'#1e2a3a',0.8);
      flakes.forEach(f=>{
        f.x+=Math.sin(t+f.phase)*0.5;
        f.y+=f.vy;
        ctx.save();ctx.globalAlpha=f.alpha;
        ctx.fillStyle='#ffffff';
        ctx.beginPath();ctx.arc(f.x,f.y,f.r,0,Math.PI*2);ctx.fill();
        ctx.restore();
        if(f.y>H) Object.assign(f,resetFlake(W,H));
      });
      animFrame=requestAnimationFrame(draw);
    }
    draw();
  },

  thunder(W,H){
    if(W <= 0 || H <= 0) return;
    let t=0, flashTimer=0, flashAlpha=0, boltPts=[];
    function newBolt(){
      const x=W*0.3+Math.random()*W*0.4;
      const pts=[[x,H*0.1]];
      let cx=x,cy=H*0.1;
      while(cy<H*0.8){cy+=18+Math.random()*14;cx+=Math.random()*40-20;pts.push([cx,cy])}
      return pts;
    }
    function draw(){
      t+=1;
      ctx.clearRect(0,0,W,H);
      drawHeavyClouds(W,H,t*0.004);
      for(let i=0;i<60;i++){
        const rx=Math.random()*W,ry=Math.random()*H;
        ctx.strokeStyle='rgba(100,160,220,0.3)';ctx.lineWidth=1;
        ctx.beginPath();ctx.moveTo(rx,ry);ctx.lineTo(rx-2,ry+12);ctx.stroke();
      }
      if(flashAlpha>0){
        ctx.fillStyle=`rgba(200,220,255,${flashAlpha*0.25})`;
        ctx.fillRect(0,0,W,H);
        if(boltPts.length>1){
          ctx.strokeStyle=`rgba(220,240,255,${flashAlpha})`;
          ctx.lineWidth=2.5+flashAlpha*2;
          ctx.shadowColor='rgba(180,220,255,0.9)';ctx.shadowBlur=14;
          ctx.beginPath();ctx.moveTo(boltPts[0][0],boltPts[0][1]);
          boltPts.slice(1).forEach(p=>ctx.lineTo(p[0],p[1]));
          ctx.stroke();
          ctx.shadowBlur=0;
        }
        flashAlpha=Math.max(0,flashAlpha-0.06);
      }
      flashTimer++;
      if(flashTimer>80+Math.random()*100){flashTimer=0;flashAlpha=1;boltPts=newBolt()}
      animFrame=requestAnimationFrame(draw);
    }
    draw();
  },

  fog(W,H){
    if(W <= 0 || H <= 0) return;
    let t=0;
    const layers=Array.from({length:5},(_,i)=>({
      y:H*(0.2+i*0.15),speed:0.18+i*0.06,offset:Math.random()*W
    }));
    function draw(){
      t+=0.006;
      ctx.clearRect(0,0,W,H);
      layers.forEach((l,i)=>{
        l.offset-=l.speed;
        if(l.offset<-W*2)l.offset=W;
        const fg=ctx.createLinearGradient(l.offset,0,l.offset+W*2,0);
        const alpha=0.08+i*0.04;
        fg.addColorStop(0,'transparent');
        fg.addColorStop(0.2,`rgba(203,213,225,${alpha})`);
        fg.addColorStop(0.5,`rgba(203,213,225,${alpha*1.5})`);
        fg.addColorStop(0.8,`rgba(203,213,225,${alpha})`);
        fg.addColorStop(1,'transparent');
        ctx.fillStyle=fg;
        const ht=40+i*12;
        ctx.beginPath();
        ctx.ellipse(l.offset+W,l.y,Math.max(1,W*1.2),Math.max(1,ht),0,0,Math.PI*2);
        ctx.fill();
      });
      animFrame=requestAnimationFrame(draw);
    }
    draw();
  }
};

function drawClouds(W,H,t,color='#ffffff',opacity=0.45){
  if(!W || !H || W <= 0 || H <= 0) return;
  const clouds=[
    {x:0.15,y:0.18,s:1,spd:0.008},
    {x:0.55,y:0.12,s:0.75,spd:0.005},
    {x:0.8, y:0.22,s:0.6, spd:0.007},
  ];
  clouds.forEach(c=>{
    const modW = W * 1.3;
    const cx = modW > 0 ? ((c.x*W + t*W*c.spd) % modW) - W*0.15 : 0;
    const cy = c.y*H; const s = c.s;
    if(isNaN(cx) || isNaN(cy)) return;
    ctx.save();ctx.globalAlpha=opacity;ctx.fillStyle=color;
    ctx.beginPath();
    ctx.arc(cx,cy,Math.max(1,30*s),0,Math.PI*2);
    ctx.arc(cx+28*s,cy-10*s,Math.max(1,22*s),0,Math.PI*2);
    ctx.arc(cx+52*s,cy,Math.max(1,26*s),0,Math.PI*2);
    ctx.arc(cx+36*s,cy+12*s,Math.max(1,18*s),0,Math.PI*2);
    ctx.arc(cx+14*s,cy+12*s,Math.max(1,16*s),0,Math.PI*2);
    ctx.fill();ctx.restore();
  });
}

function drawHeavyClouds(W,H,t){
  if(!W || !H || W <= 0 || H <= 0) return;
  const clouds=[
    {x:0.05,y:0.1,s:1.4,spd:0.004},
    {x:0.4, y:0.06,s:1.2,spd:0.003},
    {x:0.75,y:0.12,s:1.1,spd:0.005},
  ];
  clouds.forEach(c=>{
    const modW = W * 1.4;
    const cx = modW > 0 ? ((c.x*W + t*W*c.spd*100) % modW) - W*0.2 : 0;
    const cy = c.y*H; const s = c.s;
    const rad = Math.max(1, 60*s);
    const gradX = cx + 26*s;
    if(isNaN(gradX) || isNaN(cy) || isNaN(rad)) return;
    const cg=ctx.createRadialGradient(gradX,cy,0,gradX,cy,rad);
    cg.addColorStop(0,'rgba(30,41,59,0.7)');cg.addColorStop(1,'rgba(15,23,42,0.85)');
    ctx.save();ctx.globalAlpha=0.85;ctx.fillStyle=cg;
    ctx.beginPath();
    ctx.arc(cx,cy,Math.max(1,38*s),0,Math.PI*2);
    ctx.arc(cx+34*s,cy-14*s,Math.max(1,28*s),0,Math.PI*2);
    ctx.arc(cx+64*s,cy,Math.max(1,32*s),0,Math.PI*2);
    ctx.arc(cx+46*s,cy+16*s,Math.max(1,22*s),0,Math.PI*2);
    ctx.arc(cx+18*s,cy+14*s,Math.max(1,20*s),0,Math.PI*2);
    ctx.fill();ctx.restore();
  });
}

function resetDrop(W,H,init=false){
  return{
    x:Math.random()*W,
    y:init?Math.random()*H:-10,
    vx:-1,vy:14+Math.random()*8,
    len:12+Math.random()*8
  };
}
function resetFlake(W,H,init=false){
  return{
    x:Math.random()*W,
    y:init?Math.random()*H:-8,
    r:1+Math.random()*2.5,
    vy:0.6+Math.random()*1.2,
    alpha:0.5+Math.random()*0.5,
    phase:Math.random()*Math.PI*2
  };
}

// ── Helpers ────────────────────────────────────────────────────────
function showErr(msg){errText.textContent=msg;errBox.classList.add('show')}
function clearErr(){errBox.classList.remove('show')}
function setLoading(on){spinner.classList.toggle('show',on);btn.disabled=on}

// ── Events ─────────────────────────────────────────────────────────
btn.addEventListener('click',()=>fetchWeather(input.value.trim()));
input.focus();
</script>
</body>
</html>"""


# ══════════════════════════════════════════════════════
#  BACKEND
# ══════════════════════════════════════════════════════
from contextlib import asynccontextmanager

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
_client: httpx.AsyncClient | None = None

def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=10,
            headers={"User-Agent": "SkyCheck-Premium/2.0"},
            follow_redirects=True,
        )
    return _client

@asynccontextmanager
async def lifespan(application: FastAPI):
    loop = asyncio.get_running_loop()
    def handle_exception(l, context):
        exc = context.get("exception")
        if isinstance(exc, ConnectionResetError) or (isinstance(exc, OSError) and getattr(exc, 'winerror', None) == 10054):
            return
        l.default_exception_handler(context)
    loop.set_exception_handler(handle_exception)
    yield
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()

app = FastAPI(title="SkyCheck Premium", docs_url=None, redoc_url=None, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])

@app.middleware("http")
async def suppress_connection_errors(request: Request, call_next):
    try:
        return await call_next(request)
    except (ConnectionResetError, OSError) as e:
        if getattr(e, 'winerror', None) == 10054 or isinstance(e, ConnectionResetError):
            return Response(status_code=499)
        raise e

WMO = {
    0:  {"description":"Clear sky",          "icon":"☀️"},
    1:  {"description":"Mainly clear",       "icon":"🌤️"},
    2:  {"description":"Partly cloudy",      "icon":"⛅"},
    3:  {"description":"Overcast",           "icon":"☁️"},
    45: {"description":"Foggy",              "icon":"🌫️"},
    48: {"description":"Icy fog",            "icon":"🌫️"},
    51: {"description":"Light drizzle",      "icon":"🌦️"},
    53: {"description":"Drizzle",            "icon":"🌦️"},
    55: {"description":"Heavy drizzle",      "icon":"🌧️"},
    61: {"description":"Slight rain",        "icon":"🌧️"},
    63: {"description":"Rain",               "icon":"🌧️"},
    65: {"description":"Heavy rain",         "icon":"🌧️"},
    71: {"description":"Slight snow",        "icon":"🌨️"},
    73: {"description":"Snow",               "icon":"❄️"},
    75: {"description":"Heavy snow",         "icon":"❄️"},
    80: {"description":"Slight showers",     "icon":"🌦️"},
    81: {"description":"Showers",            "icon":"🌧️"},
    82: {"description":"Violent showers",    "icon":"⛈️"},
    95: {"description":"Thunderstorm",       "icon":"⛈️"},
    96: {"description":"Thunderstorm+hail",  "icon":"⛈️"},
    99: {"description":"Thunderstorm+hail",  "icon":"⛈️"},
}

GEO_URL     = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTMLResponse(content=HTML)


@app.get("/videos/{video_name}")
async def get_video(video_name: str):
    clean_name = os.path.basename(video_name)
    file_path = os.path.join(ROOT_DIR, clean_name)
    if os.path.exists(file_path) and clean_name.endswith(".mp4"):
        return FileResponse(file_path, media_type="video/mp4")
    raise HTTPException(404, "Video file not found")


@app.get("/api/suggest")
async def suggest(q: str = Query(..., min_length=1)):
    """Autocomplete: return up to 6 city suggestions."""
    try:
        client = get_client()
        r = await client.get(GEO_URL, params={"name": q, "count": 6, "language": "en"})
        r.raise_for_status()
        data = r.json()
    except Exception:
        return JSONResponse([])
    results = []
    for loc in data.get("results", []):
        results.append({
            "name":         loc.get("name",""),
            "region":       loc.get("admin1",""),
            "country":      loc.get("country",""),
            "country_code": loc.get("country_code",""),
            "latitude":     loc.get("latitude"),
            "longitude":    loc.get("longitude"),
        })
    return JSONResponse(results)


@app.get("/api/weather")
async def get_weather(
    city: str = Query(..., min_length=1),
    lat: float | None = Query(None),
    lon: float | None = Query(None),
):
    client = get_client()

    # Reverse geocode or fetch coordinates if needed
    if lat is not None and lon is not None and (city.lower() in ["my location", "current location", "auto", ""] or not city):
        try:
            rev = await client.get(f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en")
            if rev.status_code == 200:
                rev_data = rev.json()
                name = rev_data.get("locality") or rev_data.get("city") or rev_data.get("localityInfo", {}).get("administrative", [{}])[0].get("name") or "Your Area"
                country = rev_data.get("countryName", "")
                region = rev_data.get("principalSubdivision", "")
            else:
                name, country, region = "Your Area", "", ""
        except Exception:
            name, country, region = "Your Area", "", ""
    elif lat is None or lon is None:
        try:
            geo = await client.get(GEO_URL, params={"name": city, "count": 1, "language": "en"})
            geo.raise_for_status()
            geo_data = geo.json()
        except httpx.TimeoutException:
            raise HTTPException(504, "Geocoding timed out.")
        except Exception as e:
            raise HTTPException(502, f"Geocoding error: {e}")
        if not geo_data.get("results"):
            raise HTTPException(404, f"City '{city}' not found.")
        loc     = geo_data["results"][0]
        lat     = loc["latitude"]
        lon     = loc["longitude"]
        name    = loc.get("name", city)
        country = loc.get("country", "")
        region  = loc.get("admin1", "")
    else:
        name, country, region = city, "", ""

    # Fetch weather with timezone and detailed fields
    try:
        wx = await client.get(WEATHER_URL, params={
            "latitude": lat, "longitude": lon,
            "current_weather": "true", "wind_speed_unit": "kmh",
            "timezone": "auto",
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,weather_code,is_day",
        })
        wx.raise_for_status()
        wx_data = wx.json()
    except httpx.TimeoutException:
        raise HTTPException(504, "Weather service timed out.")
    except Exception as e:
        raise HTTPException(502, f"Weather error: {e}")

    if "current" in wx_data:
        c = wx_data["current"]
        temp, wind_spd = c.get("temperature_2m"), c.get("wind_speed_10m")
        wind_dir, wmo_code, is_day = c.get("wind_direction_10m"), c.get("weather_code"), c.get("is_day", 1)
        feels_like = c.get("apparent_temperature")
        humidity = c.get("relative_humidity_2m")
    elif "current_weather" in wx_data:
        c = wx_data["current_weather"]
        temp, wind_spd = c.get("temperature"), c.get("windspeed")
        wind_dir, wmo_code, is_day = c.get("winddirection"), c.get("weathercode"), c.get("is_day", 1)
        feels_like = temp
        humidity = None
    else:
        raise HTTPException(502, "Unexpected weather response format.")

    wmo_info = WMO.get(int(wmo_code), {"description":"Unknown","icon":"🌡️"}) if wmo_code is not None else {"description":"Unknown","icon":"🌡️"}
    timezone_name = wx_data.get("timezone", "UTC")
    utc_offset = wx_data.get("utc_offset_seconds", 0)

    # Generate Human-Friendly General Climate Report
    cond_desc = wmo_info["description"]
    if temp is not None:
        if temp > 32:
            temp_feel = "Hot and atmospheric"
        elif temp > 25:
            temp_feel = "Pleasantly warm and fair"
        elif temp > 15:
            temp_feel = "Mild and comfortable"
        elif temp > 5:
            temp_feel = "Cool and brisk"
        else:
            temp_feel = "Cold and chilly"
    else:
        temp_feel = "Moderate"

    report_text = f"Experiencing a {temp_feel.lower()} climate in {name}. Currently {cond_desc.lower()} with wind speeds around {wind_spd or 0} km/h."
    if humidity:
        report_text += f" Relative humidity level is approximately {humidity}%."
    if feels_like is not None and abs(feels_like - (temp or 0)) > 2:
        report_text += f" Thermal sensation feels closer to {round(feels_like)}°C due to atmospheric factors."

    return {
        "city":          name,
        "region":        region,
        "country":       country,
        "latitude":      round(float(lat), 4),
        "longitude":     round(float(lon), 4),
        "temperature":   temp,
        "feels_like":    feels_like,
        "humidity":      humidity,
        "windspeed":     wind_spd,
        "wind_direction":round(float(wind_dir)) if wind_dir is not None else None,
        "condition":     cond_desc,
        "icon":          wmo_info["icon"],
        "weather_code":  int(wmo_code) if wmo_code is not None else 0,
        "is_day":        bool(is_day),
        "timezone":      timezone_name,
        "utc_offset":    utc_offset,
        "report":        report_text,
    }


# ══════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    PORT = 8082
    URL  = f"http://localhost:{PORT}"

    try: sys.stdout.reconfigure(encoding='utf-8')
    except: pass

    print(f"""
╔══════════════════════════════════════════════╗
║       SkyCheck Premium is starting up…       ║
╠══════════════════════════════════════════════╣
║  Open → {URL:<35}║
║  Stop → Ctrl + C                             ║
╚══════════════════════════════════════════════╝
""")

    def _open():
        import time; time.sleep(1.5); webbrowser.open(URL)
    threading.Thread(target=_open, daemon=True).start()

    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
