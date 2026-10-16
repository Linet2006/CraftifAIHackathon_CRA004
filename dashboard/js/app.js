/**
 * SentinelAI - Operations Dashboard Frontend Application
 * Handles live telemetry polling, audio warnings, interactive geofence editing,
 * and hardware actuator control.
 */

let audioAlertEnabled = true;
let audioContext = null;
let lastBreachState = false;
let isEditMode = false;
let customZonePoints = [];

// Initialize Web Audio API for industrial alarm chimes
function initAudio() {
  if (!audioContext) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
  }
}

function playWarningTone(frequency = 880, duration = 0.35) {
  if (!audioAlertEnabled) return;
  try {
    initAudio();
    if (audioContext.state === 'suspended') {
      audioContext.resume();
    }
    const osc = audioContext.createOscillator();
    const gain = audioContext.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(frequency, audioContext.currentTime);
    osc.frequency.exponentialRampToValueAtTime(frequency * 1.5, audioContext.currentTime + duration);
    
    gain.gain.setValueAtTime(0.15, audioContext.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);

    osc.connect(gain);
    gain.connect(audioContext.destination);

    osc.start();
    osc.stop(audioContext.currentTime + duration);
  } catch (e) {
    console.warn("Audio chime prevented:", e);
  }
}

// Polling Loop for Live Telemetry
async function fetchTelemetry() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) return;
    const stats = await res.json();

    // Update Telemetry Header & Indicators
    document.getElementById('fps-counter').innerText = stats.fps.toFixed(1);
    document.getElementById('latency-counter').innerText = stats.latency_ms.toFixed(1) + ' ms';
    document.getElementById('worker-counter').innerText = stats.active_workers;
    document.getElementById('compliance-metric').innerText = stats.ppe_compliance_pct.toFixed(0) + '%';
    document.getElementById('violation-metric').innerText = stats.total_violations;

    const hudBreachPill = document.getElementById('hud-breach-pill');
    if (stats.danger_zone_breached) {
      hudBreachPill.classList.remove('hidden');
      hudBreachPill.classList.add('danger');
      hudBreachPill.innerText = 'CRITICAL: ROBOTIC CELL BREACH DETECTED';

      if (!lastBreachState) {
        playWarningTone(950, 0.5);
      }
      lastBreachState = true;
    } else {
      hudBreachPill.classList.remove('danger');
      hudBreachPill.classList.add('hidden');
      lastBreachState = false;
    }

    // Update Hardware Actuators
    const act = stats.actuator_status || {};
    updateActuatorUI('siren-item', act.siren_active, act.siren_active ? 'ACTIVE (2.4kHz)' : 'STANDBY');
    updateActuatorUI('strobe-item', act.strobe_active, act.strobe_active ? 'FLASHING RED' : 'STANDBY');
    updateActuatorUI('relay-item', act.machine_estop_interlock, act.machine_estop_interlock ? 'TRIPPED (OPEN)' : 'ARMED (CLOSED)');

    const espItem = document.getElementById('esp32-status');
    if (act.hardware_connected) {
      espItem.innerText = 'ONLINE (UART)';
      espItem.style.color = 'var(--accent-emerald)';
    } else {
      espItem.innerText = 'SIMULATED (BUS)';
      espItem.style.color = 'var(--accent-cyan)';
    }

  } catch (err) {
    console.error("Telemetry fetch error:", err);
  }
}

function updateActuatorUI(elemId, isActive, statusText) {
  const elem = document.getElementById(elemId);
  if (!elem) return;
  const textElem = elem.querySelector('.actuator-status-text');
  if (isActive) {
    elem.classList.add('active');
  } else {
    elem.classList.remove('active');
  }
  if (textElem) textElem.innerText = statusText;
}

// Polling Loop for Incidents
async function fetchIncidents() {
  try {
    const res = await fetch('/api/incidents');
    if (!res.ok) return;
    const incidents = await res.json();

    const listContainer = document.getElementById('incidents-list');
    if (!listContainer) return;

    if (incidents.length === 0) {
      listContainer.innerHTML = '<div style="color: var(--text-muted); font-size: 0.8rem; text-align: center; padding: 1rem;">No violations detected. Workplace safe.</div>';
      return;
    }

    listContainer.innerHTML = incidents.slice().reverse().map(inc => `
      <div class="incident-item ${inc.severity.toLowerCase()}">
        <div class="incident-left">
          <span class="incident-title">${inc.type.replace(/_/g, ' ')} (${inc.track_id})</span>
          <span class="incident-meta">${inc.description} &bull; ${inc.timestamp}</span>
        </div>
        <span class="incident-badge ${inc.severity.toLowerCase()}">${inc.severity}</span>
      </div>
    `).join('');

  } catch (err) {
    console.error("Incidents fetch error:", err);
  }
}

// Fetch TensorRT Benchmarks Report
async function fetchTensorRTReport() {
  try {
    const res = await fetch('/api/tensorrt_report');
    if (!res.ok) return;
    const data = await res.json();

    const tbody = document.getElementById('benchmark-table-body');
    if (!tbody || !data.hardware_targets) return;

    const targets = data.hardware_targets;
    tbody.innerHTML = `
      <tr>
        <td>Jetson Orin Nano (15W)</td>
        <td>${targets.jetson_orin_nano_8gb.latency_p50_ms} ms</td>
        <td style="color: var(--accent-emerald); font-weight: bold;">${targets.jetson_orin_nano_8gb.throughput_fps} FPS</td>
        <td>${targets.jetson_orin_nano_8gb.speedup_vs_fp32}</td>
      </tr>
      <tr>
        <td>Jetson AGX Orin (50W)</td>
        <td>${targets.jetson_agx_orin_64gb.latency_p50_ms} ms</td>
        <td style="color: var(--accent-emerald); font-weight: bold;">${targets.jetson_agx_orin_64gb.throughput_fps} FPS</td>
        <td>${targets.jetson_agx_orin_64gb.speedup_vs_fp32}</td>
      </tr>
      <tr>
        <td>NVIDIA RTX 4090</td>
        <td>${targets.nvidia_rtx_4090.latency_p50_ms} ms</td>
        <td style="color: var(--accent-cyan); font-weight: bold;">${targets.nvidia_rtx_4090.throughput_fps} FPS</td>
        <td>${targets.nvidia_rtx_4090.speedup_vs_fp32}</td>
      </tr>
    `;

    document.getElementById('int8-speedup-pill').innerText = 
      `INT8 Edge Quantization: ${data.int8_quantization_comparison.orin_nano_int8_fps} FPS (${data.int8_quantization_comparison.memory_savings_pct}% VRAM Savings)`;

  } catch (err) {
    console.error("Benchmark fetch error:", err);
  }
}

// Action Handlers
document.addEventListener('DOMContentLoaded', () => {
  // Manual E-Stop Button
  const btnEstop = document.getElementById('btn-manual-estop');
  if (btnEstop) {
    btnEstop.addEventListener('click', async () => {
      playWarningTone(1050, 0.6);
      await fetch('/api/actuator/trigger', { method: 'POST' });
      fetchTelemetry();
    });
  }

  // Reset E-Stop Button
  const btnReset = document.getElementById('btn-reset-estop');
  if (btnReset) {
    btnReset.addEventListener('click', async () => {
      await fetch('/api/actuator/reset', { method: 'POST' });
      fetchTelemetry();
    });
  }

  // Audio Toggle Button
  const btnAudio = document.getElementById('btn-toggle-audio');
  if (btnAudio) {
    btnAudio.addEventListener('click', () => {
      audioAlertEnabled = !audioAlertEnabled;
      btnAudio.innerText = audioAlertEnabled ? '🔊 Sound: ON' : '🔇 Sound: OFF';
    });
  }

  // Export Incidents Button
  const btnExport = document.getElementById('btn-export-incidents');
  if (btnExport) {
    btnExport.addEventListener('click', async () => {
      const res = await fetch('/api/incidents');
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sentinel_incidents_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  // Periodic Polling
  fetchTelemetry();
  fetchIncidents();
  fetchTensorRTReport();
  setInterval(fetchTelemetry, 800);
  setInterval(fetchIncidents, 1500);
});
