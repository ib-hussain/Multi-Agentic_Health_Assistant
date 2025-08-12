// web_files/profile.js — sanitize + no-fake-change detection

document.addEventListener("DOMContentLoaded", () => {
  // ---------- Elements
  const form = document.getElementById("profile-form");
  const errBox = document.getElementById("form-error");

  // fields
  const nameEl   = document.getElementById("name");
  const ageEl    = document.getElementById("age");
  const genderEl = document.getElementById("gender");
  const heightEl = document.getElementById("height");
  const weightEl = document.getElementById("weight");

  const goalEl   = document.getElementById("fitness-goal");
  const prefEl   = document.getElementById("diet-pref");
  const deadlineEl = document.getElementById("goal-deadline");

  const mhEl   = document.getElementById("mental-health");
  const medEl  = document.getElementById("medical-conditions");

  const passEl  = document.getElementById("password");
  const pass2El = document.getElementById("confirm-password");

  // actions
  const editBtn   = document.getElementById("edit-btn");
  const saveBtn   = document.getElementById("save-btn");
  const cancelBtn = document.getElementById("cancel-btn");
  const logoutBtn = document.getElementById("logout-btn");

  // workout times
  const addTimeBtn   = document.getElementById("add-time-slot");
  const timeWrap     = document.querySelector(".time-slots-container");
  const hiddenTimes  = document.getElementById("time-array");
  const FIRST_SELECT = document.querySelector('.time-hour[data-index="0"]');

  // ---------- State
  let editMode = false;
  let loadedProfile = null;
  let baselineNorm = null;           // normalized snapshot to compare changes
  let timeSlots = [null, null, null]; // values like "07:00"
  let activeSlots = 1;
  let usedHours = new Set();

  // ---------- Utils
  const HOURS = ["06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23"];

  // trim-only sanitizer (don’t collapse inner spaces; just strip edges)
  const cleanStr = (s) => (s ?? "").trim();
  const normNum  = (n) => {
    const x = Number(n);
    return Number.isFinite(x) ? +x.toFixed(3) : null;
  };
  const hhFromAny = (t) => {
    if (!t) return "";
    const s = String(t);
    const m = s.match(/(\d{1,2}):/);
    return m ? m[1].padStart(2,"0") : "";
  };
  const normTimes = (arr) =>
    (arr || [])
      .map(hhFromAny)
      .filter(Boolean)
      .map(h => `${h}:00`)
      .sort(); // order-insensitive comparison

  // Build a normalized object for reliable equality check
  function normalizeFromData(d) {
    return {
      name: cleanStr(d.name),
      age: normNum(d.age),
      gender: String(d.gender || "").toLowerCase(),
      height: normNum(d.height),
      weight: normNum(d.weight),
      fitness_goal: cleanStr(d.fitness_goal || d.goal),
      diet_pref: String(d.diet_pref || "any").toLowerCase(),
      time_deadline: parseInt(d.time_deadline ?? 0, 10) || 0,
      mental_health_background: cleanStr(d.mental_health_background || d.mental_health),
      medical_conditions: cleanStr(d.medical_conditions),
      time_arr: normTimes(d.time_arr),
      password: cleanStr(d.password || d.new_password || "")
    };
  }

  function sameNormalized(a, b) {
    return JSON.stringify(a) === JSON.stringify(b);
  }

  async function fetchJSON(url, options) {
    const res = await fetch(url, options);
    let data = null;
    try { data = await res.json(); } catch {}
    if (!res.ok) {
      const msg = (data && (data.error || data.message)) || `Request failed (${res.status})`;
      throw new Error(msg);
    }
    return data;
  }

  function showError(msgs) {
    errBox.style.display = "block";
    errBox.innerHTML = Array.isArray(msgs)
      ? `<ul style="margin:0;padding-left:20px;">${msgs.map(m=>`<li>${m}</li>`).join("")}</ul>`
      : String(msgs || "Something went wrong");
    errBox.scrollIntoView({ behavior: "smooth", block: "center" });
  }
  function clearError() {
    errBox.style.display = "none";
    errBox.innerHTML = "";
  }

  function setDisabled(el, disabled) { el.disabled = !!disabled; }

  function switchMode(on) {
    editMode = !!on;

    const editable = [
      nameEl, ageEl, genderEl, heightEl, weightEl, goalEl, prefEl,
      deadlineEl, mhEl, medEl, passEl, pass2El
    ];
    editable.forEach(el => setDisabled(el, !editMode));

    // time controls
    document.querySelectorAll(".time-hour").forEach(sel => setDisabled(sel, !editMode));
    setDisabled(addTimeBtn, !editMode);
    document.querySelectorAll(".btn-remove-time").forEach(btn => setDisabled(btn, !editMode));

    // require password only during edit/save
    [passEl, pass2El].forEach(el => {
      if (editMode) el.setAttribute("required","required");
      else el.removeAttribute("required");
    });

    // buttons
    editBtn.style.display   = editMode ? "none" : "inline-block";
    saveBtn.style.display   = editMode ? "inline-block" : "none";
    cancelBtn.style.display = editMode ? "inline-block" : "none";
  }

  // Password toggles (works in view mode too)
  document.querySelectorAll(".toggle-pass").forEach(btn => {
    btn.addEventListener("click", () => {
      const input = btn.parentElement.querySelector("input");
      const isPass = input.type === "password";
      input.type = isPass ? "text" : "password";
      btn.textContent = isPass ? "Hide" : "Show";
    });
  });

  function buildOptions(select) {
    const current = select.value;
    select.innerHTML = `<option value="" disabled selected>Select hour</option>`;
    HOURS.forEach(h => {
      const opt = document.createElement("option");
      opt.value = h;
      opt.textContent = `${h}:00`;
      if (usedHours.has(h) && current !== h) {
        opt.disabled = true;
        opt.style.color = "#bbb";
      }
      select.appendChild(opt);
    });
    if (current) select.value = current;
  }

  function resyncAllSelects() {
    document.querySelectorAll(".time-hour").forEach(buildOptions);
    document.querySelectorAll(".time-hour").forEach((sel, i) => {
      const curr = timeSlots[i] ? timeSlots[i].slice(0,2) : "";
      if (curr) sel.value = curr;
    });
    hiddenTimes.value = JSON.stringify(timeSlots.filter(Boolean));
  }

  function onTimeChange(e) {
    const idx = Number(e.target.dataset.index);
    const prevHH = timeSlots[idx] ? timeSlots[idx].slice(0,2) : null;
    if (prevHH) usedHours.delete(prevHH);

    const hh = e.target.value;
    if (hh) {
      usedHours.add(hh);
      timeSlots[idx] = `${hh}:00`;
    } else {
      timeSlots[idx] = null;
    }
    resyncAllSelects();
  }

  function addTimeSlot() {
    if (!editMode || activeSlots >= 3) return;
    activeSlots++;
    const idx = activeSlots - 1;

    const group = document.createElement("div");
    group.className = "time-slot-group";
    group.innerHTML = `
      <select class="time-hour" data-index="${idx}"></select>
      <span class="time-range-indicator">20 min session</span>
      <button type="button" class="btn-remove-time" data-index="${idx}" aria-label="Remove time">×</button>
    `;
    timeWrap.insertBefore(group, addTimeBtn);

    const sel = group.querySelector(".time-hour");
    sel.addEventListener("change", onTimeChange);
    buildOptions(sel);

    const removeBtn = group.querySelector(".btn-remove-time");
    removeBtn.addEventListener("click", () => removeTimeSlot(idx, group));

    addTimeBtn.style.display = activeSlots >= 3 ? "none" : "inline-block";
  }

  function removeTimeSlot(idx, groupEl) {
    const prevHH = timeSlots[idx] ? timeSlots[idx].slice(0,2) : null;
    if (prevHH) usedHours.delete(prevHH);
    timeSlots[idx] = null;
    groupEl.remove();
    activeSlots--;

    document.querySelectorAll(".time-hour").forEach((sel, i) => sel.dataset.index = String(i));
    document.querySelectorAll(".btn-remove-time").forEach((btn, i) => btn.dataset.index = String(i));

    addTimeBtn.style.display = activeSlots >= 3 ? "none" : "inline-block";
    resyncAllSelects();
  }

  function resetTimeUI() {
    usedHours.clear();
    timeSlots = [null, null, null];
    activeSlots = 1;

    document.querySelectorAll(".time-slot-group").forEach((g, i) => { if (i > 0) g.remove(); });
    document.querySelectorAll(".btn-remove-time").forEach(btn => btn.remove());

    FIRST_SELECT.value = "";
    buildOptions(FIRST_SELECT);

    addTimeBtn.style.display = "inline-block";
    hiddenTimes.value = "[]";
  }

  function populate(profile) {
    nameEl.value   = profile.name || "";
    ageEl.value    = profile.age ?? "";
    genderEl.value = (profile.gender || "female").toLowerCase();
    heightEl.value = profile.height ?? "";
    weightEl.value = profile.weight ?? "";

    goalEl.value   = profile.fitness_goal || "";
    prefEl.value   = profile.diet_pref || "any";
    deadlineEl.value = profile.time_deadline ?? 90;

    mhEl.value   = profile.mental_health_background || "";
    medEl.value  = profile.medical_conditions || "";

    const pwd = profile.password || "";
    passEl.value = pwd;
    pass2El.value = pwd;

    resetTimeUI();
    (profile.time_arr || []).slice(0,3).forEach((t, i) => {
      if (i > 0) addTimeSlot();
      const hh = hhFromAny(t);
      if (!hh) return;
      usedHours.add(hh);
      timeSlots[i] = `${hh}:00`;
      const sel = document.querySelector(`.time-hour[data-index="${i}"]`);
      if (sel) {
        buildOptions(sel);
        sel.value = hh;
      }
    });
    resyncAllSelects();
  }

  // sanitize on blur so trailing-only spaces don’t stick around visibly
  [nameEl, goalEl, mhEl, medEl].forEach(el => {
    el.addEventListener("blur", () => {
      const v = cleanStr(el.value);
      if (v !== el.value) el.value = v;
    });
  });
  [ageEl, heightEl, weightEl, deadlineEl].forEach(el => {
    el.addEventListener("blur", () => { el.value = cleanStr(el.value); });
  });

  // ---------- Event wiring
  FIRST_SELECT.addEventListener("change", onTimeChange);
  addTimeBtn.addEventListener("click", addTimeSlot);

  editBtn.addEventListener("click", () => switchMode(true));

  cancelBtn.addEventListener("click", () => {
    clearError();
    if (loadedProfile) populate(loadedProfile);
    switchMode(false);
  });

  logoutBtn.addEventListener("click", () => { window.location.href = "/logout"; });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!editMode) return;
    clearError();
    const errors = [];
    // collect sanitized values (trimmed so spaces-only become empty)
    const nameVal = cleanStr(nameEl.value);
    const goalVal = cleanStr(goalEl.value);
    const mhVal   = cleanStr(mhEl.value);
    const medVal  = cleanStr(medEl.value);
    const p1 = cleanStr(passEl.value);
    const p2 = cleanStr(pass2El.value);

    // Required password in edit mode
    if (!p1 || !p2) errors.push("Password and confirmation are required.");
    if (p1 && p2) {
      if (p1 !== p2) errors.push("Passwords do not match.");
      if (p1.length < 4 || p1.length > 10) errors.push("Password must be 4–10 characters.");
      if (!/[A-Z]/.test(p1)) errors.push("Password must contain at least one uppercase letter.");
      if (!/[0-9]/.test(p1)) errors.push("Password must contain at least one number.");
    }

    if (!nameVal) errors.push("Name is required.");
    if (!cleanStr(ageEl.value)) errors.push("Age is required.");
    if (!cleanStr(heightEl.value)) errors.push("Height is required.");
    if (!cleanStr(weightEl.value)) errors.push("Weight is required.");
    if (!cleanStr(deadlineEl.value)) errors.push("Goal deadline is required.");

    let selectedTimes = JSON.parse(hiddenTimes.value || "[]");
    if (!selectedTimes.length && loadedProfile?.time_arr?.length) {
      selectedTimes = loadedProfile.time_arr;
    }
    if (!selectedTimes.length) errors.push("Select at least one workout time.");

    if (errors.length) { showError(errors); return; }

    // Build payload from sanitized values
    const payload = {
      name: nameVal,
      age: parseFloat(ageEl.value),
      gender: genderEl.value, // 'female' | 'male'
      height: parseFloat(heightEl.value),
      weight: parseFloat(weightEl.value),
      fitness_goal: goalVal,
      diet_pref: prefEl.value,
      time_deadline: parseInt(deadlineEl.value, 10),
      mental_health: mhVal || null,
      medical_conditions: medVal || null,
      time_arr: selectedTimes,
      new_password: p1
    };
    // ---- No fake change detection (ignores trailing/leading spaces)
    const currentNorm = normalizeFromData({
      ...payload,
      password: payload.new_password
    });
    if (baselineNorm && sameNormalized(currentNorm, baselineNorm)) {
      alert("No changes detected.");
      switchMode(false);
      return;
    }
    // proceed with save
    const prev = saveBtn.textContent;
    saveBtn.disabled = true;
    saveBtn.textContent = "Saving...";
    try {
      await fetchJSON("/api/profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      // Update local model + baseline to sanitized values
      loadedProfile = {
        ...loadedProfile,
        name: payload.name,
        age: payload.age,
        gender: payload.gender,
        height: payload.height,
        weight: payload.weight,
        fitness_goal: payload.fitness_goal,
        diet_pref: payload.diet_pref,
        time_deadline: payload.time_deadline,
        mental_health_background: payload.mental_health || "",
        medical_conditions: payload.medical_conditions || "",
        time_arr: normTimes(payload.time_arr),
        password: payload.new_password
      };
      baselineNorm = normalizeFromData(loadedProfile);

      populate(loadedProfile);
      switchMode(false);
      alert("Profile updated successfully.");
    } catch (err) {
      showError(err.message);
    } finally {
      saveBtn.disabled = false;
      saveBtn.textContent = prev;
    }
  });

  // ---------- Initial load
  (async function init() {
    try {
      const data = await fetchJSON("/api/profile");
      loadedProfile = data;
      baselineNorm = normalizeFromData(loadedProfile);
      populate(loadedProfile);
      switchMode(false); // view-first
    } catch (err) {
      showError(err.message);
    }
  })();
});
