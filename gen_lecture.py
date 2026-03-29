#!/usr/bin/env python3
"""
Generate lecture.html — a full interactive lecture on how a MEMS atomic clock works.
Self-contained: all CSS, JS, SVG animations, and simulation plots embedded inline.
"""
import base64
from pathlib import Path

BASE = Path("C:/Users/DD/OneDrive/Programming/willAI/atomicclock-mems")
OUT  = BASE / "lecture.html"

def b64img(rel):
    p = BASE / rel
    if p.exists():
        return f"data:image/png;base64,{base64.b64encode(p.read_bytes()).decode()}"
    return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVQI12NgAAIABQAABjE+ibYAAAAASUVORK5CYII="

def b64svg(rel):
    p = BASE / rel
    if p.exists():
        return f"data:image/svg+xml;base64,{base64.b64encode(p.read_bytes()).decode()}"
    return ""

imgs = {
    "energy_levels":    b64img("00_atomic_model/plots/energy_levels.png"),
    "cpt_lineshape":    b64img("00_atomic_model/plots/cpt_lineshape_theory.png"),
    "laser_sweep":      b64img("00_atomic_model/plots/laser_power_sweep_theory.png"),
    "density_matrix":   b64img("00_atomic_model/plots/density_matrix_structure.png"),
    "dicke_narrowing":  b64img("02_buffer_gas/plots/dicke_narrowing_physics.png"),
    "pressure_shift":   b64img("02_buffer_gas/plots/pressure_shift.png"),
    "cpt_resonance":    b64img("02_buffer_gas/plots/cpt_resonance.png"),
    "bode_plot":        b64img("07_servo_loop/plots/bode_plot.png"),
    "step_response":    b64img("07_servo_loop/plots/step_response.png"),
    "adev_plot":        b64img("08_allan/plots/adev_plot.png"),
    "pid_disturb":      b64img("04_thermal/plots/pid_disturbance_rejection.png"),
    "mask_preview":     b64img("design/mask_layout/csac_cell_v1_preview.png"),
    "wafer_preview":    b64img("design/mask_layout/wafer_layout_preview.png"),
    "package_lcc":      b64img("design/package/lcc20_package.png"),
    "cross_section":    b64img("design/package/cross_section.png"),
}

def img(key, caption="", style=""):
    s = style or "width:100%;border-radius:8px;border:1px solid #30363d;display:block;cursor:zoom-in;"
    cap = f'<p style="font-size:0.78rem;color:#6e7681;text-align:center;margin-top:6px;font-style:italic;">{caption}</p>' if caption else ""
    return f'<div><img src="{imgs[key]}" style="{s}" loading="lazy" class="zoomable">{cap}</div>'

# ─────────────────────────────────────────────────────────────────────────────
# INLINE JS+CSS ANIMATIONS
# ─────────────────────────────────────────────────────────────────────────────

ANIMATIONS_JS = r"""
// ── Atom bounce simulation ─────────────────────────────────────────────────
function initAtomSim(canvasId, numAtoms, withN2, darkState) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const speed = withN2 ? 1.4 : 3.2;
  const atoms = Array.from({length: numAtoms}, (_, i) => ({
    x: Math.random()*W, y: Math.random()*H,
    vx: (Math.random()-0.5)*speed*2,
    vy: (Math.random()-0.5)*speed*2,
    r: 5, phase: Math.random()*Math.PI*2,
    dark: false, flashT: 0
  }));
  let laserOn = false, t = 0;
  function draw() {
    ctx.clearRect(0,0,W,H);
    // background
    ctx.fillStyle = '#0d1117'; ctx.fillRect(0,0,W,H);
    // cell walls
    ctx.strokeStyle = '#30363d'; ctx.lineWidth = 2;
    ctx.strokeRect(2,2,W-4,H-4);
    // laser beam
    if (laserOn) {
      const grad = ctx.createLinearGradient(0,H/2-8,0,H/2+8);
      grad.addColorStop(0,'rgba(255,50,50,0)');
      grad.addColorStop(0.5,'rgba(255,50,50,0.18)');
      grad.addColorStop(1,'rgba(255,50,50,0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, H/2-8, W, 16);
      // laser line
      ctx.strokeStyle = 'rgba(255,80,80,0.7)'; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(0,H/2); ctx.lineTo(W,H/2); ctx.stroke();
    }
    // N2 molecules (small grey dots)
    if (withN2) {
      for (let i=0; i<18; i++) {
        const nx = ((i*73+t*0.2) % W + W) % W;
        const ny = ((i*47+t*0.15) % H + H) % H;
        ctx.beginPath(); ctx.arc(nx,ny,2.5,0,Math.PI*2);
        ctx.fillStyle = 'rgba(100,150,200,0.35)'; ctx.fill();
      }
    }
    // atoms
    atoms.forEach(a => {
      // bounce
      a.x += a.vx; a.y += a.vy;
      if (a.x < a.r || a.x > W-a.r) { a.vx *= -1; a.x = Math.max(a.r, Math.min(W-a.r, a.x)); }
      if (a.y < a.r || a.y > H-a.r) { a.vy *= -1; a.y = Math.max(a.r, Math.min(H-a.r, a.y)); }
      // N2 slow-down
      if (withN2) {
        a.vx *= 0.999; a.vy *= 0.999;
        const spd = Math.sqrt(a.vx*a.vx+a.vy*a.vy);
        if (spd < 0.3) { const ang=Math.random()*Math.PI*2; a.vx=Math.cos(ang)*0.6; a.vy=Math.sin(ang)*0.6; }
      }
      // dark state
      if (darkState && laserOn) { a.dark = true; }
      if (a.flashT > 0) a.flashT--;
      // draw
      const grd = ctx.createRadialGradient(a.x-1,a.y-1,1,a.x,a.y,a.r);
      if (a.dark && darkState) {
        grd.addColorStop(0,'#334'); grd.addColorStop(1,'#112');
        ctx.beginPath(); ctx.arc(a.x,a.y,a.r,0,Math.PI*2);
        ctx.fillStyle = grd; ctx.fill();
        ctx.strokeStyle = '#446'; ctx.lineWidth=1; ctx.stroke();
      } else if (a.flashT > 0) {
        grd.addColorStop(0,'#ffffc0'); grd.addColorStop(1,'#ff8800');
        ctx.beginPath(); ctx.arc(a.x,a.y,a.r+1,0,Math.PI*2);
        ctx.fillStyle = grd; ctx.fill();
      } else {
        grd.addColorStop(0,'#e0f0ff'); grd.addColorStop(1,'#3080c0');
        ctx.beginPath(); ctx.arc(a.x,a.y,a.r,0,Math.PI*2);
        ctx.fillStyle = grd; ctx.fill();
        ctx.strokeStyle = '#60a0ff'; ctx.lineWidth=0.8; ctx.stroke();
        // absorption flash (not dark state)
        if (laserOn && !darkState && Math.random() < 0.008) {
          a.flashT = 8;
          // emit photon
          const angle = Math.random()*Math.PI*2;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(a.x+Math.cos(angle)*18, a.y+Math.sin(angle)*18);
          ctx.strokeStyle = 'rgba(255,255,100,0.7)'; ctx.lineWidth=1.2; ctx.stroke();
        }
      }
    });
    t++;
    requestAnimationFrame(draw);
  }
  canvas.addEventListener('click', () => { laserOn = !laserOn; });
  draw();
  return { setLaser: v => { laserOn = v; } };
}

// ── CPT resonance scan animation ──────────────────────────────────────────
function initCPTScan(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  let scanX = 0, scanning = false, paused = false;
  const pad = {l:50,r:20,t:30,b:40};
  const cw = W-pad.l-pad.r, ch = H-pad.t-pad.b;

  function lorentzian(x) {
    const bg = 0.8;
    const dip = 0.55;
    const width = 0.06;
    return bg * (1 - dip / (1 + Math.pow((x-0.5)/width, 2)));
  }

  function draw() {
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle = '#0d1117'; ctx.fillRect(0,0,W,H);

    // axes
    ctx.strokeStyle = '#444'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, pad.t+ch);
    ctx.lineTo(pad.l+cw, pad.t+ch); ctx.stroke();

    // x-axis label
    ctx.fillStyle = '#8b949e'; ctx.font = '11px monospace'; ctx.textAlign = 'center';
    ctx.fillText('Oscillator frequency offset', pad.l+cw/2, H-6);
    ctx.save(); ctx.translate(14, pad.t+ch/2); ctx.rotate(-Math.PI/2);
    ctx.fillText('Light absorbed by Rb atoms', 0, 0); ctx.restore();
    ctx.fillText('← off resonance', pad.l+cw*0.18, pad.t-10);
    ctx.fillText('on resonance →', pad.l+cw*0.78, pad.t-10);

    // reference lines
    ctx.setLineDash([4,4]); ctx.strokeStyle = '#30363d'; ctx.lineWidth=0.8;
    const yMid = pad.t + ch * 0.18;
    ctx.beginPath(); ctx.moveTo(pad.l, yMid); ctx.lineTo(pad.l+cw, yMid); ctx.stroke();
    ctx.setLineDash([]);

    // absorption curve (drawn up to scanX)
    const pts = [];
    for (let i=0; i<=Math.min(scanX, cw); i++) {
      const fx = i/cw;
      const abs = lorentzian(fx);
      pts.push({x: pad.l+i, y: pad.t + ch*(1-abs)});
    }
    if (pts.length > 1) {
      ctx.beginPath(); ctx.moveTo(pts[0].x, pts[0].y);
      for (let i=1; i<pts.length; i++) ctx.lineTo(pts[i].x, pts[i].y);
      ctx.strokeStyle = '#58a6ff'; ctx.lineWidth = 2.5; ctx.stroke();
      // fill under
      ctx.lineTo(pts[pts.length-1].x, pad.t+ch);
      ctx.lineTo(pts[0].x, pad.t+ch);
      ctx.closePath();
      const grad = ctx.createLinearGradient(0,pad.t,0,pad.t+ch);
      grad.addColorStop(0,'rgba(88,166,255,0.18)');
      grad.addColorStop(1,'rgba(88,166,255,0.02)');
      ctx.fillStyle = grad; ctx.fill();
    }

    // scan cursor
    if (scanX > 0 && scanX <= cw) {
      const cx2 = pad.l + scanX;
      const fx = scanX/cw;
      const abs = lorentzian(fx);
      const cy2 = pad.t + ch*(1-abs);
      ctx.beginPath(); ctx.arc(cx2, cy2, 5, 0, Math.PI*2);
      const isNearDip = Math.abs(fx-0.5) < 0.05;
      ctx.fillStyle = isNearDip ? '#56d364' : '#e3b341';
      ctx.fill();

      // annotation at dip
      if (scanX > cw*0.45 && scanX < cw*0.6) {
        ctx.fillStyle = '#56d364'; ctx.font = 'bold 12px sans-serif'; ctx.textAlign = 'center';
        ctx.fillText('← CPT dark state!', cx2+60, cy2-14);
        ctx.fillText('Atoms stop absorbing', cx2+60, cy2+2);
        ctx.strokeStyle = '#56d364'; ctx.lineWidth = 1;
        ctx.setLineDash([3,3]);
        ctx.beginPath(); ctx.moveTo(cx2, cy2); ctx.lineTo(cx2, pad.t+ch); ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    if (scanX >= cw && !paused) {
      ctx.fillStyle = '#79c0ff'; ctx.font = '13px sans-serif'; ctx.textAlign='center';
      ctx.fillText('Scan complete — the dip is the clock signal', W/2, pad.t+ch/2);
      ctx.font='11px sans-serif'; ctx.fillStyle='#6e7681';
      ctx.fillText('Click to restart', W/2, pad.t+ch/2+20);
    }
  }

  function scan() {
    if (!scanning) return;
    scanX += 1.2;
    draw();
    if (scanX < cw) requestAnimationFrame(scan);
    else { scanning = false; draw(); }
  }

  canvas.addEventListener('click', () => {
    scanX = 0; scanning = true; scan();
  });
  draw();
  ctx.fillStyle='#58a6ff'; ctx.font='13px sans-serif'; ctx.textAlign='center';
  ctx.fillText('▶ Click to scan frequency', W/2, H/2);
}

// ── Energy level animation ────────────────────────────────────────────────
function initEnergyAnim(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  let mode = 0; // 0=idle 1=single beam 2=CPT dark state
  let photons = [];
  let t = 0;

  const levels = {
    f1:  {x:W*0.25, y:H*0.78, w:80, label:'|F=1⟩  ground state 1', col:'#58a6ff'},
    f2:  {x:W*0.65, y:H*0.78, w:80, label:'|F=2⟩  ground state 2', col:'#79c0ff'},
    exc: {x:W*0.45, y:H*0.22, w:80, label:"5P₁/₂ excited state", col:'#ffa657'},
  };

  function drawLevel(lv, glow) {
    if (glow) {
      ctx.shadowBlur = 18; ctx.shadowColor = lv.col;
    }
    ctx.strokeStyle = lv.col; ctx.lineWidth = glow ? 3 : 2;
    ctx.beginPath(); ctx.moveTo(lv.x-lv.w/2, lv.y); ctx.lineTo(lv.x+lv.w/2, lv.y); ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.fillStyle = lv.col; ctx.font = '11px monospace'; ctx.textAlign='center';
    ctx.fillText(lv.label, lv.x, lv.y + 16);
  }

  function drawArrow(x1,y1,x2,y2,col,dashed) {
    ctx.strokeStyle = col; ctx.lineWidth = 1.8;
    if (dashed) ctx.setLineDash([5,4]); else ctx.setLineDash([]);
    ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
    ctx.setLineDash([]);
    // arrowhead
    const angle = Math.atan2(y2-y1,x2-x1);
    ctx.fillStyle = col;
    ctx.beginPath();
    ctx.moveTo(x2,y2);
    ctx.lineTo(x2-10*Math.cos(angle-0.4), y2-10*Math.sin(angle-0.4));
    ctx.lineTo(x2-10*Math.cos(angle+0.4), y2-10*Math.sin(angle+0.4));
    ctx.closePath(); ctx.fill();
  }

  function draw() {
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#0d1117'; ctx.fillRect(0,0,W,H);

    // 6.8 GHz label between ground states
    ctx.fillStyle='#444'; ctx.font='10px monospace'; ctx.textAlign='center';
    ctx.fillText('← 6,834,682,610 Hz →', W*0.45, H*0.83);
    ctx.setLineDash([2,3]); ctx.strokeStyle='#333'; ctx.lineWidth=0.8;
    ctx.beginPath(); ctx.moveTo(W*0.29,H*0.78); ctx.lineTo(W*0.61,H*0.78); ctx.stroke();
    ctx.setLineDash([]);

    // draw levels
    drawLevel(levels.f1, mode===2);
    drawLevel(levels.f2, mode===2);
    drawLevel(levels.exc, false);

    if (mode === 1) {
      // single beam: absorption and emission
      drawArrow(levels.f1.x, levels.f1.y-2, levels.exc.x-10, levels.exc.y+2, '#ff6b6b', false);
      drawArrow(levels.exc.x-10, levels.exc.y+2, levels.f1.x, levels.f1.y-2, '#ff6b6b', true);
      drawArrow(levels.exc.x+10, levels.exc.y+2, levels.f2.x, levels.f2.y-2, '#ff6b6b', true);
      ctx.fillStyle='#ff6b6b'; ctx.font='11px sans-serif'; ctx.textAlign='left';
      ctx.fillText('Single beam: atoms absorbed', 10, 20);
      ctx.fillText('and re-emitted randomly', 10, 36);
    } else if (mode === 2) {
      // CPT: two beams, dark state
      drawArrow(levels.f1.x, levels.f1.y-2, levels.exc.x-10, levels.exc.y+2, '#58a6ff', false);
      drawArrow(levels.f2.x, levels.f2.y-2, levels.exc.x+10, levels.exc.y+2, '#79c0ff', false);
      // X over excited state = no absorption
      ctx.strokeStyle='#56d364'; ctx.lineWidth=3;
      ctx.beginPath(); ctx.moveTo(levels.exc.x-20,levels.exc.y-12); ctx.lineTo(levels.exc.x+20,levels.exc.y+12); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(levels.exc.x+20,levels.exc.y-12); ctx.lineTo(levels.exc.x-20,levels.exc.y+12); ctx.stroke();
      ctx.fillStyle='#56d364'; ctx.font='bold 12px sans-serif'; ctx.textAlign='center';
      ctx.fillText('DARK STATE', levels.exc.x, levels.exc.y - 20);
      ctx.fillText('No absorption!', levels.exc.x, levels.exc.y - 6);
      // coherence arrow between ground states
      ctx.setLineDash([4,3]);
      const midX=(levels.f1.x+levels.f2.x)/2, midY=levels.f1.y-28;
      ctx.strokeStyle='#ffa657'; ctx.lineWidth=2;
      ctx.beginPath();
      ctx.moveTo(levels.f1.x+40,levels.f1.y-4);
      ctx.quadraticCurveTo(midX, midY, levels.f2.x-40, levels.f2.y-4);
      ctx.stroke(); ctx.setLineDash([]);
      ctx.fillStyle='#ffa657'; ctx.font='10px monospace'; ctx.textAlign='center';
      ctx.fillText('quantum coherence ρ₁₂', midX, midY-6);
      ctx.fillStyle='#58a6ff'; ctx.font='11px sans-serif'; ctx.textAlign='left';
      ctx.fillText('Two beams (Δf = 6.835 GHz):', 10, 20);
      ctx.fillText('atoms enter dark state →', 10, 36);
      ctx.fillStyle='#56d364';
      ctx.fillText('laser passes straight through!', 10, 52);
    } else {
      ctx.fillStyle='#6e7681'; ctx.font='12px sans-serif'; ctx.textAlign='center';
      ctx.fillText('Click: Single beam  →  Two beams (CPT)', W/2, H-10);
    }
  }

  canvas.addEventListener('click', () => { mode = (mode+1)%3; draw(); });
  draw();
}

// ── Clock drift comparison ───────────────────────────────────────────────
function initDriftAnim(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  let t = 0, running = false;
  const pad = {l:60,r:20,t:30,b:45};
  const cw = W-pad.l-pad.r, ch = H-pad.t-pad.b;
  const maxT = 365; // days

  function draw() {
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#0d1117'; ctx.fillRect(0,0,W,H);

    // axes
    ctx.strokeStyle='#444'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(pad.l,pad.t); ctx.lineTo(pad.l,pad.t+ch); ctx.lineTo(pad.l+cw,pad.t+ch); ctx.stroke();
    ctx.fillStyle='#8b949e'; ctx.font='11px monospace'; ctx.textAlign='center';
    ctx.fillText('Time (days)', pad.l+cw/2, H-5);
    ctx.save(); ctx.translate(14, pad.t+ch/2); ctx.rotate(-Math.PI/2);
    ctx.fillText('Accumulated error', 0, 0); ctx.restore();

    // y axis ticks
    const yTicks = [{v:0,l:'0'},{v:0.25,l:'1 sec'},{v:0.5,l:'1 min'},{v:0.75,l:'1 hr'},{v:1.0,l:'1 day'}];
    yTicks.forEach(tk => {
      const y = pad.t+ch*(1-tk.v);
      ctx.fillStyle='#555'; ctx.font='9px monospace'; ctx.textAlign='right';
      ctx.fillText(tk.l, pad.l-4, y+4);
      ctx.strokeStyle='#222'; ctx.lineWidth=0.5;
      ctx.beginPath(); ctx.moveTo(pad.l,y); ctx.lineTo(pad.l+cw,y); ctx.stroke();
    });

    // x axis ticks
    [0,90,180,270,365].forEach(d => {
      const x = pad.l + (d/maxT)*cw;
      ctx.fillStyle='#555'; ctx.font='9px monospace'; ctx.textAlign='center';
      ctx.fillText(d, x, pad.t+ch+14);
    });

    const now = Math.min(t, maxT);

    // quartz watch
    ctx.beginPath();
    ctx.moveTo(pad.l, pad.t+ch);
    for (let d=0; d<=now; d++) {
      const x = pad.l + (d/maxT)*cw;
      const err_quartz = d * (1/86400); // 1 second per day normalized
      const y = pad.t + ch*(1 - Math.min(err_quartz, 1.0));
      if (d===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.strokeStyle='#e3b341'; ctx.lineWidth=2; ctx.stroke();

    // GPS-disciplined TCXO
    ctx.beginPath();
    for (let d=0; d<=now; d++) {
      const x = pad.l + (d/maxT)*cw;
      const err_gps = d * (1/(86400*1e4));
      const y = pad.t + ch*(1 - Math.min(err_gps, 1.0));
      if (d===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.strokeStyle='#ffa657'; ctx.lineWidth=2; ctx.stroke();

    // SA65 CSAC
    ctx.beginPath();
    for (let d=0; d<=now; d++) {
      const x = pad.l + (d/maxT)*cw;
      const err_sa65 = d * (1/(86400*1e8));
      const y = pad.t + ch*(1 - Math.min(err_sa65*5e6, 1.0));
      if (d===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.strokeStyle='#58a6ff'; ctx.lineWidth=2; ctx.stroke();

    // Our CSAC
    ctx.beginPath();
    for (let d=0; d<=now; d++) {
      const x = pad.l + (d/maxT)*cw;
      const err_ours = d * (1/(86400*1e9*3));
      const y = pad.t + ch*(1 - Math.min(err_ours*5e6, 1.0));
      if (d===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
    }
    ctx.strokeStyle='#56d364'; ctx.lineWidth=2.5; ctx.stroke();

    // legend
    const leg = [
      {col:'#e3b341', label:'Quartz watch (~1 s/day)'},
      {col:'#ffa657', label:'GPS-disciplined TCXO (~0.1 ms/day)'},
      {col:'#58a6ff', label:'SA65 CSAC (industry benchmark)'},
      {col:'#56d364', label:'Our design (28× better than SA65)'},
    ];
    leg.forEach((l,i) => {
      ctx.strokeStyle=l.col; ctx.lineWidth=2.5;
      ctx.beginPath(); ctx.moveTo(pad.l+8, pad.t+14+i*18); ctx.lineTo(pad.l+30, pad.t+14+i*18); ctx.stroke();
      ctx.fillStyle=l.col; ctx.font='10px sans-serif'; ctx.textAlign='left';
      ctx.fillText(l.label, pad.l+34, pad.t+18+i*18);
    });

    if (!running) {
      ctx.fillStyle='#58a6ff'; ctx.font='13px sans-serif'; ctx.textAlign='center';
      ctx.fillText('▶ Click to animate clock drift over 1 year', W/2, pad.t+ch/2);
    }
  }

  canvas.addEventListener('click', () => {
    if (t >= maxT) { t = 0; }
    running = true;
    function step() {
      t += 2;
      draw();
      if (t < maxT) requestAnimationFrame(step);
      else { running=false; draw(); }
    }
    step();
  });
  draw();
}

// ── ADEV explained animation ──────────────────────────────────────────────
function initADEVAnim(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  let step = 0;
  const steps = [
    {title: "Step 1: Measure the clock output for τ = 1 second", desc: "Take one 1-second average of the clock frequency."},
    {title: "Step 2: Take another 1-second average", desc: "Take the next 1-second average."},
    {title: "Step 3: Compute the difference", desc: "How different are the two averages? That difference (divided by f₀) is one ADEV sample."},
    {title: "Step 4: Repeat many times, take RMS", desc: "σ_y(1s) = RMS of all those differences. Ours: 8.84×10⁻¹²."},
    {title: "Step 5: Do the same for τ = 10s, 100s, ...", desc: "Longer averages = less noise. Plot σ_y vs τ to see all noise sources."},
  ];

  function draw() {
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#0d1117'; ctx.fillRect(0,0,W,H);
    const s = steps[step];
    ctx.fillStyle='#79c0ff'; ctx.font='bold 13px sans-serif'; ctx.textAlign='center';
    ctx.fillText(s.title, W/2, 28);
    ctx.fillStyle='#c9d1d9'; ctx.font='12px sans-serif';
    ctx.fillText(s.desc, W/2, 50);

    // timeline
    const tl_y = H*0.45, tl_x0=40, tl_w = W-80;
    ctx.strokeStyle='#333'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(tl_x0,tl_y); ctx.lineTo(tl_x0+tl_w,tl_y); ctx.stroke();
    ctx.fillStyle='#555'; ctx.font='10px monospace'; ctx.textAlign='center';
    for (let i=0;i<=6;i++) {
      const x=tl_x0+(i/6)*tl_w;
      ctx.fillText(i+'s', x, tl_y+16);
      ctx.beginPath(); ctx.moveTo(x,tl_y-4); ctx.lineTo(x,tl_y+4); ctx.strokeStyle='#444'; ctx.stroke();
    }

    // draw measurement blocks
    if (step >= 0) {
      ctx.fillStyle='rgba(88,166,255,0.25)'; ctx.strokeStyle='#58a6ff'; ctx.lineWidth=1.5;
      ctx.fillRect(tl_x0, tl_y-35, tl_w/6, 30);
      ctx.strokeRect(tl_x0, tl_y-35, tl_w/6, 30);
      ctx.fillStyle='#58a6ff'; ctx.font='10px monospace'; ctx.textAlign='center';
      ctx.fillText('f̄₁', tl_x0+tl_w/12, tl_y-16);
    }
    if (step >= 1) {
      ctx.fillStyle='rgba(121,192,255,0.25)'; ctx.strokeStyle='#79c0ff'; ctx.lineWidth=1.5;
      ctx.fillRect(tl_x0+tl_w/6, tl_y-35, tl_w/6, 30);
      ctx.strokeRect(tl_x0+tl_w/6, tl_y-35, tl_w/6, 30);
      ctx.fillStyle='#79c0ff'; ctx.font='10px monospace'; ctx.textAlign='center';
      ctx.fillText('f̄₂', tl_x0+tl_w/6+tl_w/12, tl_y-16);
    }
    if (step >= 2) {
      ctx.fillStyle='#f85149'; ctx.font='bold 14px sans-serif'; ctx.textAlign='center';
      ctx.fillText('Δf = f̄₂ − f̄₁', W/2, tl_y+42);
      ctx.fillText('σ_y = |Δf| / f₀', W/2, tl_y+60);
    }
    if (step >= 3) {
      ctx.fillStyle='#56d364'; ctx.font='bold 13px sans-serif'; ctx.textAlign='center';
      ctx.fillText('Our σ_y(τ=1s) = 8.84 × 10⁻¹²', W/2, tl_y+82);
      ctx.fillStyle='#8b949e'; ctx.font='11px sans-serif';
      ctx.fillText('(1 part in 113 billion — 1 second in 3,600 years)', W/2, tl_y+100);
    }
    if (step >= 4) {
      ctx.fillStyle='#ffa657'; ctx.font='12px sans-serif'; ctx.textAlign='center';
      ctx.fillText('See the full ADEV plot below (log-log, τ from 0.1s to 10,000s)', W/2, tl_y+124);
    }

    ctx.fillStyle='#444'; ctx.font='11px sans-serif'; ctx.textAlign='center';
    ctx.fillText(`Step ${step+1}/${steps.length} — click to advance`, W/2, H-10);
  }

  canvas.addEventListener('click', () => { step = (step+1)%steps.length; draw(); });
  draw();
}

// ── Servo dither animation ────────────────────────────────────────────────
function initServoDither(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  let t = 0, running = false, locked = false;
  let probeF = 0.2; // normalized position

  function lorentz(x) { return 0.7*(1-0.7/(1+Math.pow((x-0.5)/0.06,2))); }

  function draw() {
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#0d1117'; ctx.fillRect(0,0,W,H);

    const pad={l:50,r:20,t:20,b:40}, cw=W-pad.l-pad.r, ch=H-pad.t-pad.b;

    // draw resonance
    ctx.beginPath();
    for (let i=0;i<=cw;i++) {
      const x=i/cw, y=lorentz(x);
      const px=pad.l+i, py=pad.t+ch*(1-y/0.75);
      if (i===0) ctx.moveTo(px,py); else ctx.lineTo(px,py);
    }
    ctx.strokeStyle='#58a6ff'; ctx.lineWidth=2; ctx.stroke();

    // axes
    ctx.strokeStyle='#333'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(pad.l,pad.t); ctx.lineTo(pad.l,pad.t+ch); ctx.lineTo(pad.l+cw,pad.t+ch); ctx.stroke();
    ctx.fillStyle='#6e7681'; ctx.font='10px monospace'; ctx.textAlign='center';
    ctx.fillText('Frequency offset from dark state', pad.l+cw/2, H-6);
    ctx.fillText('lower absorption = dark state', pad.l+cw*0.5, pad.t+10);

    // target line
    ctx.setLineDash([4,4]); ctx.strokeStyle='#56d364'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(pad.l+cw*0.5, pad.t); ctx.lineTo(pad.l+cw*0.5, pad.t+ch); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle='#56d364'; ctx.font='10px sans-serif'; ctx.textAlign='center';
    ctx.fillText('target', pad.l+cw*0.5, pad.t+22);

    // dither probe
    const dither = running ? 0.04*Math.sin(t*0.25) : 0;
    const fLeft = probeF - 0.025 + dither;
    const fRight = probeF + 0.025 + dither;
    const aLeft = lorentz(fLeft), aRight = lorentz(fRight);
    const pxL = pad.l + fLeft*cw, pyL = pad.t+ch*(1-aLeft/0.75);
    const pxR = pad.l + fRight*cw, pyR = pad.t+ch*(1-aRight/0.75);

    // error signal
    const err = aRight - aLeft;

    if (running) {
      // move probe toward center
      probeF += err > 0 ? -0.003 : (err < 0 ? 0.003 : 0);
      probeF = Math.max(0.05, Math.min(0.95, probeF));
      if (Math.abs(probeF-0.5) < 0.005) locked = true;
    }

    // draw probe marker
    const pxP = pad.l + probeF*cw;
    const pyP = pad.t+ch*(1-lorentz(probeF)/0.75);
    ctx.beginPath(); ctx.arc(pxP, pyP, 7, 0, Math.PI*2);
    ctx.fillStyle = locked ? '#56d364' : '#e3b341'; ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth=1.5; ctx.stroke();

    // dither arrows
    if (running && !locked) {
      ctx.strokeStyle='rgba(255,200,0,0.6)'; ctx.lineWidth=1.5;
      ctx.beginPath(); ctx.moveTo(pxL,pyL-4); ctx.lineTo(pxP-8,pyP-4); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(pxR,pyR-4); ctx.lineTo(pxP+8,pyP-4); ctx.stroke();
      ctx.fillStyle='#e3b341'; ctx.font='10px sans-serif'; ctx.textAlign='center';
      ctx.fillText(`Error: ${err.toFixed(3)}`, pxP, pyP-18);
      ctx.fillText(err > 0.002 ? '← correct left' : (err < -0.002 ? 'correct right →' : 'near lock...'), pxP, pyP-6);
    }

    if (locked) {
      ctx.fillStyle='#56d364'; ctx.font='bold 13px sans-serif'; ctx.textAlign='center';
      ctx.fillText('LOCKED to dark state ✓', pad.l+cw/2, pad.t+ch*0.5);
      ctx.fillStyle='#8b949e'; ctx.font='11px sans-serif';
      ctx.fillText('The oscillator is now steered to atomic physics', pad.l+cw/2, pad.t+ch*0.5+20);
    } else if (!running) {
      ctx.fillStyle='#58a6ff'; ctx.font='13px sans-serif'; ctx.textAlign='center';
      ctx.fillText('▶ Click to start servo loop', W/2, pad.t+ch*0.6);
    }
  }

  canvas.addEventListener('click', () => {
    if (locked) { probeF=0.2; locked=false; }
    running = true;
    function step() {
      t++;
      draw();
      if (!locked) requestAnimationFrame(step);
      else { running=false; draw(); }
    }
    step();
  });
  draw();
}

// ── N2 Dicke narrowing interactive ────────────────────────────────────────
function initDickeAnim(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  let pressure = 0; // 0..200 Torr
  let dragging = false;

  function linewidth(P) {
    if (P < 0.1) P = 0.1;
    const dicke = 8000/P;
    const press = 10.8*P;
    const base = 300;
    return base + dicke + press;
  }

  const sliderX = 60, sliderW = W-120, sliderY = H-40;

  function draw() {
    ctx.clearRect(0,0,W,H);
    ctx.fillStyle='#0d1117'; ctx.fillRect(0,0,W,H);
    const pad={l:60,r:20,t:30,b:80}, cw=W-pad.l-pad.r, ch=H-pad.t-pad.b;

    // draw curve
    ctx.beginPath();
    for (let i=0;i<=cw;i++) {
      const P=(i/cw)*200;
      const lw=linewidth(P);
      const y=pad.t+ch*(1-Math.min(lw/15000,1));
      if (i===0) ctx.moveTo(pad.l+i,y); else ctx.lineTo(pad.l+i,y);
    }
    ctx.strokeStyle='#8b949e'; ctx.lineWidth=1.5; ctx.stroke();

    // fill below curve up to current pressure
    const px = pad.l + (pressure/200)*cw;
    ctx.beginPath();
    for (let i=0;i<=(pressure/200)*cw;i++) {
      const P=(i/cw)*200;
      const lw=linewidth(P);
      const y=pad.t+ch*(1-Math.min(lw/15000,1));
      if (i===0) ctx.moveTo(pad.l,pad.t+ch); else if (i===1) { ctx.lineTo(pad.l,y); } else ctx.lineTo(pad.l+i,y);
    }
    ctx.lineTo(px,pad.t+ch); ctx.closePath();
    ctx.fillStyle='rgba(88,166,255,0.1)'; ctx.fill();

    // current point
    const curLW = linewidth(pressure);
    const curY = pad.t+ch*(1-Math.min(curLW/15000,1));
    ctx.beginPath(); ctx.arc(px, curY, 7, 0, Math.PI*2);
    ctx.fillStyle = pressure>60&&pressure<90 ? '#56d364' : '#e3b341'; ctx.fill();

    // minimum marker
    let minP=1,minLW=linewidth(1);
    for(let p=1;p<=200;p++){const l=linewidth(p);if(l<minLW){minLW=l;minP=p;}}
    const minX=pad.l+(minP/200)*cw;
    const minY=pad.t+ch*(1-Math.min(minLW/15000,1));
    ctx.setLineDash([4,3]); ctx.strokeStyle='#56d364'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(minX,minY); ctx.lineTo(minX,pad.t+ch); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle='#56d364'; ctx.font='10px monospace'; ctx.textAlign='center';
    ctx.fillText(`Optimum: ${minP} Torr`, minX, minY-8);

    // labels
    ctx.fillStyle='#58a6ff'; ctx.font='10px sans-serif'; ctx.textAlign='left';
    ctx.fillText('← Dicke narrowing dominates (too few N₂)', pad.l+4, pad.t+18);
    ctx.textAlign='right';
    ctx.fillText('Pressure broadening dominates →', pad.l+cw-4, pad.t+18);

    // axes
    ctx.strokeStyle='#333'; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(pad.l,pad.t); ctx.lineTo(pad.l,pad.t+ch); ctx.lineTo(pad.l+cw,pad.t+ch); ctx.stroke();
    ctx.fillStyle='#8b949e'; ctx.font='10px monospace'; ctx.textAlign='center';
    ctx.fillText('N₂ pressure (Torr)', pad.l+cw/2, pad.t+ch+14);
    ctx.save(); ctx.translate(14,pad.t+ch/2); ctx.rotate(-Math.PI/2); ctx.fillText('CPT linewidth (Hz)', 0, 0); ctx.restore();

    // current value display
    ctx.fillStyle='#e3b341'; ctx.font='bold 12px monospace'; ctx.textAlign='center';
    ctx.fillText(`${pressure} Torr → linewidth = ${Math.round(curLW)} Hz`, W/2, pad.t+ch+30);

    // slider
    ctx.fillStyle='#21262d'; ctx.fillRect(sliderX,sliderY-6,sliderW,12);
    ctx.fillStyle='#58a6ff'; ctx.fillRect(sliderX,sliderY-6,(pressure/200)*sliderW,12);
    ctx.beginPath(); ctx.arc(sliderX+(pressure/200)*sliderW,sliderY,10,0,Math.PI*2);
    ctx.fillStyle='#79c0ff'; ctx.fill();
    ctx.fillStyle='#6e7681'; ctx.font='10px sans-serif'; ctx.textAlign='center';
    ctx.fillText('← drag to change N₂ pressure →', W/2, sliderY+24);
  }

  function getP(clientX, rect) {
    const x = clientX - rect.left - sliderX;
    return Math.max(0, Math.min(200, (x/sliderW)*200));
  }
  canvas.addEventListener('mousedown', e => {
    const r=canvas.getBoundingClientRect();
    if (Math.abs(e.clientY-r.top-sliderY)<20) { dragging=true; pressure=getP(e.clientX,r); draw(); }
  });
  canvas.addEventListener('mousemove', e => {
    if (!dragging) return;
    pressure=getP(e.clientX,canvas.getBoundingClientRect()); draw();
  });
  canvas.addEventListener('mouseup', () => dragging=false);
  canvas.addEventListener('touchstart', e => { dragging=true; });
  canvas.addEventListener('touchmove', e => {
    e.preventDefault();
    const r=canvas.getBoundingClientRect();
    pressure=getP(e.touches[0].clientX,r); draw();
  }, {passive:false});
  canvas.addEventListener('touchend', () => dragging=false);
  pressure=76;
  draw();
}

window.addEventListener('DOMContentLoaded', () => {
  initAtomSim('canvas-atoms-bare',    16, false, false);
  initAtomSim('canvas-atoms-n2',      16, true,  false);
  initAtomSim('canvas-atoms-dark',    16, true,  true);
  initCPTScan('canvas-cpt-scan');
  initEnergyAnim('canvas-energy');
  initDriftAnim('canvas-drift');
  initADEVAnim('canvas-adev-explain');
  initServoDither('canvas-servo');
  initDickeAnim('canvas-dicke');
});

// ── Lightbox / zoom for PNG images ──────────────────────────────────────────
(function() {
  const modal = document.getElementById('zoom-modal');
  const zoomImg = document.getElementById('zoom-img');
  const closeBtn = modal ? modal.querySelector('.close-btn') : null;

  function openModal(src, alt) {
    if (!modal || !zoomImg) return;
    zoomImg.src = src;
    zoomImg.alt = alt || '';
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeModal() {
    if (!modal) return;
    modal.classList.remove('open');
    document.body.style.overflow = '';
    setTimeout(() => { if (zoomImg) zoomImg.src = ''; }, 200);
  }

  // Click on any .zoomable img opens the modal
  document.addEventListener('click', function(e) {
    const t = e.target;
    if (t && t.tagName === 'IMG' && t.classList.contains('zoomable')) {
      openModal(t.src, t.alt);
    }
  });

  // Click the × button or the backdrop closes it
  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) closeModal();
    });
  }

  // Escape key also closes
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
  });
})();
"""

# ─────────────────────────────────────────────────────────────────────────────
# HTML SECTIONS
# ─────────────────────────────────────────────────────────────────────────────

def section(id_, title, subtitle=""):
    sub = f'<p style="color:#8b949e;font-size:1rem;margin-top:6px;">{subtitle}</p>' if subtitle else ""
    return f"""
<div id="{id_}" style="margin-bottom:64px;">
<h2 style="font-size:1.6rem;color:#e6edf3;border-bottom:2px solid #1f6feb;
    padding-bottom:10px;margin-bottom:6px;">{title}</h2>
{sub}"""

def card(content, accent="#30363d"):
    return f'<div style="background:#161b22;border:1px solid {accent};border-radius:10px;padding:24px 28px;margin-bottom:20px;">{content}</div>'

def two_col(left, right, ratio="1fr 1fr"):
    return f'<div style="display:grid;grid-template-columns:{ratio};gap:24px;align-items:start;">{left}{right}</div>'

def canvas_box(id_, w, h, caption=""):
    cap = f'<p style="font-size:0.78rem;color:#6e7681;text-align:center;margin-top:6px;font-style:italic;">{caption}</p>' if caption else ""
    return f'<div><canvas id="{id_}" width="{w}" height="{h}" style="width:100%;border-radius:8px;border:1px solid #30363d;cursor:pointer;display:block;"></canvas>{cap}</div>'

def callout(text, color="#58a6ff", icon="💡"):
    return f'<div style="border-left:3px solid {color};padding:12px 16px;background:#161b22;border-radius:0 8px 8px 0;margin:12px 0;font-size:0.88rem;color:#c9d1d9;line-height:1.6;">{icon} {text}</div>'

def p(text):
    return f'<p style="color:#c9d1d9;font-size:0.92rem;line-height:1.75;margin-bottom:14px;">{text}</p>'

def h3(text):
    return f'<h3 style="color:#79c0ff;font-size:1.05rem;margin:20px 0 8px;">{text}</h3>'

def equation(tex):
    return f'<div style="background:#0d1117;border:1px solid #21262d;border-radius:6px;padding:12px 18px;font-family:monospace;font-size:1rem;color:#ffa657;text-align:center;margin:14px 0;">{tex}</div>'

# ─────────────────────────────────────────────────────────────────────────────
# CONTENT SECTIONS
# ─────────────────────────────────────────────────────────────────────────────

sec_problem = section("problem", "1. The Problem: Why Do We Need an Atomic Clock?",
    "What's wrong with quartz, and when does it matter?")
sec_problem += card(
    two_col(
        "".join([
            p("Every device that keeps time uses an oscillator — something that vibrates at a known, stable rate. "
              "The quartz crystal in your phone vibrates 32,768 times per second. It's cheap and small, but it <strong>drifts</strong> — "
              "its frequency changes with temperature, aging, and mechanical stress."),
            p("A typical quartz watch loses or gains about <strong>1 second per day</strong>. "
              "That sounds fine for telling time, but many critical applications need much better:"),
            "<ul style='color:#c9d1d9;font-size:0.9rem;line-height:2;padding-left:20px;'>"
            "<li><strong>GPS navigation</strong> — a 1 µs timing error = 300 m position error</li>"
            "<li><strong>5G base stations</strong> — must be synchronised to nanoseconds</li>"
            "<li><strong>Underwater vehicles</strong> — no GPS, must keep time dead-reckoning for hours</li>"
            "<li><strong>Electronic warfare</strong> — signal timing integrity at 10⁻¹¹</li>"
            "<li><strong>Finance</strong> — trade timestamps must be accurate to microseconds</li>"
            "</ul>",
            callout("The solution: lock your oscillator to an atomic transition. Atoms are identical everywhere in the universe — "
                    "a rubidium atom in London vibrates at exactly the same frequency as one in Tokyo.", "#56d364", "⚛️"),
        ]),
        canvas_box("canvas-drift", 520, 320,
            "Accumulated clock error over 1 year. Click to animate. "
            "Green (our CSAC) stays flat while quartz (yellow) drifts by seconds.")
    )
) + "</div>"

sec_rb = section("rubidium", "2. Rubidium Physics: The Magic Frequency",
    "Why rubidium? What is a hyperfine splitting?")
sec_rb += card(
    two_col(
        "".join([
            h3("The Atom as a Clock"),
            p("Rubidium-87 atoms have electrons that can sit in different energy levels. "
              "The two lowest levels — called hyperfine ground states — are separated by a tiny energy gap. "
              "That gap corresponds to a specific electromagnetic frequency: exactly"),
            equation("f<sub>hfs</sub> = 6,834,682,610.904 Hz"),
            p("This number is <strong>a fundamental constant of nature</strong>. It doesn't change with "
              "temperature, pressure, voltage, or age. Every Rb-87 atom in the universe has this exact same gap. "
              "This is what makes atomic clocks so stable."),
            h3("Why 6.8 GHz?"),
            p("The gap is set by the interaction between the nuclear magnetic moment and the electron's "
              "magnetic field (hyperfine coupling). For Rb-87 (nuclear spin I = 3/2), the Hamiltonian gives "
              "ΔE = A_hfs × 2 where A_hfs = 3417 MHz, hence ΔE/h = 6835 MHz."),
            callout("The second itself is defined as: 9,192,631,770 periods of the Cs-133 ground state transition. "
                    "Rb clocks use a similar principle but are smaller and cheaper.", "#ffa657", "📏"),
        ]),
        "".join([
            img("energy_levels", "Rb-87 energy level diagram. Bottom: two ground states 6.8 GHz apart. "
                "Top: excited state 795 nm above. The Λ shape connecting them is how CPT works.")
        ])
    )
) + "</div>"

sec_cpt = section("cpt", "3. Coherent Population Trapping (CPT): The Clock Mechanism",
    "The quantum trick that lets a tiny laser replace a microwave cavity")
sec_cpt += card(
    "".join([
        two_col(
            "".join([
                h3("Step 1: Single Laser Beam — Normal Absorption"),
                p("Shine a laser at rubidium. Photons at 795 nm (near-infrared) excite atoms from the "
                  "ground state up to the excited state. The atom quickly falls back down, emitting light "
                  "in a random direction. You see strong <strong>absorption</strong> — the laser loses power "
                  "passing through the cell."),
                h3("Step 2: Two Beams — The Dark State"),
                p("Now shine <em>two</em> laser beams whose frequency difference equals exactly 6.8347 GHz. "
                  "Something remarkable happens: the atoms are driven into a quantum superposition of the two "
                  "ground states — a <strong>dark state</strong> — from which they cannot absorb either beam. "
                  "The laser passes straight through. The cell becomes transparent."),
                h3("Step 3: Detecting the Transition"),
                p("Sweep the frequency difference through 6.8347 GHz while monitoring the transmitted light. "
                  "When you hit the exact resonance, transmission <em>jumps up</em> (absorption dips). "
                  "That dip is the CPT resonance — our clock signal."),
                callout("The dark state is maintained by <strong>quantum coherence</strong> (ρ₁₂ in the density matrix). "
                        "It's a fragile superposition — buffer gas and magnetic shielding protect it.", "#58a6ff", "🌑"),
            ]),
            canvas_box("canvas-energy", 380, 340,
                "Energy level animation. Click to cycle: idle → single beam absorption → two-beam CPT dark state.")
        )
    ])
) + card(
    "".join([
        h3("The CPT Resonance Scan — What the Photodetector Sees"),
        two_col(
            "".join([
                p("When we sweep the oscillator frequency past the dark state, the photodetector sees: "
                  "<strong>high absorption everywhere, except at the exact resonance frequency</strong> where it dips. "
                  "That dip is our clock signal. Its width (linewidth) determines precision."),
                p("Our CPT linewidth: <strong>3 kHz</strong> wide out of 6,835,000,000 Hz total. "
                  "That's a Q-factor of 2.3 billion — the atom's internal oscillator is incredibly sharp. "
                  "The sharper the dip, the more precisely we can find its center, and the more stable the clock."),
                equation("Q = f₀ / Δf = 6.835 × 10⁹ / 3000 = 2.3 × 10⁶"),
                callout("The CPT linewidth is set by <em>how long atoms stay coherent</em>. "
                        "Buffer gas (N₂) buys more time by slowing atomic motion. "
                        "More coherence time = narrower dip = better clock.", "#56d364", "📐"),
            ]),
            canvas_box("canvas-cpt-scan", 380, 300,
                "CPT resonance scan animation. Click to sweep the oscillator frequency. "
                "Watch the absorption trace — find the dip at the dark state resonance.")
        )
    ])
) + card(
    "".join([
        h3("The Density Matrix: What's Happening Quantum-Mechanically"),
        two_col(
            "".join([
                p("The quantum state of the rubidium is described by a 3×3 density matrix ρ. "
                  "The diagonal elements (ρ₁₁, ρ₂₂, ρ₃₃) are the probabilities of being in each state. "
                  "The off-diagonal elements (ρ₁₂, ρ₁₃...) are quantum coherences — "
                  "they represent the atom being in a superposition of two states simultaneously."),
                p("The dark state exists when <strong>ρ₁₂ is non-zero</strong> — "
                  "when there is coherence between the two ground states. "
                  "Our simulation uses the Lindblad master equation to track ρ as a function of "
                  "laser detuning. At the CPT resonance, ρ₁₂ peaks, and absorption (Im[ρ₃₁]+Im[ρ₃₂]) dips."),
                equation("dρ/dt = −i[H,ρ] + Σ_k (L_k ρ L_k† − ½{L_k†L_k, ρ})"),
                p("The four Lindblad operators L_k model spontaneous emission (Γ = 5.7 MHz) "
                  "and ground-state decoherence (γ₁₂ = 300 Hz from buffer gas + cell geometry)."),
            ]),
            img("density_matrix", "3×3 density matrix. Orange = populations. Gold/purple = ρ₁₂ coherence "
                "(this IS the dark state). Blue = optical coherences. Right: which Lindblad operator governs each decay.")
        )
    ])
) + "</div>"

sec_laser = section("laser", "4. The Laser Setup: Making Two Frequencies from One",
    "We only have one VCSEL — here's how we get two beams 6.8 GHz apart")
sec_laser += card(
    two_col(
        "".join([
            h3("The Problem: 6.8 GHz From a Single Laser"),
            p("CPT requires two laser beams whose frequencies differ by exactly 6,834,682,611 Hz — "
              "6.8 GHz apart. Buying two separate VCSELs and locking them to each other is expensive and complex. "
              "Instead, we use <strong>FM sideband modulation</strong>: wobble the laser's frequency "
              "at 3.417 GHz (half the hyperfine gap), which creates sidebands at ±3.417 GHz — "
              "giving us two 'copies' of the laser exactly 6.835 GHz apart."),
            h3("Bessel Functions Control the Power Split"),
            p("How much power goes into the sidebands depends on the modulation depth β via "
              "<strong>Bessel functions</strong>. The carrier power is J₀(β)², "
              "first-order sidebands are J₁(β)², and so on. "
              "The optimal β ≈ 1.84 maximises J₁²(β) — sideband power — "
              "while keeping higher harmonics small."),
            equation("E(t) = E₀ exp(i·[ω_c·t + β·sin(ω_m·t)])"),
            equation("= E₀ Σ_n J_n(β) exp(i·[ω_c + n·ω_m]·t)"),
            callout("At β=1.84, our sidebands carry 67.7% of total optical power. "
                    "The remaining 32.3% is in the (suppressed) carrier and higher harmonics — "
                    "they don't contribute to CPT but don't harm it either.", "#ffa657", "⚡"),
        ]),
        img("laser_sweep", "Laser power optimisation. Blue = CPT linewidth (rises with power = broadening). "
            "Red = contrast (rises then falls). Green dashed = figure of merit C/Δν — peaks at the gold marker, "
            "our operating point. Balance: strong signal without excessive broadening.")
    )
) + "</div>"

sec_buffgas = section("buffgas", "5. Buffer Gas: Fighting Atomic Motion",
    "Why filling the cell with nitrogen gas makes the clock more stable")
sec_buffgas += card(
    two_col(
        "".join([
            h3("The Problem: Doppler Broadening"),
            p("Rubidium atoms at 85°C move at ~300 m/s. A moving atom sees the laser frequency Doppler-shifted: "
              "f_seen = f_laser × (1 ± v/c). Different atoms move at different speeds, so they each see "
              "slightly different frequencies. The CPT dip gets smeared out over a wide range — "
              "this is <strong>Doppler broadening</strong>, and without buffer gas, "
              "the linewidth would be ~100× wider than our target."),
            h3("Dicke Narrowing: The Solution"),
            p("N₂ buffer gas slows the net atomic drift via collisions — not stopping atoms, but "
              "confining their <em>net displacement</em>. When an atom moves less than a wavelength "
              "between collisions, it can no longer Doppler-shift the light effectively. "
              "This is <strong>Dicke narrowing</strong>: more N₂ = narrower linewidth from transit effects."),
            h3("But There's a Trade-off"),
            p("N₂ also collides with Rb in the ground states, causing the coherence to decay faster "
              "(<strong>pressure broadening</strong>, growing linearly with P). "
              "The total linewidth has a <em>minimum</em> — our simulation finds it at <strong>76.6 Torr</strong>. "
              "Below this, transit broadening dominates. Above this, pressure broadening wins."),
        ]),
        "".join([
            canvas_box("canvas-dicke", 420, 320,
                "Interactive Dicke narrowing curve. Drag the slider to change N₂ pressure "
                "and see how CPT linewidth changes. The green minimum is our operating point at 76.6 Torr."),
        ])
    )
) + card(
    two_col(
        img("dicke_narrowing", "The U-shaped linewidth vs pressure curve. "
            "Dicke narrowing (blue) falls with pressure. Pressure broadening (red) rises. "
            "Total (green) has a minimum — that's 76.6 Torr."),
        img("pressure_shift", "N₂ pressure shifts the clock frequency by −6.7 kHz/Torr. "
            "At 76.6 Torr, that's a −513 kHz offset. This is large but predictable and stable — "
            "the servo loop corrects it automatically.")
    )
) + card(
    "".join([
        h3("Three Atom Simulations: Before and After Buffer Gas"),
        p("Click each canvas to toggle the laser beam. Watch how atoms behave differently:"),
        '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">',
        "".join([
            canvas_box("canvas-atoms-bare", 260, 200,
                "No N₂ — fast atoms, click to toggle laser. Frequent absorptions (orange flash + photon emitted)."),
            canvas_box("canvas-atoms-n2", 260, 200,
                "With N₂ buffer gas — atoms slowed by collisions. Same laser, but fewer/longer absorptions."),
            canvas_box("canvas-atoms-dark", 260, 200,
                "CPT dark state — with both beams at correct frequency. Click laser on: atoms go dark (deep blue), no absorption."),
        ]),
        '</div>'
    ])
) + "</div>"

sec_cell = section("cell", "6. The MEMS Cell: Silicon Microfabrication",
    "Shrinking a vapour cell from a tennis ball to a 3mm chip")
sec_cell += card(
    two_col(
        "".join([
            h3("Anodic Bonding"),
            p("The cell is made from two materials: a <strong>silicon wafer</strong> (etched by DRIE — "
              "deep reactive ion etching — to create a 1.5 mm diameter × 1 mm deep cavity) "
              "bonded to a <strong>Pyrex glass wafer</strong> at 350°C under 800 V. "
              "Sodium ions in the glass migrate toward the silicon, creating a permanent atomic bond. "
              "The seal is hermetic — it holds the N₂ fill for the 10+ year product lifetime."),
            h3("Three Engineering Constraints"),
            p("The simulation swept cell dimensions to satisfy three constraints simultaneously:"),
            "<ol style='color:#c9d1d9;font-size:0.88rem;line-height:2;padding-left:20px;'>"
            "<li><strong>Bond strength:</strong> thermal cycling stress must stay below fracture limit. "
            "Safety factor 3.9× (spec 3×). At 2.59 MPa, we're well within the 10 MPa limit.</li>"
            "<li><strong>Beer-Lambert absorption α·L:</strong> too short = weak signal, too long = all light absorbed. "
            "Target 0.9–1.5; we achieve 1.201 at 5.0 mm path length.</li>"
            "<li><strong>Acoustic resonance:</strong> the cell must not mechanically ring at frequencies "
            "near the servo bandwidth (30 Hz). At 448 kHz resonance, we're 15,000× safe.</li>"
            "</ol>",
            callout("The 3mm die contains 8 layers: cavity, platinum heater serpentine, Pt100 RTD meander, "
                    "bond ring, dicing lane, optical window, labels. All checked by DRC: 9/9 rules pass.", "#56d364", "🏭"),
        ]),
        "".join([
            img("mask_preview", "GDS-II mask layout of the 3×3 mm CSAC die. "
                "L1 (white): circular Rb cavity. L2 (red): Pt heater serpentine in lower-left. "
                "L3 (orange): Pt100 RTD meander, upper-right. L4 (green): bond ring. "
                "8 bond pads along bottom edge."),
        ])
    )
) + card(
    two_col(
        "".join([
            h3("Wafer-Level Economics"),
            p("A single 100 mm silicon wafer holds <strong>701 CSAC dies</strong> at 80.3% fill factor "
              "(3mm die, 150 µm dicing lanes). At ~$3,000 for a MEMS wafer run, that's $4.28 per die "
              "in silicon cost — before packaging, filling, and testing. "
              "Production cost target: $120–230 per unit at 1,000 units/batch."),
        ]),
        img("wafer_preview", "100 mm wafer tiling: 701 steel-blue CSAC dies. "
            "White gaps are 150 µm dicing lanes. Dashed circle = 1 mm edge exclusion. "
            "80.3% fill is excellent for MEMS die sizes.")
    )
) + "</div>"

sec_thermal = section("thermal", "7. Thermal Control: Holding 85°C to ±0.001°C",
    "The tightest manufacturing tolerance in the whole design")
sec_thermal += card(
    two_col(
        "".join([
            h3("Why Temperature Matters So Much"),
            p("The N₂ pressure inside the sealed cell shifts with temperature via the ideal gas law: "
              "P ∝ T. Since N₂ pressure shifts the clock frequency at <strong>−6.7 kHz/Torr</strong>, "
              "and we run at 76.6 Torr, a 1°C temperature change shifts the clock by:"),
            equation("Δf ≈ −6.7 kHz/Torr × 76.6 Torr × (1°C / 358 K) ≈ −1.9 kHz"),
            p("That's a 1.9 kHz frequency error from a 1°C temperature error, which maps to "
              "ADEV ≈ 1.9e3 / 6.8e9 = 2.8×10⁻⁷ — completely unacceptable. "
              "We need temperature stable to <strong>±0.001°C (1 millikelvin)</strong>."),
            h3("The PID Controller Solution"),
            p("A platinum heater serpentine (100 Ω) and Pt100 RTD meander are etched into the silicon. "
              "A PID controller reads the RTD temperature 10× per second and adjusts heater PWM. "
              "The thermal time constant is 194 s — the cell changes temperature slowly, "
              "which actually helps: it <em>low-pass filters</em> ambient disturbances. "
              "Against a ±20°C ambient swing, the PID achieves <strong>0.84 mK peak deviation</strong> — "
              "within the 1 mK spec."),
            callout("Kp = 401 mW/°C is a very stiff loop. If the temperature drops 1°C, "
                    "the heater immediately adds 401 mW of correction. This is why it's fast.", "#79c0ff", "🌡️"),
        ]),
        canvas_box("canvas-pid-temp", 380, 300, "") +
        img("pid_disturb", "Disturbance rejection: 1°C ambient step applied at t=0. "
            "Temperature deviation (blue) peaks at 0.84 mK — below the 1 mK spec (red dashed). "
            "The PID rejects the disturbance completely within a few seconds.")
    )
) + "</div>"

sec_rf = section("rf", "8. RF Synthesis: Building 6.8 GHz from 10 MHz",
    "A phase-locked loop multiplies a cheap crystal reference up to microwave frequencies")
sec_rf += card(
    two_col(
        "".join([
            h3("The PLL Principle"),
            p("A 10 MHz TCXO (temperature-compensated crystal oscillator) is our stable reference. "
              "It drifts ~0.1 ppm/year — much less than a plain quartz crystal. "
              "A phase-locked loop (PLL) multiplies this up to 6.835 GHz by comparing the VCO output "
              "(divided by N) against the 10 MHz reference, and using the phase error to correct the VCO."),
            h3("Fractional-N Trick"),
            p("You can't get 6,834,682,611 Hz by multiplying 10 MHz by a simple integer (it's not a multiple of 10 MHz). "
              "Fractional-N synthesis divides by <em>non-integer</em> ratios by rapidly alternating "
              "between dividing by 341 and 342. The average over many cycles gives N_eff = 341.7341... — "
              "exactly what we need."),
            equation("N_eff = N + F/M = 341 + 798/1087 = 341.7341…"),
            equation("f_out = N_eff × f_ref = 341.7341 × 10 MHz = 3,417,341,000 Hz"),
            p("Frequency error: <strong>0.896 Hz</strong> out of 3,417,341,305 Hz. "
              "That's 0.26 parts-per-billion. The servo loop corrects the remaining error "
              "by locking to the CPT resonance — so this initial accuracy is more than sufficient."),
            callout("The VCO phase noise contributes only 9×10⁻¹⁵ ADEV at 1 s — "
                    "1,000× below the shot noise floor. RF synthesis is not the bottleneck.", "#56d364", "📡"),
        ]),
        "".join([
            img("cpt_resonance", "CPT resonance shape (from buffer gas module). "
                "This is what the photodetector outputs as a function of oscillator frequency offset. "
                "The narrow dip is what the PLL locks to."),
        ])
    )
) + "</div>"

sec_servo = section("servo", "9. The Servo Loop: Locking to the Atom",
    "Feedback control that steers the oscillator onto the CPT dark state")
sec_servo += card(
    two_col(
        "".join([
            h3("Why We Need a Servo"),
            p("The PLL gives us a tone near 6.8347 GHz, but 'near' drifts with temperature and aging. "
              "The servo loop continuously corrects this drift by measuring the CPT error signal. "
              "It works by <strong>dithering</strong>: modulating the oscillator frequency by ±small amount "
              "at ~1 kHz, then synchronously demodulating the photodetector signal to extract "
              "which direction the frequency needs to move."),
            h3("If frequency is too low: detector sees rising absorption → push frequency up."),
            h3("If frequency is too high: detector sees rising absorption on the other side → push frequency down."),
            p("The PID controller then applies the appropriate correction. The <strong>bandwidth of 30 Hz</strong> means "
              "it makes 30 corrections per second — fast enough to reject vibration-induced shifts "
              "but slow enough not to amplify high-frequency noise."),
            h3("Stability Analysis"),
            p("Bode analysis of the open-loop transfer function tells us if the system will oscillate or settle cleanly:"),
            equation("L(s) = C(s) × G(s) = PID × (K_VCO × K_CPT / s)"),
            callout("<strong>Phase margin 84.9°</strong> (anything >45° is stable). "
                    "<strong>Gain margin 60 dB</strong> (we could add 1,000× more gain before instability). "
                    "This is an extremely robust, well-conditioned control system.", "#56d364", "🔒"),
        ]),
        "".join([
            canvas_box("canvas-servo", 420, 280,
                "Servo dither animation. Click to start the servo. Watch the yellow probe dither "
                "back and forth, find the error signal, and steer toward the green dashed resonance center."),
        ])
    )
) + card(
    two_col(
        img("bode_plot", "Open-loop Bode plot. Top: magnitude (0 dB crossover at 30 Hz = our bandwidth). "
            "Bottom: phase. Red vertical line = gain crossover. Phase at crossover = −95°, so PM = 85°. "
            "The loop is extremely stable."),
        img("step_response", "Closed-loop step response: if we jump the target frequency, "
            "the system settles smoothly within 33 ms with no overshoot. "
            "No ringing = good phase margin.")
    )
) + "</div>"

sec_adev = section("adev", "10. Allan Deviation: Measuring Clock Quality",
    "ADEV σ_y(τ) — the universal language of clock stability")
sec_adev += card(
    two_col(
        "".join([
            h3("What ADEV Measures"),
            p("Take two consecutive measurements of the clock output, each averaged over time τ. "
              "ADEV is the expected fractional difference between those averages. "
              "Smaller ADEV = more stable clock. At τ = 1s, our ADEV is 8.84×10⁻¹²."),
            equation("σ_y(τ) = √( ½⟨(ȳ_{k+1} − ȳ_k)²⟩ )"),
            h3("Three Noise Sources"),
            p("The ADEV curve (log-log) reveals which noise dominates at each timescale:"),
            "<ul style='color:#c9d1d9;font-size:0.9rem;line-height:2;padding-left:20px;'>"
            "<li><strong>Shot noise</strong> (dominant, slope τ⁻¹/²): "
            "random arrival of photons at detector. More photons = less noise. "
            "σ_shot = (Δν_CPT / (C × f₀)) / SNR / √τ</li>"
            "<li><strong>VCO phase noise</strong> (slope τ⁻¹, tiny): "
            "ADF4351 PLL contributes 9×10⁻¹⁵ — negligible.</li>"
            "<li><strong>Thermal noise</strong> (slope τ⁻¹/²): "
            "temperature variations shift N₂ pressure → shift clock frequency. "
            "σ_thermal = K × P_N₂ × (δT/T) / f₀ / √τ</li>"
            "</ul>",
            callout("Our SNR = 1,623,295 is the key differentiator. "
                    "The SA65 commercial CSAC uses a ~1mm cell with ~10,000× fewer photons. "
                    "Our larger cell + better optics → 28× better ADEV.", "#56d364", "📊"),
        ]),
        canvas_box("canvas-adev-explain", 420, 280,
            "ADEV step-by-step explainer. Click to advance through the 5 steps of what ADEV means and how it's computed.")
    )
) + card(
    "".join([
        h3("The ADEV Plot — Reading It Correctly"),
        two_col(
            img("adev_plot",
                "Allan deviation vs averaging time τ (log-log). "
                "Blue dashed = shot noise (slope −½, dominant). "
                "Red dashed = VCO phase noise (slope −1, tiny). "
                "Green dashed = thermal noise (slope −½). "
                "Black = total. Orange horizontal = 5×10⁻¹⁰ design target. "
                "Grey = SA65 2.5×10⁻¹⁰ benchmark. Our black curve stays well below both."),
            "".join([
                "<table style='width:100%;border-collapse:collapse;font-size:0.85rem;'>",
                "<tr style='background:#0d1117;'><th style='padding:7px 10px;color:#8b949e;text-align:left;border-bottom:1px solid #30363d;'>Clock Type</th>"
                "<th style='padding:7px 10px;color:#8b949e;text-align:right;border-bottom:1px solid #30363d;'>ADEV @ 1s</th>"
                "<th style='padding:7px 10px;color:#8b949e;text-align:right;border-bottom:1px solid #30363d;'>1 sec lost in</th></tr>",
                *[f"<tr style='background:{'#161b22' if i%2 else '#0d1117'};'>"
                  f"<td style='padding:7px 10px;color:{c};'>{n}</td>"
                  f"<td style='padding:7px 10px;text-align:right;color:{c};font-family:monospace;'>{a}</td>"
                  f"<td style='padding:7px 10px;text-align:right;color:#8b949e;'>{t}</td></tr>"
                  for i,(n,a,t,c) in enumerate([
                      ("Quartz watch",          "~1×10⁻⁵",   "1 day",      "#e3b341"),
                      ("TCXO (GPS-disciplined)", "~1×10⁻⁸",  "30 years",   "#ffa657"),
                      ("Microchip SA65 CSAC",    "2.5×10⁻¹⁰","1,200 years","#58a6ff"),
                      ("Our MEMS CSAC",          "8.84×10⁻¹²","34,000 years","#56d364"),
                      ("Hydrogen maser",         "~1×10⁻¹³", ">1 million yr","#a0a0a0"),
                  ])],
                "</table>",
            ])
        )
    ])
) + "</div>"

sec_chain = section("chain", "11. Putting It All Together: The Full System",
    "How all 10 modules connect into a working atomic clock")
sec_chain += card(
    "".join([
        h3("Signal Flow — From Photons to ADEV"),
        '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:16px 0;">',
        *[f'<div style="background:#0d1117;border:1px solid {border};border-radius:8px;padding:12px 8px;text-align:center;">'
          f'<div style="font-size:1.4rem;margin-bottom:6px;">{icon}</div>'
          f'<div style="font-size:0.78rem;color:{col};font-weight:700;margin-bottom:4px;">{num}</div>'
          f'<div style="font-size:0.75rem;color:#c9d1d9;">{name}</div>'
          f'<div style="font-size:0.7rem;color:#8b949e;margin-top:4px;">{out}</div>'
          f'</div>'
          for num,name,out,icon,border,col in [
              ("00","Atom Physics","CPT = 3 kHz, 34.8%","⚛️","#56d364","#56d364"),
              ("01","VCSEL Laser","β=1.84, 67.7%","💡","#e3b341","#e3b341"),
              ("02","Buffer Gas","76.6 Torr N₂","🔵","#56d364","#56d364"),
              ("03","MEMS Cell","SF=3.9×, αL=1.2","🔲","#56d364","#56d364"),
              ("04","Thermal","±0.84 mK","🌡️","#e3b341","#e3b341"),
              ("05","Optics","SNR=1.6M","🔭","#56d364","#56d364"),
              ("06","RF / PLL","0.9 Hz error","📡","#56d364","#56d364"),
              ("07","Servo","PM=85°, BW=30Hz","🔒","#56d364","#56d364"),
              ("08","ADEV","8.84×10⁻¹²","📊","#e3b341","#e3b341"),
              ("09","Full Chain","Phase 2 ✓","✅","#1f6feb","#58a6ff"),
          ]],
        '</div>',
        p("The ADEV formula combines all three noise contributions:"),
        equation("σ_y(τ) = √( σ_shot² + σ_VCO² + σ_thermal² ) / √τ"),
        equation("σ_shot = (Δν_CPT / (C × f₀)) / SNR  =  (3000 Hz / (0.35 × 6.835 GHz)) / 1,623,295  =  7.7×10⁻¹²"),
        equation("σ_thermal = K_shift × P_N₂ × (δT / T) / f₀  =  6700 × 76.6 × (0.001/358) / 6.835×10⁹  =  2.1×10⁻¹²"),
        equation("σ_VCO = 9.25×10⁻¹⁵  (negligible)"),
        equation("σ_total(τ=1s) = √(7.7² + 2.1² + 0.009²) × 10⁻¹²  ≈  8.0×10⁻¹²"),
    ])
) + card(
    two_col(
        "".join([
            h3("Power Budget: 123.8 mW Total"),
            "<table style='width:100%;border-collapse:collapse;font-size:0.88rem;'>",
            "<tr style='background:#0d1117;'><th style='padding:7px 10px;color:#8b949e;text-align:left;border-bottom:1px solid #30363d;'>Component</th>"
            "<th style='padding:7px 10px;color:#8b949e;text-align:right;border-bottom:1px solid #30363d;'>Power</th>"
            "<th style='padding:7px 10px;color:#8b949e;text-align:right;border-bottom:1px solid #30363d;'>Why</th></tr>",
            *[f"<tr style='background:{'#161b22' if i%2 else '#0d1117'};'>"
              f"<td style='padding:7px 10px;color:#c9d1d9;'>{n}</td>"
              f"<td style='padding:7px 10px;text-align:right;color:#79c0ff;font-family:monospace;'>{p2}</td>"
              f"<td style='padding:7px 10px;text-align:right;color:#8b949e;font-size:0.8rem;'>{r}</td></tr>"
              for i,(n,p2,r) in enumerate([
                  ("Pt heater (keep cell at 85°C)","54–74 mW","sealed package, no convection"),
                  ("RF PLL (ADF4351, 6.8 GHz)","30 mW","microwave synthesis is power-hungry"),
                  ("Digital (MCU + ADC + PID)","15 mW","48 MHz MCU + 16-bit ADC"),
                  ("VCSEL laser (5 mA driver)","5 mW","small — VCSELs are efficient"),
                  ("","─────",""),
                  ("Total","123.8 mW","26 mW headroom under 150 mW budget"),
              ])],
            "</table>",
        ]),
        "".join([
            h3("The Package"),
            img("cross_section", "Cross-section of the LCC-20 ceramic package. "
                "8 layers from PCB to Kovar lid. The Rb cavity is hermetically sealed "
                "under a borosilicate glass window in an Ar/N₂ atmosphere."),
        ])
    )
) + "</div>"

sec_summary = section("summary", "12. Summary: The Complete Story in 60 Seconds", "")
sec_summary += card(
    "".join([
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">',
        "".join([
            "<div>",
            h3("The Physics (what makes it work)"),
            "<ol style='color:#c9d1d9;font-size:0.9rem;line-height:2.2;padding-left:20px;'>",
            "<li>Rb-87 atoms have two ground states split by <strong>6.8347 GHz</strong> — fixed by nature</li>",
            "<li>Two laser beams at that frequency difference drive atoms into a <strong>dark state</strong> (no absorption)</li>",
            "<li>A servo loop dithers the oscillator and steers it to find the dark state → locks to atomic physics</li>",
            "<li>Buffer gas (N₂ at 76.6 Torr) narrows the resonance by suppressing atomic motion (Dicke narrowing)</li>",
            "<li>1.6 million SNR gives low shot noise → ADEV 8.84×10⁻¹²</li>",
            "</ol>",
            "</div>",
        ]),
        "".join([
            "<div>",
            h3("The Hardware (how we build it)"),
            "<ol style='color:#c9d1d9;font-size:0.9rem;line-height:2.2;padding-left:20px;'>",
            "<li>3×3 mm Si/Pyrex MEMS cell — DRIE etched, anodic bonded, N₂ filled at 76.6 Torr</li>",
            "<li>VCSEL laser at 795 nm, FM-modulated at 3.417 GHz to create CPT sidebands</li>",
            "<li>ADF4351 fractional-N PLL synthesises 6.835 GHz from 10 MHz TCXO (0.9 Hz error)</li>",
            "<li>Pt heater + Pt100 RTD hold cell at 85°C ±0.001°C — critical for frequency stability</li>",
            "<li>PID servo loop (30 Hz BW, 85° phase margin) locks VCO to CPT dark state</li>",
            "</ol>",
            "</div>",
        ]),
        "</div>",
        '<div style="background:#0d2137;border:1px solid #1f6feb;border-radius:8px;padding:20px;margin-top:16px;">',
        '<h3 style="color:#58a6ff;margin-bottom:12px;">The one-sentence version:</h3>',
        '<p style="color:#e6edf3;font-size:1.05rem;line-height:1.7;">',
        'We use quantum mechanics (CPT dark state in rubidium) to create a 6.835 GHz frequency reference, '
        'implement it as a 3mm silicon chip with a laser, buffer-gas cell, and PID temperature control, '
        'achieving clock stability of <strong>8.84×10⁻¹²</strong> — one second lost in 34,000 years — '
        'on a <strong>124 mW</strong> power budget, 28× better than the commercial benchmark.',
        '</p></div>',
    ])
) + "</div>"

# ─────────────────────────────────────────────────────────────────────────────
# NAV + CSS + FINAL ASSEMBLY
# ─────────────────────────────────────────────────────────────────────────────

NAV_LINKS = [
    ("problem",  "1. The Problem"),
    ("rubidium", "2. Rb Physics"),
    ("cpt",      "3. CPT"),
    ("laser",    "4. Laser"),
    ("buffgas",  "5. Buffer Gas"),
    ("cell",     "6. MEMS Cell"),
    ("thermal",  "7. Thermal"),
    ("rf",       "8. RF Synth"),
    ("servo",    "9. Servo"),
    ("adev",     "10. ADEV"),
    ("chain",    "11. Full Chain"),
    ("summary",  "12. Summary"),
]

nav_items = "".join(
    f'<a href="#{id_}" style="color:#8b949e;text-decoration:none;font-size:0.8rem;'
    f'padding:4px 10px;border-radius:6px;white-space:nowrap;transition:background 0.15s,color 0.15s;" '
    f'onmouseover="this.style.background=\'#21262d\';this.style.color=\'#58a6ff\'" '
    f'onmouseout="this.style.background=\'transparent\';this.style.color=\'#8b949e\'">{label}</a>'
    for id_, label in NAV_LINKS
)

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:#0d1117;color:#c9d1d9;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  font-size:15px;line-height:1.6}
.container{max-width:1100px;margin:0 auto;padding:32px 20px 80px}
canvas{cursor:pointer}
strong{color:#e6edf3}
em{color:#79c0ff;font-style:italic}
h3{color:#79c0ff}
img.zoomable{cursor:zoom-in;transition:opacity 0.15s}
img.zoomable:hover{opacity:0.88}
#zoom-modal{display:none;position:fixed;inset:0;z-index:9999;
  background:rgba(0,0,0,0.88);cursor:zoom-out;
  align-items:center;justify-content:center;padding:24px}
#zoom-modal.open{display:flex}
#zoom-modal img{max-width:92vw;max-height:92vh;border-radius:10px;
  border:1px solid #30363d;box-shadow:0 8px 48px rgba(0,0,0,0.8);
  cursor:default;object-fit:contain}
#zoom-modal .close-btn{position:fixed;top:18px;right:22px;
  color:#e6edf3;font-size:2rem;line-height:1;cursor:pointer;
  background:rgba(13,17,23,0.7);border-radius:50%;width:40px;height:40px;
  display:flex;align-items:center;justify-content:center;
  border:1px solid #30363d;transition:background 0.15s}
#zoom-modal .close-btn:hover{background:#21262d}
@media(max-width:700px){
  div[style*="grid-template-columns:1fr 1fr"]{grid-template-columns:1fr!important}
  div[style*="grid-template-columns:repeat(5"]{grid-template-columns:repeat(2,1fr)!important}
}
"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>MEMS Atomic Clock — How It Works (Lecture)</title>
<style>{CSS}</style>
</head>
<body>

<!-- ZOOM MODAL -->
<div id="zoom-modal" role="dialog" aria-modal="true" aria-label="Zoomed image">
  <span class="close-btn" aria-label="Close">&#x2715;</span>
  <img id="zoom-img" src="" alt="Zoomed plot">
</div>

<!-- STICKY NAV -->
<nav style="position:sticky;top:0;z-index:100;background:rgba(13,17,23,0.95);
    border-bottom:1px solid #21262d;backdrop-filter:blur(8px);">
  <div style="max-width:1100px;margin:0 auto;padding:8px 20px;
      display:flex;gap:4px;overflow-x:auto;align-items:center;flex-wrap:nowrap;">
    <span style="color:#58a6ff;font-weight:700;font-size:0.85rem;
        white-space:nowrap;margin-right:8px;flex-shrink:0;">⚛️ CSAC Lecture</span>
    {nav_items}
  </div>
</nav>

<!-- HERO -->
<div style="background:linear-gradient(135deg,#0d1117 0%,#0d1f33 50%,#0d1117 100%);
    border-bottom:1px solid #1f6feb;padding:56px 20px 48px;text-align:center;">
  <p style="font-family:monospace;color:#58a6ff;font-size:0.85rem;margin-bottom:10px;">
    atomicclock-mems / lecture / how-it-works</p>
  <h1 style="font-size:2.4rem;color:#e6edf3;letter-spacing:-0.02em;margin-bottom:10px;line-height:1.2;">
    How a MEMS Chip-Scale Atomic Clock Works</h1>
  <p style="color:#8b949e;font-size:1.05rem;max-width:680px;margin:0 auto 24px;">
    A complete lecture: from quantum physics to silicon chip.
    Every animation is interactive — click to run them.</p>
  <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
    <div style="background:#161b22;border:1px solid #30363d;border-radius:20px;
        padding:6px 18px;font-size:0.83rem;">
      Stability: <strong style="color:#56d364;">8.84×10⁻¹²</strong></div>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:20px;
        padding:6px 18px;font-size:0.83rem;">
      Power: <strong style="color:#79c0ff;">124 mW</strong></div>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:20px;
        padding:6px 18px;font-size:0.83rem;">
      Die size: <strong>3 × 3 mm</strong></div>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:20px;
        padding:6px 18px;font-size:0.83rem;">
      vs SA65: <strong style="color:#56d364;">28× better</strong></div>
    <div style="background:#161b22;border:1px solid #30363d;border-radius:20px;
        padding:6px 18px;font-size:0.83rem;">
      1 sec lost in <strong>34,000 years</strong></div>
  </div>
</div>

<div class="container">
{sec_problem}
{sec_rb}
{sec_cpt}
{sec_laser}
{sec_buffgas}
{sec_cell}
{sec_thermal}
{sec_rf}
{sec_servo}
{sec_adev}
{sec_chain}
{sec_summary}
</div>

<footer style="text-align:center;color:#30363d;font-size:0.78rem;padding:24px;
    border-top:1px solid #21262d;margin-top:32px;">
  MEMS Rb-87 CPT Atomic Clock — Interactive Lecture — 2026-03-29 —
  All simulations from physics models; all plots from simulation results
</footer>

<script>
{ANIMATIONS_JS}
</script>
</body>
</html>"""

OUT.write_text(html, encoding="utf-8")
print(f"Written: {OUT} ({OUT.stat().st_size/1024:.0f} KB)")
