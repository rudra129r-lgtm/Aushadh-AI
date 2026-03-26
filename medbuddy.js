/**
 * Aushadh AI — Shared Utilities
 * Connects frontend to FastAPI backend
 */

const API = window.location.origin + "/api";

// ── Pre-baked Demo Data (Apollo Hospitals Sample - Severe Case) ─────
const DEMO_DATA = {
  confidence: 88,
  confidence_note: "Complex case requiring immediate medical attention",
  summary_en: "Mr. Rahul Sharma was admitted with acute chest pain and shortness of breath. Emergency cardiac workup revealed STEMI (heart attack). Underwent urgent angioplasty with stent placement in LAD artery. Now on dual antiplatelet therapy, statins, and beta-blockers. Discharge to cardiac rehabilitation with strict monitoring required.",
  summary_hi: "राहुल शर्मा को सीने में दर्द और सांस फूलने के कारण अस्पताल में भर्ती किया गया। हार्ट अटैक का पता चला। अत्यावश्यक एंजियोप्लास्टी हुई। अब दवाइयां चल रही हैं।",
  diagnosis: {
    original_jargon: "STEMI (ST-Elevation Myocardial Infarction) - Acute Anterior Wall MI - Critical Care Unit admission - Post primary PCI with drug-eluting stent to LAD - Triple vessel disease - Hypertension - Type 2 Diabetes Mellitus",
    simple_english: "You had a heart attack (STEMI). The main artery supplying blood to your heart (LAD) was completely blocked. An emergency procedure was done to open the blocked artery and a small tube (stent) was placed to keep it open. You were in the ICU for 3 days. You now have three arteries that have blockages and need ongoing cardiac care."
  },
  watch_for: {
    original: "Chest pain (angina), shortness of breath, palpitations, sweating, dizziness, fainting - call emergency immediately if any occur",
    simple: "Watch for: Any chest pain, difficulty breathing, fast heartbeat, sweating, or feeling faint. These could mean your heart is in trouble. Call ambulance immediately."
  },
  emergency: "IMMEDIATE ACTION REQUIRED: If you experience chest pain, difficulty breathing, sudden sweating, or fainting, call ambulance immediately (102/108). Do not wait. This is a life-threatening cardiac condition.",
  medications: [
    {
      name: "Aspirin",
      dosage: "75mg",
      timing: "Once daily - Morning",
      duration: "Long-term (lifetime)",
      with_food: "After food",
      simple_instruction: "Take EVERY DAY for life. This prevents blood clots. Never skip."
    },
    {
      name: "Clopidogrel",
      dosage: "75mg",
      timing: "Once daily - Morning",
      duration: "12 months (dual antiplatelet therapy)",
      with_food: "After food",
      simple_instruction: "Take for 1 year along with Aspirin. Both are critical to prevent another heart attack."
    },
    {
      name: "Atorvastatin",
      dosage: "40mg",
      timing: "Once daily - Night",
      duration: "Long-term (lifetime)",
      with_food: "After food",
      simple_instruction: "Take at bedtime. This lowers cholesterol to prevent more blockages."
    },
    {
      name: "Metoprolol",
      dosage: "25mg",
      timing: "Twice daily - Morning & Night",
      duration: "Long-term",
      with_food: "After food",
      simple_instruction: "Take morning and night. Keeps heart rate controlled. Do not stop suddenly."
    },
    {
      name: "Ramipril",
      dosage: "5mg",
      timing: "Once daily - Morning",
      duration: "Long-term",
      with_food: "Can take with or without food",
      simple_instruction: "Take in morning. Controls blood pressure. Watch for persistent cough."
    }
  ],
  side_effects: [
    { icon: "🚨", text: "Bleeding from gums, nose, or in urine/stool - contact doctor immediately", severity: "high" },
    { icon: "🚨", text: "Chest pain, breathlessness, palpitations - call emergency (102/108) immediately", severity: "high" },
    { icon: "🚨", text: "Severe dizziness, fainting, or fall - could be due to low blood pressure", severity: "high" },
    { icon: "💊", text: "Mild stomach discomfort - take medicines after food", severity: "low" },
    { icon: "😴", text: "Fatigue or mild dizziness - avoid driving until stable", severity: "low" }
  ],
  checklist: [
    { text: "Take Aspirin 75mg daily - lifetime", category: "Medications" },
    { text: "Take Clopidogrel 75mg daily for 12 months", category: "Medications" },
    { text: "Take Atorvastatin 40mg at night", category: "Medications" },
    { text: "Take Metoprolol 25mg twice daily", category: "Medications" },
    { text: "Cardiac rehabilitation program - 3 times per week", category: "Follow-up" },
    { text: "ECG review after 2 weeks", category: "Tests" },
    { text: "Lipid profile and cardiac enzymes after 1 month", category: "Tests" },
    { text: "Echocardiography after 3 months", category: "Tests" },
    { text: "Strict low-salt, low-fat diet", category: "Lifestyle" },
    { text: "No smoking or alcohol", category: "Lifestyle" },
    { text: "Light exercise only after doctor approval", category: "Lifestyle" },
    { text: "Monitor blood pressure daily", category: "Monitoring" },
    { text: "Watch for chest pain or breathlessness", category: "Emergency" }
  ],
  recovery_note: "6-8 weeks recovery period. No heavy lifting, climbing stairs, or strenuous activity. Cardiac rehab essential. Follow-up with cardiologist in 2 weeks.",
  doctor_name: "Dr. Rajesh Kumar",
  doctor_specialty: "Interventional Cardiologist",
  hospital: "Apollo Hospitals, Delhi",
  patient_age: "58",
  patient_gender: "Male",
  recovery_days_min: 42,
  recovery_days_max: 56,
  drug_interactions: [],
  pipeline: "Demo (Pre-loaded)"
};

function loadDemoData() {
  saveAnalysis(DEMO_DATA);
}

// ── Auth ──────────────────────────────────────────────
function requireAuth() {
  const current = window.location.pathname.split('/').pop();
  const publicPages = ['index.html', 'login.html', ''];
  if (!localStorage.getItem('medbuddy_logged_in') && !publicPages.includes(current)) {
    // Save current page so we can redirect back after login
    sessionStorage.setItem('medbuddy_redirect', window.location.href);
    window.location.href = 'login.html';
  }
}

function getUser() {
  return JSON.parse(localStorage.getItem('medbuddy_user') || '{}');
}

function saveUser(user) {
  localStorage.setItem('medbuddy_user', JSON.stringify(user));
}

function logout() {
  localStorage.removeItem('medbuddy_logged_in');
  window.location.href = 'index.html';
}

// ── Dark Mode ───────────────────────────────────────────
function toggleDarkMode() {
  const html = document.documentElement;
  const isDark = html.classList.contains('dark');
  
  if (isDark) {
    html.classList.remove('dark');
    localStorage.setItem('medbuddy_dark_mode', 'false');
    updateDarkModeUI(false);
  } else {
    html.classList.add('dark');
    localStorage.setItem('medbuddy_dark_mode', 'true');
    updateDarkModeUI(true);
  }
}

function updateDarkModeUI(isDark) {
  const icon = document.getElementById('dark-mode-icon');
  const text = document.getElementById('dark-mode-text');
  if (icon) icon.textContent = isDark ? 'light_mode' : 'dark_mode';
  if (text) text.textContent = isDark ? 'Light Mode' : 'Dark Mode';
}

function initDarkMode() {
  const darkMode = localStorage.getItem('medbuddy_dark_mode') === 'true';
  if (darkMode) {
    document.documentElement.classList.add('dark');
  }
  updateDarkModeUI(darkMode);
}

// Initialize dark mode on page load
document.addEventListener('DOMContentLoaded', initDarkMode);

function injectUserName() {
  const user = getUser();
  const name = user.name || user.email?.split('@')[0] || 'there';
  document.querySelectorAll('[data-user-name]').forEach(el => el.textContent = name);
  document.querySelectorAll('[data-user-firstname]').forEach(el => el.textContent = name.split(' ')[0]);
}

// ── Analysis storage ──────────────────────────────────
function saveAnalysis(data) {
  const json = JSON.stringify(data);
  localStorage.setItem('medbuddy_analysis', json);
  sessionStorage.setItem('medbuddy_analysis_backup', json);

  // Push to history (keep last 5)
  try {
    const history = getPrescriptionHistory();
    const entry = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      summary_en: data.summary_en || '',
      diagnosis_short: data.diagnosis?.original_jargon?.substring(0, 60) || '',
      med_count: (data.medications || []).length,
      doctor_name: data.doctor_name || null,
      confidence: data.confidence || 0,
      data: data
    };
    const filtered = history.filter(h => h.summary_en !== data.summary_en);
    filtered.unshift(entry);
    localStorage.setItem('medbuddy_history', JSON.stringify(filtered.slice(0, 5)));

    // Save notification
    saveNotification({
      title: 'New Analysis Complete',
      desc: data.summary_en?.substring(0, 60) || 'Health summary ready',
      type: 'analysis'
    });
  } catch(e) {}
}
function getAnalysis() {
  // Try localStorage first, fall back to sessionStorage backup
  const primary = localStorage.getItem('medbuddy_analysis');
  if (primary) return JSON.parse(primary);
  const backup = sessionStorage.getItem('medbuddy_analysis_backup');
  if (backup) {
    // Restore to localStorage
    localStorage.setItem('medbuddy_analysis', backup);
    return JSON.parse(backup);
  }
  return null;
}
function clearAnalysis() {
  localStorage.removeItem('medbuddy_analysis');
  sessionStorage.removeItem('medbuddy_analysis_backup');
}

// ── Prescription History ───────────────────────────────
function getPrescriptionHistory() {
  try { return JSON.parse(localStorage.getItem('medbuddy_history') || '[]'); }
  catch(e) { return []; }
}
function loadHistoryEntry(id) {
  const history = getPrescriptionHistory();
  const entry = history.find(h => h.id === id);
  if (!entry) return;
  saveAnalysis(entry.data);
  window.location.href = 'diagnosis.html';
}

// ── API: Chat Starters ────────────────────────────────
async function apiChatStarters(context, language) {
  try {
    const res = await fetch(`${API}/chat/starters`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ context: context || null, language: language || 'English' })
    });
    if (!res.ok) throw new Error('starters failed');
    const d = await res.json();
    return d.questions || [];
  } catch(e) {
    return [
      "When should I take my medicines?",
      "What foods should I avoid?",
      "When should I see the doctor again?",
      "What are the warning signs to watch for?"
    ];
  }
}

// ── API: Analyse file ─────────────────────────────────
async function apiAnalyseFile(file, age, language) {
  console.log(`[Aushadh AI] Uploading file: ${file.name}, size: ${file.size} bytes, type: ${file.type}`);
  const form = new FormData();
  form.append('file', file);
  if (age) form.append('age', age);
  form.append('language', language || 'English');
  
  try {
    const res = await fetch(`${API}/analyse/file`, { method: 'POST', body: form });
    console.log(`[Aushadh AI] Response status: ${res.status}`);
    
    if (!res.ok) {
      const e = await res.json();
      console.error(`[Aushadh AI] Error response: ${JSON.stringify(e)}`);
      throw new Error(e.detail || 'Analysis failed');
    }
    
    const result = await res.json();
    console.log(`[Aushadh AI] Analysis result received`);
    return result;
  } catch (err) {
    console.error(`[Aushadh AI] Upload error: ${err.message}`);
    throw err;
  }
}

// ── API: Analyse text ─────────────────────────────────
async function apiAnalyseText(text, age, language) {
  console.log(`[Aushadh AI] Analyzing text, length: ${text.length} chars`);
  const form = new FormData();
  form.append('text', text);
  if (age) form.append('age', age);
  form.append('language', language || 'English');
  
  try {
    const res = await fetch(`${API}/analyse/text`, { method: 'POST', body: form });
    console.log(`[Aushadh AI] Response status: ${res.status}`);
    
    if (!res.ok) {
      const e = await res.json();
      throw new Error(e.detail || 'Analysis failed');
    }
    
    return await res.json();
  } catch (err) {
    console.error(`[Aushadh AI] Text analysis error: ${err.message}`);
    throw err;
  }
}

// ── API: Sample prescription ──────────────────────────
async function apiAnalyseSample(language) {
  const form = new FormData();
  form.append('language', language || 'English');
  const res = await fetch(`${API}/analyse/sample`, { method: 'POST', body: form });
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Sample failed'); }
  return res.json();
}

// ── API: Chat ─────────────────────────────────────────
async function apiChat(message, history, context, language) {
  const res = await fetch(`${API}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history, context, language: language || 'English' }),
  });
  if (!res.ok) { const e = await res.json(); throw new Error(e.detail || 'Chat failed'); }
  return res.json();
}

// ── API: Export txt ───────────────────────────────────
async function apiExportTxt(analysis, language) {
  const res = await fetch(`${API}/export/txt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ analysis, language: language || 'English' }),
  });
  if (!res.ok) throw new Error('Export failed');
  const text = await res.text();
  const blob = new Blob([text], { type: 'text/plain' });
  const a = Object.assign(document.createElement('a'), {
    href: URL.createObjectURL(blob), download: 'Aushadh AI-Summary.txt'
  });
  a.click(); URL.revokeObjectURL(a.href);
}

// ── Alert System ───────────────────────────────────────
function checkForEmergency(analysis) {
  if (!analysis) return null;
  
  const emergencyKeywords = [
    'emergency', 'urgent', 'immediately', 'critical', 'severe',
    'life-threatening', ' ICU ', 'ventilator', 'cardiac arrest',
    'stroke', 'heart attack', 'suicide', 'overdose', 'coma',
    'blood pressure', 'high bp', 'hypertensive', 'diabetic',
    'cancer', 'tumor', 'malignant', 'chemotherapy', 'radiation',
    'dialysis', 'kidney failure', 'liver failure', 'organ failure',
    'sepsis', 'meningitis', 'encephalitis', 'dengue', 'malaria',
    'tuberculosis', 'hiv', 'aids', 'hospitalization', 'admitted',
    'surgery', 'operation', 'post-operative', 'critical care',
    'monoclonal', 'immunotherapy', 'biologic', 'transplant'
  ];
  
  const text = JSON.stringify(analysis).toLowerCase();
  
  for (const keyword of emergencyKeywords) {
    if (text.includes(keyword)) {
      return {
        isSevere: true,
        reason: `Found indicator: ${keyword}`,
        message: "This prescription contains medical information that may require immediate attention. Please consult your doctor or visit the nearest hospital for clarification."
      };
    }
  }
  
  return null;
}

function showEmergencyAlert(alert) {
  const alertDiv = document.createElement('div');
  alertDiv.id = 'emergency-alert';
  alertDiv.className = 'fixed inset-0 z-[99999] flex items-center justify-center p-4';
  alertDiv.innerHTML = `
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" onclick="closeEmergencyAlert()"></div>
    <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-bounce-in">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-12 h-12 bg-error rounded-full flex items-center justify-center">
          <span class="material-symbols-outlined text-white text-2xl" style="font-variation-settings:'FILL' 1">warning</span>
        </div>
        <div>
          <h3 class="font-headline font-bold text-xl text-error">Medical Alert</h3>
          <p class="text-xs text-outline">Severity Detected</p>
        </div>
      </div>
      <p class="text-on-surface mb-4">${alert.message}</p>
      <div class="bg-error-container/30 rounded-xl p-4 mb-4">
        <p class="text-sm text-error font-semibold">⚕️ Please consult your doctor immediately</p>
        <p class="text-xs text-on-surface-variant mt-1">This is an AI-generated summary. Always verify with your healthcare provider.</p>
      </div>
      <div class="flex gap-3">
        <button onclick="closeEmergencyAlert()" class="flex-1 bg-primary text-white py-3 rounded-full font-bold hover:bg-primary/90 transition-all">
          I Understand
        </button>
        <a href="https://www.google.com/maps/search/hospital+near+me" target="_blank" class="flex-1 bg-error text-white py-3 rounded-full font-bold hover:bg-error/90 transition-all text-center">
          Find Hospital
        </a>
      </div>
    </div>
  `;
  document.body.appendChild(alertDiv);
}

function closeEmergencyAlert() {
  const alert = document.getElementById('emergency-alert');
  if (alert) alert.remove();
}

// Also add animation style
const alertStyle = document.createElement('style');
alertStyle.textContent = `
  @keyframes bounce-in {
    0% { transform: scale(0.8); opacity: 0; }
    50% { transform: scale(1.05); }
    100% { transform: scale(1); opacity: 1; }
  }
  .animate-bounce-in { animation: bounce-in 0.4s ease forwards; }
`;
document.head.appendChild(alertStyle);

// ── Toast ─────────────────────────────────────────────
function showToast(msg, type = 'success') {
  const old = document.getElementById('mb-toast');
  if (old) old.remove();
  const t = document.createElement('div');
  t.id = 'mb-toast';
  t.style.cssText = `position:fixed;bottom:28px;left:50%;transform:translateX(-50%) translateY(80px);background:${type==='error'?'#ba1a1a':'#181c20'};color:white;padding:12px 24px;border-radius:30px;font-size:13px;font-weight:700;font-family:'Public Sans',sans-serif;box-shadow:0 8px 32px rgba(0,0,0,0.3);z-index:9999;transition:transform 0.3s ease;pointer-events:none;`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.style.transform = 'translateX(-50%) translateY(0)', 10);
  setTimeout(() => { t.style.transform = 'translateX(-50%) translateY(80px)'; setTimeout(() => t.remove(), 300); }, 3000);
}

const esc = s => String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

// ── WhatsApp Share ─────────────────────────────────────
function shareOnWhatsApp(text) {
  const encoded = encodeURIComponent(text);
  window.open(`https://wa.me/?text=${encoded}`, '_blank');
}

function shareAnalysisOnWhatsApp() {
  const data = getAnalysis();
  if (!data) return;
  let msg = `*Aushadh AI Health Summary*\n\n`;
  msg += `📋 *Summary:* ${data.summary_en || ''}\n\n`;
  msg += `🩺 *Condition:* ${data.diagnosis?.simple_english || ''}\n\n`;
  msg += `💊 *Medicines:*\n`;
  (data.medications || []).forEach(m => {
    msg += `  • ${m.name} ${m.dosage} — ${m.timing} for ${m.duration}\n`;
  });
  msg += `\n🚨 *Emergency:* ${data.emergency || ''}\n\n`;
  msg += `_Simplified by Aushadh AI AI — always consult your doctor_`;
  shareOnWhatsApp(msg);
}

document.addEventListener('DOMContentLoaded', () => { injectUserName(); });

// ── Profile dropdown ──────────────────────────────────
function injectDropdownStyles() {
  if (document.getElementById('mb-dd-style')) return;
  const s = document.createElement('style');
  s.id = 'mb-dd-style';
  s.textContent = `
    .mb-avatar-wrap{position:relative;cursor:pointer;display:inline-flex;align-items:center}
    .mb-avatar-ring{background:linear-gradient(135deg,#006068,#007b85);padding:2px;border-radius:50%;display:inline-flex}
    .mb-avatar-inner{width:36px;height:36px;border-radius:50%;background:#006068;display:flex;align-items:center;justify-content:center;border:2px solid white}
    .mb-dropdown{position:absolute;top:calc(100% + 10px);right:0;width:256px;background:#fff;border:1px solid #e5e8ee;border-radius:16px;box-shadow:0 8px 40px rgba(0,0,0,0.13);z-index:9999;opacity:0;transform:translateY(-8px) scale(0.97);transition:all 0.2s;pointer-events:none;font-family:'Public Sans',sans-serif}
    .mb-dropdown.open{opacity:1;transform:none;pointer-events:all}
    .mb-dd-item{display:flex;align-items:center;gap:10px;padding:10px 14px;border-radius:10px;text-decoration:none;color:#181c20;font-size:13px;font-weight:600;transition:background 0.15s;cursor:pointer;border:none;width:100%;background:none;text-align:left;font-family:'Public Sans',sans-serif}
    .mb-dd-item:hover{background:#f1f4fa}
    .mb-dd-item.danger{color:#ba1a1a}
    .mb-dd-item.danger:hover{background:#ffdad6}
  `;
  document.head.appendChild(s);
}

function buildProfileDropdown() {
  if (!localStorage.getItem('medbuddy_logged_in')) return;
  const user = getUser();
  const name = user.name || user.email?.split('@')[0] || 'User';
  const initials = name.split(' ').map(n=>n[0]).join('').toUpperCase().slice(0,2);
  const email = user.email || '';
  const hasAvatar = !!user.avatar;

  // Find all person icon avatar divs in header and replace them
  document.querySelectorAll('header').forEach(header => {
    // Already injected?
    if (header.querySelector('.mb-avatar-wrap')) return;

    // Find the person icon container
    const personIcon = header.querySelector('.material-symbols-outlined');
    let avatarContainer = null;
    header.querySelectorAll('.material-symbols-outlined').forEach(icon => {
      if (icon.textContent.trim() === 'person') {
        avatarContainer = icon.closest('div');
      }
    });

    if (!avatarContainer) return;

    const avatarContent = hasAvatar 
      ? `<img src="${user.avatar}" style="width:100%;height:100%;object-fit:cover;border-radius:50%">`
      : `<span style="color:white;font-weight:900;font-size:13px">${initials}</span>`;

    const wrap = document.createElement('div');
    wrap.className = 'mb-avatar-wrap';
    wrap.innerHTML = `
      <div class="mb-avatar-ring" onclick="mbToggleDropdown(event)">
        <div class="mb-avatar-inner">
          ${avatarContent}
        </div>
      </div>
      <div class="mb-dropdown" id="mb-profile-dd">
        <div style="padding:16px;border-bottom:1px solid #e5e8ee;display:flex;align-items:center;gap:12px">
          <div style="width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#006068,#007b85);display:flex;align-items:center;justify-content:center;flex-shrink:0;overflow:hidden">
            ${hasAvatar ? `<img src="${user.avatar}" style="width:100%;height:100%;object-fit:cover">` : `<span style="color:white;font-weight:900;font-size:14px">${initials}</span>`}
          </div>
          <div style="min-width:0">
            <p style="font-weight:700;font-size:14px;color:#181c20;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin:0">${esc(name)}</p>
            <p style="font-size:11px;color:#6e797a;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin:0">${esc(email)}</p>
          </div>
        </div>
        <div style="padding:8px">
          <a href="profile.html" class="mb-dd-item"><span class="material-symbols-outlined" style="font-size:18px;color:#006068">person</span>My Profile</a>
          <a href="dashboard.html" class="mb-dd-item"><span class="material-symbols-outlined" style="font-size:18px;color:#006068">dashboard</span>Dashboard</a>
          <a href="documents.html" class="mb-dd-item"><span class="material-symbols-outlined" style="font-size:18px;color:#006068">upload_file</span>Upload Document</a>
          <a href="diagnosis.html" class="mb-dd-item"><span class="material-symbols-outlined" style="font-size:18px;color:#006068">summarize</span>Health Summary</a>
          <div style="height:1px;background:#e5e8ee;margin:6px 2px"></div>
          <button onclick="logout()" class="mb-dd-item danger"><span class="material-symbols-outlined" style="font-size:18px">logout</span>Sign Out</button>
        </div>
      </div>`;

    avatarContainer.replaceWith(wrap);
  });
}

// ── Notifications ──────────────────────────────────────
function getNotifications() {
  try { return JSON.parse(localStorage.getItem('medbuddy_notifications') || '[]'); }
  catch(e) { return []; }
}

function saveNotification(notif) {
  const notifs = getNotifications();
  notifs.unshift({ ...notif, id: Date.now(), read: false, timestamp: new Date().toISOString() });
  localStorage.setItem('medbuddy_notifications', JSON.stringify(notifs.slice(0, 20)));
}

function markNotificationRead(id) {
  const notifs = getNotifications();
  notifs.forEach(n => { if (n.id === id) n.read = true; });
  localStorage.setItem('medbuddy_notifications', JSON.stringify(notifs));
}

function getUnreadCount() {
  return getNotifications().filter(n => !n.read).length;
}

function createNotificationsPanel() {
  const style = document.createElement('style');
  style.textContent = `
    .mb-notif-panel{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:90%;max-width:380px;background:#fff;border-radius:20px;box-shadow:0 25px 80px rgba(0,0,0,0.25);z-index:9999;font-family:'Public Sans',sans-serif;max-height:70vh;overflow-y:auto}
    .mb-notif-backdrop{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);backdrop-filter:blur(8px);z-index:9998}
    .mb-notif-header{padding:16px 18px;border-bottom:1px solid #f1f4fa;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;background:#fff;z-index:1}
    .mb-notif-header-title{font-weight:700;font-size:16px;color:#181c20}
    .mb-notif-close{background:none;border:none;font-size:20px;cursor:pointer;color:#6e797a;padding:4px}
    .mb-notif-close:hover{color:#181c20}
    .mb-notif-item{padding:14px 18px;border-bottom:1px solid #f1f4fa;cursor:pointer;transition:background 0.15s}
    .mb-notif-item:hover{background:#f7f9ff}
    .mb-notif-item.unread{background:#f0f9fa}
    .mb-notif-item.unread:hover{background:#e6f4f5}
    .mb-notif-title{font-weight:600;font-size:14px;color:#181c20}
    .mb-notif-desc{font-size:13px;color:#6e797a;margin-top:4px;line-height:1.4}
    .mb-notif-time{font-size:11px;color:#bdc9ca;margin-top:6px}
    .mb-notif-empty{padding:40px 20px;text-align:center;color:#6e797a;font-size:14px}
    .mb-notif-type{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px}
    .mb-notif-type.analysis{color:#006068}
    .mb-notif-type.alert{color:#ba1a1a}
  `;
  document.head.appendChild(style);

  const panel = document.createElement('div');
  panel.id = 'mb-notif-panel';
  panel.className = 'mb-notif-panel hidden';
  panel.style.display = 'none';
  
  const backdrop = document.createElement('div');
  backdrop.id = 'mb-notif-backdrop';
  backdrop.className = 'mb-notif-backdrop hidden';
  backdrop.style.display = 'none';
  
  const header = document.createElement('div');
  header.className = 'mb-notif-header';
  header.innerHTML = '<span class="mb-notif-header-title">🔔 Notifications</span><button class="mb-notif-close" onclick="hideNotificationsPanel()">×</button>';
  panel.appendChild(header);
  
  document.body.appendChild(panel);
  document.body.appendChild(backdrop);

  renderNotifications();

  document.addEventListener('click', (e) => {
    const p = document.getElementById('mb-notif-panel');
    const bell = document.querySelector('.mb-notif-bell');
    if (p && !p.classList.contains('hidden') && !p.contains(e.target) && (!bell || !bell.contains(e.target))) {
      hideNotificationsPanel();
    }
  });
}

function hideNotificationsPanel() {
  const p = document.getElementById('mb-notif-panel');
  const b = document.getElementById('mb-notif-backdrop');
  if (p) {
    p.classList.add('hidden');
    p.style.display = 'none';
  }
  if (b) {
    b.classList.add('hidden');
    b.style.display = 'none';
  }
}

function showNotificationsPanel() {
  const panel = document.getElementById('mb-notif-panel');
  const backdrop = document.getElementById('mb-notif-backdrop');
  if (panel) {
    if (panel.classList.contains('hidden')) {
      panel.classList.remove('hidden');
      panel.style.display = 'block';
      renderNotifications();
    } else {
      panel.classList.add('hidden');
      panel.style.display = 'none';
    }
    if (backdrop) {
      if (!panel.classList.contains('hidden')) {
        backdrop.classList.remove('hidden');
        backdrop.style.display = 'block';
      } else {
        backdrop.classList.add('hidden');
        backdrop.style.display = 'none';
      }
    }
  } else {
    createNotificationsPanel();
    const newPanel = document.getElementById('mb-notif-panel');
    newPanel.classList.remove('hidden');
    newPanel.style.display = 'block';
    const newBackdrop = document.getElementById('mb-notif-backdrop');
    if (newBackdrop) {
      newBackdrop.classList.remove('hidden');
      newBackdrop.style.display = 'block';
    }
  }
}

function renderNotifications() {
  const panel = document.getElementById('mb-notif-panel');
  if (!panel) return;

  const notifs = getNotifications();
  const data = getAnalysis();

  // Keep header, find content area
  const header = panel.querySelector('.mb-notif-header');
  let html = '';

  if (notifs.length === 0 && !data) {
    html = '<div class="mb-notif-empty"><span class="material-symbols-outlined text-4xl text-outline">notifications_off</span><p class="mt-3">No notifications yet</p><p class="text-xs mt-1 text-outline">Upload a prescription to get started</p></div>';
  } else {
    if (data) {
      const latest = {
        id: 'latest',
        title: 'New Analysis Complete',
        desc: data.summary_en?.substring(0, 100) + (data.summary_en?.length > 100 ? '...' : '') || 'Your health summary is ready',
        type: 'analysis',
        time: new Date().toISOString()
      };
      notifs.unshift(latest);
    }

    html = notifs.slice(0, 10).map(n => `
      <div class="mb-notif-item ${n.read ? '' : 'unread'}" onclick="handleNotificationClick('${n.type || 'default'}', ${n.id === 'latest' ? 0 : n.id})">
        <div class="mb-notif-type ${n.type || 'analysis'}">${n.type === 'alert' ? '⚠️ Alert' : '📊 Analysis'}</div>
        <div class="mb-notif-title">${esc(n.title)}</div>
        <div class="mb-notif-desc">${esc(n.desc)}</div>
        <div class="mb-notif-time">${formatNotifTime(n.timestamp || n.time)}</div>
      </div>
    `).join('');
  }

  // Update panel content keeping header
  panel.innerHTML = '';
  if (header) panel.appendChild(header);
  const contentDiv = document.createElement('div');
  contentDiv.innerHTML = html;
  panel.appendChild(contentDiv);
}

function handleNotificationClick(type, id) {
  if (type === 'analysis' || id === 0) {
    window.location.href = 'diagnosis.html';
  } else if (id && id !== 'latest') {
    markNotificationRead(id);
  }
  showNotificationsPanel();
}

function formatNotifTime(ts) {
  if (!ts) return '';
  const d = new Date(ts);
  const now = new Date();
  const diff = now - d;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

function updateNotificationBadge() {
  const bell = document.querySelector('.mb-notif-bell');
  if (!bell) return;
  const count = getUnreadCount();
  const badge = bell.querySelector('.notif-badge');
  if (count > 0) {
    if (badge) {
      badge.textContent = count > 9 ? '9+' : count;
    } else {
      const b = document.createElement('span');
      b.className = 'notif-badge';
      b.style.cssText = 'position:absolute;top:-2px;right:-2px;background:#ba1a1a;color:white;font-size:9px;font-weight:700;min-width:16px;height:16px;border-radius:8px;display:flex;align-items:center;justify-content:center;padding:0 4px';
      b.textContent = count > 9 ? '9+' : count;
      bell.style.position = 'relative';
      bell.appendChild(b);
    }
  } else if (badge) {
    badge.remove();
  }
}

function mbToggleDropdown(e) {
  e.stopPropagation();
  const dd = document.getElementById('mb-profile-dd');
  if (dd) dd.classList.toggle('open');
}

// Override DOMContentLoaded to also inject dropdown
document.addEventListener('DOMContentLoaded', () => {
  injectDropdownStyles();
  
  // Only init dropdown and notifications if user is logged in and not on landing page
  if (localStorage.getItem('medbuddy_logged_in') && !window.__medbuddy_landing) {
    setTimeout(buildProfileDropdown, 150);
    setTimeout(() => {
      createNotificationsPanel();
      initNotificationBell();
    }, 200);
  }
});

function initNotificationBell() {
  document.querySelectorAll('header').forEach(header => {
    const notifBtn = header.querySelector('.material-symbols-outlined');
    let bellContainer = null;
    header.querySelectorAll('.material-symbols-outlined').forEach(icon => {
      if (icon.textContent.trim() === 'notifications') {
        bellContainer = icon.closest('button');
      }
    });

    if (!bellContainer || bellContainer.classList.contains('mb-notif-bell')) return;

    bellContainer.classList.add('mb-notif-bell', 'cursor-pointer', 'hover:bg-surface-container-high', 'rounded-full', 'transition-all');
    bellContainer.onclick = function(e) {
      e.stopPropagation();
      showNotificationsPanel();
    };
    bellContainer.title = 'Notifications';

    updateNotificationBadge();
  });
}
