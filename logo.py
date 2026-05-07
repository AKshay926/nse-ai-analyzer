LOGO_HTML = """
<style>
* { margin:0; padding:0; box-sizing:border-box; }
.logo-wrapper {
    background: transparent;
    display: flex;
    align-items: center;
    gap: 16px;
    font-family: Arial, sans-serif;
    padding: 8px 0;
}
.bolt-wrap {
    position: relative;
    width: 70px;
    height: 90px;
    flex-shrink: 0;
}
.bolt {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 64px;
    color: #00cfff;
    filter: drop-shadow(0 0 6px #00cfff) drop-shadow(0 0 18px #00cfff) drop-shadow(0 0 40px #0099ff);
    animation: boltFlicker 3s ease-in-out infinite;
    line-height: 1;
}
.bolt-ring {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    border-radius: 50%;
    border: 1px solid #00cfff;
    opacity: 0;
    animation: ringPulse 3s ease-out infinite;
}
.bolt-ring:nth-child(1) { width: 40px; height: 40px; animation-delay: 0s; }
.bolt-ring:nth-child(2) { width: 40px; height: 40px; animation-delay: 1s; }
.bolt-ring:nth-child(3) { width: 40px; height: 40px; animation-delay: 2s; }
@keyframes boltFlicker {
    0%,100% { opacity:1; filter: drop-shadow(0 0 6px #00cfff) drop-shadow(0 0 18px #00cfff) drop-shadow(0 0 40px #0099ff); }
    89% { opacity:0.5; filter: drop-shadow(0 0 2px #00cfff); }
    90% { opacity:1; }
}
@keyframes ringPulse {
    0% { width:40px; height:40px; opacity:0.7; }
    100% { width:110px; height:110px; opacity:0; }
}
.brand-name {
    font-size: 48px;
    font-weight: 900;
    font-style: italic;
    color: #ffffff;
    letter-spacing: -1px;
    line-height: 1;
    text-shadow: 0 0 10px rgba(255,255,255,0.9), 0 0 20px rgba(0,180,255,0.6), 0 0 40px rgba(0,120,255,0.4);
    animation: textGlow 3s ease-in-out infinite;
    display: flex;
    align-items: center;
    gap: 4px;
}
@keyframes textGlow {
    0%,100% { text-shadow: 0 0 10px rgba(255,255,255,0.9), 0 0 20px rgba(0,180,255,0.6), 0 0 40px rgba(0,120,255,0.4); }
    50% { text-shadow: 0 0 16px #fff, 0 0 32px rgba(0,200,255,0.9), 0 0 60px rgba(0,150,255,0.6); }
}
.brand-sub {
    font-size: 10px;
    letter-spacing: 3px;
    color: #00cfff;
    text-transform: uppercase;
    opacity: 0.75;
    text-shadow: 0 0 8px #00cfff;
    margin-top: 2px;
}
.pulse-line {
    stroke-dasharray: 300;
    stroke-dashoffset: 300;
    animation: drawPulse 2s ease forwards, pulseFade 3s ease-in-out 2s infinite;
}
@keyframes drawPulse { to { stroke-dashoffset: 0; } }
@keyframes pulseFade {
    0%,100% { opacity:1; filter: drop-shadow(0 0 3px #00cfff); }
    50% { opacity:0.5; filter: drop-shadow(0 0 8px #00cfff); }
}
</style>

<div class="logo-wrapper">
  <div class="bolt-wrap">
    <div class="bolt-ring"></div>
    <div class="bolt-ring"></div>
    <div class="bolt-ring"></div>
    <div class="bolt">&#9889;</div>
  </div>
  <div>
    <div class="brand-name">
      PulseIQ
      <svg width="80" height="34" viewBox="0 0 110 44" fill="none" xmlns="http://www.w3.org/2000/svg" style="display:inline-block;vertical-align:middle;">
        <polyline class="pulse-line"
          points="0,22 15,22 22,8 28,36 36,4 44,38 50,22 62,22 68,14 74,30 80,22 110,22"
          stroke="#00cfff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"
          style="filter: drop-shadow(0 0 4px #00cfff) drop-shadow(0 0 10px #0099ff);"/>
      </svg>
    </div>
    <div class="brand-sub">AI-Powered Option Chain Intelligence</div>
  </div>
</div>
"""