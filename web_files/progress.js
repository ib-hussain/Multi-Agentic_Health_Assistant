/* progress.js – activity as string (mapped to score), blue theme */

let weightChart, activityChart, planChart;

// enumerated mapping for activity → numeric score for charts/heat
const ACT_MAP = {
  "not active": 0,
  "lightly active": 1,
  "active": 2,
  "very active": 3
};
const SCORE_TO_LABEL = Object.fromEntries(Object.entries(ACT_MAP).map(([k,v])=>[v,k]));

document.addEventListener("DOMContentLoaded", () => {
  if (window.Chart) {
    Chart.defaults.font.family =
      "'Manrope', system-ui, -apple-system, Segoe UI, Roboto, sans-serif";
    Chart.defaults.color = "#2b3446";
    Chart.defaults.borderColor = "rgba(0,0,0,.06)";
    Chart.defaults.plugins.tooltip.backgroundColor = "rgba(23,26,31,.9)";
  }
  document.getElementById("reload-btn").addEventListener("click", loadProgress);
  loadProgress();
});

async function loadProgress() {
  setError(null);
  try {
    const res = await fetch("/api/progress");
    const json = await res.json();
    if (!res.ok || !json?.success) throw new Error(json?.error || `HTTP ${res.status}`);
    renderAll(Array.isArray(json.rows) ? json.rows : []);
  } catch (e) { setError(e.message || String(e)); }
}

function setError(msg) {
  const box = document.getElementById("error-box");
  if (!msg) { box.hidden = true; box.textContent = ""; return; }
  box.hidden = false; box.textContent = msg;
}

function renderAll(rows) {
  // rows: [date, condition, activityStr, days_done, days_left, height, weight, diet]
  const parsed = rows.map((r, i) => {
    const [d, cond, activityStr, done, left, h, w, diet] = r;
    const date = parseDate(d);
    const actLabel = String(activityStr || "").toLowerCase().trim();
    const actScore = ACT_MAP[actLabel] ?? 0;
    return {
      key: i,
      date, label: fmtLabel(date),
      cond: String(cond || "").toLowerCase(),
      activityStr: actLabel || "not active",
      activityScore: actScore,
      done: num(done), left: num(left),
      height: fnum(h), weight: fnum(w), diet: String(diet || "")
    };
  });

  // ----- Table (shows activity STRING)
  const tbody = document.getElementById("progress-tbody");
  tbody.innerHTML = "";
  parsed.forEach(d => {
    tbody.appendChild(
      el("tr", {},
        el("td", {}, d.label),
        el("td", { class: "capitalize" }, d.cond || "–"),
        el("td", { class: "capitalize" }, d.activityStr),
        el("td", {}, d.done),
        el("td", {}, d.left),
        el("td", {}, d.height ?? "–"),
        el("td", {}, d.weight ?? "–"),
        el("td", { title: d.diet }, d.diet || "–"),
      )
    );
  });
  document.getElementById("row-count").textContent = `${parsed.length} days`;

  // ----- Charts
  const labels = parsed.map(d => d.label);
  const weights = parsed.map(d => d.weight ?? null);
  const actScores = parsed.map(d => d.activityScore ?? 0);
  const actLabels = parsed.map(d => d.activityStr);
  const last = parsed.at(-1);

  document.getElementById("weight-last").textContent =
    last?.weight != null ? `${last.weight} kg` : "–";
  document.getElementById("activity-last").textContent =
    last ? titleCase(last.activityStr) : "–";
  document.getElementById("plan-last").textContent =
    last ? `${last.done} / ${last.done + last.left}` : "–";

  const stroke = "#2563eb", fill = "rgba(37,99,235,.22)";
  const barA = "#2563eb", barB = "#93c5fd";

  // Weight
  weightChart = createOrUpdateChart(weightChart, "weightChart", {
    type: "line",
    data: { labels, datasets: [{ label:"Weight (kg)", data: weights, tension:.3, borderWidth:2, borderColor:stroke, backgroundColor:fill, fill:true, pointRadius:0 }] },
    options: baseLineOptions("kg")
  });

  // Activity (uses scores, shows label in tooltip)
  activityChart = createOrUpdateChart(activityChart, "activityChart", {
    type: "line",
    data: { labels, datasets: [{ label:"Activity", data: actScores, tension:.3, borderWidth:2, borderColor:stroke, backgroundColor:fill, fill:true, pointRadius:0 }] },
    options: {
      ...baseLineOptions(""),
      scales: { y: { beginAtZero:true, suggestedMax:3, ticks:{ stepSize:1, callback:(v)=>titleCase(SCORE_TO_LABEL[v] ?? "") } } },
      plugins: { ...baseLineOptions("").plugins, tooltip:{ callbacks:{ label:(ctx)=> titleCase(SCORE_TO_LABEL[ctx.parsed.y] ?? "") } } }
    }
  });

  // Progression towards goal
  const done = last?.done ?? 0, left = last?.left ?? 0;
  planChart = createOrUpdateChart(planChart, "planChart", {
    type: "bar",
    data: { labels:["Done","Left"], datasets:[{ label:"Days", data:[done,left], backgroundColor:[barA,barB], borderRadius:6 }] },
    options: { responsive:true, scales:{ y:{ beginAtZero:true } }, plugins:{ legend:{ display:false } } }
  });
}


/* utils */
function parseDate(v){ try{ if (typeof v==="string" && /^\d{4}-\d{2}-\d{2}/.test(v)) return new Date(v); const d=new Date(v); return isNaN(d)?null:d; }catch{ return null; } }
function fmtLabel(d){ return d ? d.toLocaleDateString(undefined,{month:"short", day:"numeric"}) : ""; }
const num = v => Number(v ?? 0);
const fnum = v => { const n = Number(v); return Number.isFinite(n) ? Math.round(n*10)/10 : null; };
const titleCase = s => (s||"").split(" ").map(w=>w? w[0].toUpperCase()+w.slice(1):"").join(" ");
function el(t, attrs={}, ...kids){ const n=document.createElement(t); for(const [k,v] of Object.entries(attrs)){ if(k==="class") n.className=v; else if(k==="style") n.setAttribute(k,v); else n.setAttribute(k,v); } kids.forEach(c=>n.append(c instanceof Node?c:document.createTextNode(c))); return n; }
function createOrUpdateChart(inst, id, cfg){ const ctx=document.getElementById(id).getContext("2d"); if(inst) inst.destroy(); return new Chart(ctx,cfg); }
function baseLineOptions(suf){ return { responsive:true, plugins:{ legend:{display:false}, tooltip:{ callbacks:{ label:(ctx)=>`${ctx.parsed.y}${suf?` ${suf}`:''}` } } }, scales:{ x:{ ticks:{ maxRotation:0, autoSkip:true }}, y:{ beginAtZero:false } } }; }

