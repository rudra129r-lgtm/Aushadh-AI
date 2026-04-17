/**
 * Aushadh AI — Shared Utilities
 * Connects frontend to FastAPI backend
 */

var API = window.location.origin + "/api";

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
  // Only load demo data for display - don't save to any storage
  window.DEMO_DATA = DEMO_DATA;
  return DEMO_DATA;
}

// ── Language System ───────────────────────────────────
const TRANSLATIONS = {
  dashboard: {
    nav_dashboard: { en: 'Dashboard', hi: 'डैशबोर्ड' },
    nav_documents: { en: 'Documents', hi: 'दस्तावेज़' },
    nav_summary: { en: 'Summary', hi: 'सारांश' },
    nav_medications: { en: 'Medications', hi: 'दवाइयाँ' },
    nav_checklist: { en: 'Checklist', hi: 'चेकलिस्ट' },
    nav_askai: { en: 'Ask AI', hi: 'AI से पूछें' },
    nav_profile: { en: 'Profile', hi: 'प्रोफ़ाइल' },
    sign_out: { en: 'Sign Out', hi: 'साइन आउट' },
    welcome_back: { en: 'Welcome back', hi: 'वापसी पर स्वागत है' },

    your_health: { en: 'Your Health', hi: 'आपका स्वास्थ्य' },
    finally_clear: { en: 'Finally Clear.', hi: 'अंत में स्पष्ट।' },
    upload_prescription: { en: 'Upload Prescription', hi: 'नुस्खा अपलोड करें' },
    try_live_demo: { en: 'Try Live Demo', hi: 'लाइव डेमो देखें' },
    active_medications: { en: 'Active Medications', hi: 'सक्रिय दवाइयाँ' },
    no_medications: { en: 'No medications yet', hi: 'अभी तक कोई दवाई नहीं' },
    health_summary: { en: 'Health Summary', hi: 'स्वास्थ्य सारांश' },
    health_summary_desc: { en: 'View your simplified diagnosis and plain-language explanation.', hi: 'अपना सरलीकृत निदान और सादी भाषा में समझना देखें।' },
    followup_checklist: { en: 'Follow-up Checklist', hi: 'फॉलो-अप चेकलिस्ट' },
    checklist_desc: { en: 'Side effects, alerts and tasks from your last consultation.', hi: 'आपकी पिछली जांच से साइड इफेक्ट्स, अलर्ट और कार्य।' },
    medications_desc: { en: 'Full schedule, dosage and timing for all your prescriptions.', hi: 'आपके सभी नुस्खों के लिए पूरा शेड्यूल, खुराक और समय।' },
    view_all: { en: 'View All', hi: 'सभी देखें' },
    recent_prescriptions: { en: 'Recent Prescriptions', hi: 'हाल के नुस्खे' },
    last_analysis: { en: 'Last Analysis', hi: 'पिछला विश्लेषण' },
    diagnosis: { en: 'Diagnosis', hi: 'निदान' },
    summary_label: { en: 'Summary', hi: 'सारांश' },
    ai_confidence: { en: 'AI Confidence', hi: 'AI विश्वास' },
    view_summary: { en: 'View Summary', hi: 'सारांश देखें' },
    view_meds: { en: 'View Meds', hi: 'दवाइयाँ देखें' },
    no_analysis: { en: 'No Analysis Yet', hi: 'अभी तक कोई विश्लेषण नहीं' },
    upload_first: { en: 'Upload your first prescription to see your health summary here.', hi: 'अपना स्वास्थ्य सारांश यहाँ देखने के लिए अपना पहला नुस्खा अपलोड करें।' },
    upload_now: { en: 'Upload Now', hi: 'अभी अपलोड करें' },
    current: { en: 'CURRENT', hi: 'वर्तमान' },
    medications_text: { en: 'Medications', hi: 'दवाइयाँ' },
    med_subtitle: { en: 'Upload a prescription to see your medications', hi: 'अपनी दवाइयाँ देखने के लिए नुस्खा अपलोड करें' },
    no_medications: { en: 'No medications yet', hi: 'अभी तक कोई दवाई नहीं' },
    med_schedule_placeholder: { en: 'Your medication schedule will appear here after you upload a prescription.', hi: 'आपका दवाई का शेड्यूल यहाँ दिखेगा जब आप नुस्खा अपलोड करेंगे।' },
    you_have_meds: { en: 'You have {count} medication{plural} in your prescription.', hi: 'आपके नुस्खे में {count} दवाई है।' },
    meds_label: { en: 'meds', hi: 'दवाइयाँ' },
    verified_label: { en: 'verified', hi: 'सत्यापित' },
    medication_terms: {
      timing: {
        'once daily': 'प्रतिदिन एक बार',
        'twice daily': 'दिन में दो बार',
        'three times': 'दिन में तीन बार',
        'morning': 'सुबह',
        'afternoon': 'दोपहर',
        'evening': 'शाम',
        'night': 'रात में',
        'after food': 'खाने के बाद',
        'before food': 'खाने से पहले',
        'with food': 'खाने के साथ',
        'daily': 'प्रतिदिन',
        'at bedtime': 'सोने से पहले',
        'twice': 'दो बार',
        'once': 'एक बार'
      },
      duration: {
        'long-term': 'दीर्घकालिक',
        'short-term': 'अल्पकालिक',
        'lifetime': 'आजीवन',
        'months': 'महीने',
        'weeks': 'सप्ताह',
        'days': 'दिन'
      },
      instructions: {
        'take one tablet daily': 'एक गोली प्रतिदिन लें',
        'take one tablet at bedtime': 'सोने से पहले एक गोली लें',
        'take one tablet twice daily': 'दिन में दो बार एक गोली लें',
        'take one tablet once daily': 'प्रतिदिन एक गोली लें'
      },
      not_specified: { en: 'Not specified', hi: 'निर्दिष्ट नहीं' },
      no_specific_recovery: { en: 'No specific recovery period mentioned', hi: 'कोई विशेष स्वास्थ्य लाभ अवधि उल्लिखित नहीं है' }
    }
  },
  documents: {
    nav_dashboard: { en: 'Dashboard', hi: 'डैशबोर्ड' },
    nav_documents: { en: 'Documents', hi: 'दस्तावेज़' },
    nav_summary: { en: 'Summary', hi: 'सारांश' },
    nav_medications: { en: 'Medications', hi: 'दवाइयाँ' },
    nav_checklist: { en: 'Checklist', hi: 'चेकलिस्ट' },
    nav_askai: { en: 'Ask AI', hi: 'AI से पूछें' },
    nav_profile: { en: 'Profile', hi: 'प्रोफ़ाइल' },
    sign_out: { en: 'Sign Out', hi: 'साइन आउट' },
    upload_title: { en: 'Upload Your Document', hi: 'अपना दस्तावेज़ अपलोड करें' },
    prescription_btn: { en: 'Prescription / Report', hi: 'नुस्खा / रिपोर्ट' },
    medical_btn: { en: 'Medical Image (X-ray, MRI, CT Scan)', hi: 'मेडिकल इमेज (एक्स-रे, MRI, CT स्कैन)' },
    drop_file_here: { en: 'Drop your file here', hi: 'अपनी फ़ाइल यहाँ छोड़ें' },
    click_to_browse: { en: 'or click to browse from your device', hi: 'या अपने डिवाइस से ब्राउज़ करने के लिए क्लिक करें' },
    analyzing: { en: 'Analyzing...', hi: 'विश्लेषण हो रहा है...' },
    processing: { en: 'Processing your document', hi: 'आपका दस्तावेज़ प्रोसेस हो रहा है' },
    previous_uploads: { en: 'Previous Uploads', hi: 'पिछली अपलोड' },
    no_uploads: { en: 'No uploads yet', hi: 'अभी तक कोई अपलोड नहीं' },
    view_analysis: { en: 'View Analysis', hi: 'विश्लेषण देखें' },
    delete: { en: 'Delete', hi: 'हटाएं' },
    load_sample: { en: 'Load Sample Prescription', hi: 'सैंपल नुस्खा लोड करें' },
    analysis_options: { en: 'Analysis Options', hi: 'विश्लेषण विकल्प' },
    patient_age: { en: 'Patient Age', hi: 'रोगी की आयु' },
    image_type: { en: 'Image Type', hi: 'इमेज प्रकार' },
    img_xray: { en: 'X-ray', hi: 'एक्स-रे' },
    img_mri: { en: 'MRI Scan', hi: 'MRI स्कैन' },
    img_ct: { en: 'CT Scan', hi: 'CT स्कैन' },
    img_ultrasound: { en: 'Ultrasound', hi: 'अल्ट्रासाउंड' },
    optional: { en: '(Optional)', hi: '(वैकल्पिक)' },
    eg_45: { en: 'e.g. 45', hi: 'जैसे 45' },
    output_language: { en: 'Output Language', hi: 'आउटपुट भाषा' },
    analyse_with_ai: { en: 'Analyse with AI', hi: 'AI से विश्लेषण करें' },
    ai_ready: { en: 'AI Ready to Analyse', hi: 'AI विश्लेषण के लिए तैयार' },
    upload_instruction: { en: 'Upload your document or paste your prescription, then click Analyse.', hi: 'अपना दस्तावेज़ अपलोड करें या नुस्खा पेस्ट करें, फिर विश्लेषण के लिए क्लिक करें।' },
    plain_diagnosis: { en: 'Plain-language diagnosis', hi: 'सरल भाषा में निदान' },
    exact_schedule: { en: 'Exact medication schedule', hi: 'सही दवाई का शेड्यूल' },
    side_effect_alerts: { en: 'Side effect alerts', hi: 'साइड इफेक्ट अलर्ट' },
    followup_check: { en: 'Follow-up checklist', hi: 'फॉलो-अप चेकलिस्ट' },
    no_document: { en: 'No document? Try this:', hi: 'कोई दस्तावेज़ नहीं? यह आज़माएं:' },
    sample_prescription_title: { en: 'Apollo Hospitals — Bacterial Pneumonia discharge', hi: 'अपोलो अस्पताल — बैक्टीरियल निमोनिया डिस्चार्ज' },
    disclaimer: { en: 'Aushadh AI only simplifies what your doctor wrote. It never adds advice, changes dosages, or uses outside information.', hi: 'Aushadh AI केवल जो आपके डॉक्टर ने लिखा है उसे सरल बनाता है। यह कभी सलाह नहीं जोड़ता, खुराक नहीं बदलता, या बाहरी जानकारी का उपयोग नहीं करता।' },
    drop_medical_image: { en: 'Drop your medical image', hi: 'अपनी मेडिकल इमेज छोड़ें' },
    xray_mri_ct: { en: 'X-ray, MRI, CT Scan, Ultrasound', hi: 'X-ray, MRI, CT स्कैन, अल्ट्रासाउंड' }
  },
  diagnosis: {
    title: { en: 'Health Summary', hi: 'स्वास्थ्य सारांश' },
    nav_dashboard: { en: 'Dashboard', hi: 'डैशबोर्ड' },
    nav_documents: { en: 'Documents', hi: 'दस्तावेज़' },
    nav_summary: { en: 'Summary', hi: 'सारांश' },
    nav_medications: { en: 'Medications', hi: 'दवाइयाँ' },
    nav_checklist: { en: 'Checklist', hi: 'चेकलिस्ट' },
    nav_askai: { en: 'Ask AI', hi: 'AI से पूछें' },
    nav_profile: { en: 'Profile', hi: 'प्रोफ़ाइल' },
    sign_out: { en: 'Sign Out', hi: 'साइन आउट' },
    your_health_summary: { en: 'Your Health Summary', hi: 'आपका स्वास्थ्य सारांश' },
    ai_simplified: { en: 'AI-simplified from your prescription by Aushadh AI', hi: 'Aushadh AI द्वारा आपके नुस्खे से AI-सरलीकृत' },
    verified: { en: 'verified', hi: 'सत्यापित' },
    confidence_score: { en: 'AI Confidence Score', hi: 'AI विश्वास स्कोर' },
    high_confidence: { en: 'High confidence - detailed analysis available', hi: 'उच्च विश्वास - विस्तृत विश्लेषण उपलब्ध' },
    good_confidence: { en: 'Good confidence level', hi: 'अच्छा विश्वास स्तर' },
    moderate_confidence: { en: 'Moderate confidence - verify with doctor', hi: 'मध्यम विश्वास - डॉक्टर से पुष्टि करें' },
    what_happened: { en: 'What Happened — In Simple Words', hi: 'क्या हुआ — सादे शब्दों में' },
    easy_read_summary: { en: 'Easy-to-read summary for you and your family', hi: 'आपके और परिवार के लिए आसान पठन सारांश' },
    copy: { en: 'Copy', hi: 'कॉपी करें' },
    share_whatsapp: { en: 'Share on WhatsApp', hi: 'WhatsApp पर साझा करें' },
    listen: { en: 'Listen', hi: 'सुनें' },
    read_aloud: { en: 'Read Aloud', hi: 'ऊपर से पढ़ें' },
    diagnosis_explained: { en: 'Diagnosis Explained', hi: 'निदान समझाया' },
    doctors_words: { en: "Doctor's Words → Plain Language", hi: "डॉक्टर के शब्द → सादी भाषा" },
    doctors_original: { en: "Doctor's Original", hi: 'डॉक्टर का मूल' },
    simplified_ai: { en: 'Simplified by AI', hi: 'AI द्वारा सरलीकृत' },
    your_medications: { en: 'Your Medications', hi: 'आपकी दवाइयाँ' },
    full_list: { en: 'Full List', hi: 'पूरी सूची' },
    what_watch: { en: 'What to Watch For', hi: 'क्या ध्यान दें' },
    doctors_notes: { en: "Doctor's Notes", hi: 'डॉक्टर के नोट्स' },
    possible_side_effects: { en: 'Possible Side Effects', hi: 'संभावित साइड इफेक्ट्स' },
    call_doctor: { en: 'Call doctor immediately if:', hi: 'तुरंत डॉक्टर को बुलाएं अगर:' },
    followup_checklist: { en: 'Follow-up Checklist', hi: 'फॉलो-अप चेकलिस्ट' },
    full_schedule: { en: 'Full Medication Schedule', hi: 'पूर्ण दवाई शेड्यूल' },
    ask_ai_question: { en: 'Ask AI a Question', hi: 'AI से पूछें' },
    export_pdf: { en: 'Export PDF', hi: 'PDF निर्यात करें' },
    diagnosis_label: { en: 'Diagnosis', hi: 'निदान' },
    original_diagnosis: { en: 'What the doctor wrote', hi: 'डॉक्टर ने क्या लिखा' },
    simple_explanation: { en: 'What it means', hi: 'इसका क्या मतलब है' },
    watch_for: { en: 'Watch For', hi: 'ध्यान दें' },
    emergency: { en: 'EMERGENCY', hi: 'आपातकालीन' },
    recovery: { en: 'Recovery', hi: 'स्वास्थ्य लाभ' },
    share_summary: { en: 'Share Summary', hi: 'सारांश साझा करें' },
    download_pdf: { en: 'Download PDF', hi: 'PDF डाउनलोड करें' },
    view_medications: { en: 'View Medications', hi: 'दवाइयाँ देखें' },
    patient_doctor_details: { en: 'Patient & Doctor Details', hi: 'रोगी और डॉक्टर विवरण' },
    patient_age: { en: 'Patient Age', hi: 'रोगी की आयु' },
    gender: { en: 'Gender', hi: 'लिंग' },
    doctor_label: { en: 'Doctor', hi: 'डॉक्टर' },
    hospital: { en: 'Hospital', hi: 'अस्पताल' },
    recovery_timeline: { en: 'Recovery Timeline', hi: 'स्वास्थ्य लाभ समयरेखा' },
    listen: { en: 'Listen', hi: 'सुनें' },
    stop_listening: { en: 'Stop', hi: 'रुकें' },
    no_medications_found: { en: 'No medications found in your document', hi: 'आपके दस्तावेज़ में कोई दवाई नहीं मिली' },
    in_plain_words: { en: 'In Plain Words', hi: 'सादे शब्दों में' },
    full_list: { en: 'Full List', hi: 'पूरी सूची' },
    drug_interactions_heading: { en: 'Drug Interactions', hi: 'दवाइयों की अंतःक्रियाएं' },
    drug_interactions_desc: { en: 'These medicines may affect each other. Consult your doctor.', hi: 'ये दवाइयाँ एक-दूसरे को प्रभावित कर सकती हैं। अपने डॉक्टर से परामर्श करें।' },
    severity_high: { en: 'High', hi: 'उच्च' },
    severity_medium: { en: 'Medium', hi: 'मध्यम' },
    severity_low: { en: 'Low', hi: 'कम' },
    duration_label: { en: 'Duration', hi: 'अवधि' },
    with_food_label: { en: 'With Food', hi: 'भोजन के साथ' },
    fda_warnings: { en: 'FDA Warnings', hi: 'FDA चेतावनियाँ' },
    fda_side_effects: { en: 'Side Effects', hi: 'साइड इफेक्ट्स' },
    storage_instructions: { en: 'Storage', hi: 'भंडारण' },
    show_more: { en: 'Show more', hi: 'और देखें' },
    show_less: { en: 'Show less', hi: 'कम देखें' },
    recovery_days: { en: 'days', hi: 'दिन' },
    medical_findings: { en: 'Medical Image Findings', hi: 'मेडिकल इमेज निष्कर्ष' },
    findings_normal: { en: 'Normal', hi: 'सामान्य' },
    findings_abnormal: { en: 'Abnormal', hi: 'असामान्य' },
    findings_critical: { en: 'Critical', hi: 'गंभीर' },
    quick_checklist: { en: 'Quick Checklist', hi: 'त्वरित चेकलिस्ट' },
    view_full_checklist: { en: 'View full checklist', hi: 'पूरी चेकलिस्ट देखें' },
    no_interactions: { en: 'No known drug interactions found.', hi: 'कोई ज्ञात दवा अंतःक्रिया नहीं मिली।' },
    checklist_items: { en: 'checklist items', hi: 'चेकलिस्ट आइटम' }
  },
  medications: {
    title: { en: 'Medications', hi: 'दवाइयाँ' },
    nav_dashboard: { en: 'Dashboard', hi: 'डैशबोर्ड' },
    nav_documents: { en: 'Documents', hi: 'दस्तावेज़' },
    nav_summary: { en: 'Summary', hi: 'सारांश' },
    nav_medications: { en: 'Medications', hi: 'दवाइयाँ' },
    nav_checklist: { en: 'Checklist', hi: 'चेकलिस्ट' },
    nav_askai: { en: 'Ask AI', hi: 'AI से पूछें' },
    nav_profile: { en: 'Profile', hi: 'प्रोफ़ाइल' },
    sign_out: { en: 'Sign Out', hi: 'साइन आउट' },
    active_meds: { en: 'Active Medications', hi: 'सक्रिय दवाइयाँ' },
    active_meds_short: { en: 'Active Meds', hi: 'सक्रिय दवाइयाँ' },
    dosage: { en: 'Dosage', hi: 'खुराक' },
    timing: { en: 'Timing', hi: 'समय' },
    duration: { en: 'Duration', hi: 'अवधि' },
    instructions: { en: 'Instructions', hi: 'निर्देश' },
    with_food: { en: 'With Food', hi: 'खाने के साथ' },
    active: { en: 'ACTIVE', hi: 'सक्रिय' },
    no_meds: { en: 'No medications found', hi: 'कोई दवाई नहीं मिली' },
    print_schedule: { en: 'Print Schedule', hi: 'शेड्यूल प्रिंट करें' },
    todays_schedule: { en: "Today's Schedule", hi: 'आज का शेड्यूल' },
    when_to_take: { en: 'When to take each medicine', hi: 'कौन सी दवाई कब लेनी है' },
    morning: { en: 'Morning', hi: 'सुबह' },
    afternoon: { en: 'Afternoon', hi: 'दोपहर' },
    night: { en: 'Night', hi: 'रात' },
    no_meds_this_time: { en: 'No medicines this time', hi: 'इस समय कोई दवाई नहीं' },
    medicines: { en: 'medicines', hi: 'दवाइयाँ' },
    morning_dose: { en: 'Morning Dose', hi: 'सुबह की खुराक' },
    evening_dose: { en: 'Evening Dose', hi: 'शाम की खुराक' },
    longest_course: { en: 'Longest Course', hi: 'सबसे लंबी अवधि' },
    not_specified: { en: 'Not specified', hi: 'निर्दिष्ट नहीं' },
    adherence_tracker: { en: 'Adherence Tracker', hi: 'पालन ट्रैकर' },
    history: { en: 'History', hi: 'इतिहास' },
    clear: { en: 'Clear', hi: 'साफ करें' },
    day_rate: { en: '30-Day Rate', hi: '30 दिन का रेट' },
    day_streak: { en: 'Day Streak', hi: 'दिन की स्ट्रीक' },
    doses_taken: { en: 'Doses Taken', hi: 'खुराक ली गई' },
    full_medication_table: { en: 'Full Medication Table', hi: 'पूरी दवाइयों की तालिका' },
    print: { en: 'Print', hi: 'प्रिंट' },
    recovery_timeline: { en: 'Recovery Timeline', hi: 'स्वास्थ्य लाभ समयरेखा' },
    no_specific_recovery: { en: 'No specific recovery period mentioned', hi: 'कोई विशेष स्वास्थ्य लाभ अवधि उल्लिखित नहीं है' },
    health_summary: { en: 'Health Summary', hi: 'स्वास्थ्य सारांश' },
    checklist: { en: 'Checklist', hi: 'चेकलिस्ट' },
    new_upload: { en: 'New Upload', hi: 'नई अपलोड' },
    no_meds_yet: { en: 'No Medications Yet', hi: 'अभी तक कोई दवाई नहीं' },
    upload_prescription: { en: 'Upload your prescription to see your complete medication schedule here.', hi: 'अपना नुस्खा अपलोड करें अपना पूरा दवाई शेड्यूल यहाँ देखने के लिए।' },
    upload_document: { en: 'Upload Document', hi: 'दस्तावेज़ अपलोड करें' },
    mark_as_taken: { en: 'Mark as Taken', hi: 'लिया हुआ चिह्नित करें' },
    medicine: { en: 'Medicine', hi: 'दवाई' }
  },
  checklist: {
    title: { en: 'Checklist & Alerts', hi: 'चेकलिस्ट और अलर्ट' },
    nav_dashboard: { en: 'Dashboard', hi: 'डैशबोर्ड' },
    nav_documents: { en: 'Documents', hi: 'दस्तावेज़' },
    nav_summary: { en: 'Summary', hi: 'सारांश' },
    nav_medications: { en: 'Medications', hi: 'दवाइयाँ' },
    nav_checklist: { en: 'Checklist', hi: 'चेकलिस्ट' },
    nav_askai: { en: 'Ask AI', hi: 'AI से पूछें' },
    nav_profile: { en: 'Profile', hi: 'प्रोफ़ाइल' },
    sign_out: { en: 'Sign Out', hi: 'साइन आउट' },
    all_tasks: { en: 'All Tasks', hi: 'सभी कार्य' },
    pending: { en: 'Pending', hi: 'बाकी' },
    completed: { en: 'Completed', hi: 'पूर्ण' },
    side_effects: { en: 'Side Effects', hi: 'साइड इफेक्ट्स' },
    high_severity: { en: 'High Priority', hi: 'उच्च प्राथमिकता' },
    low_severity: { en: 'Low Priority', hi: 'कम प्राथमिकता' },
    emergency_alert: { en: 'Emergency Alert', hi: 'आपातकालीन अलर्ट' },
    no_tasks: { en: 'No tasks yet', hi: 'अभी तक कोई कार्य नहीं' },
    followup_guide: { en: 'Follow-up Guide', hi: 'फॉलो-अप गाइड' },
    post_consultation: { en: 'Post-Consultation', hi: 'परामर्श के बाद' },
    personalized_breakdown: { en: "Your personalised breakdown of what to watch for and your next steps.", hi: 'आपके लिए क्या देखना है और आपके अगले कदमों का व्यक्तिगत विवरण।' },
    side_effects_alerts: { en: 'Side Effects Alerts', hi: 'साइड इफेक्ट्स अलर्ट' },
    view_medications: { en: 'View Medications', hi: 'दवाइयाँ देखें' },
    your_followup_checklist: { en: 'Your Follow-up Checklist', hi: 'आपकी फॉलो-अप चेकलिस्ट' },
    seek_help: { en: 'SEEK HELP', hi: 'मदद लें' },
    expected: { en: 'EXPECTED', hi: 'अपेक्षित' },
    watch: { en: 'WATCH', hi: 'ध्यान दें' },
    family_status: { en: 'Family Status Update', hi: 'परिवार की स्थिति अपडेट' },
    copy: { en: 'Copy', hi: 'कॉपी' },
    whatsapp: { en: 'WhatsApp', hi: 'व्हाट्सएप' },
    no_side_effects: { en: 'No side effects noted.', hi: 'कोई साइड इफेक्ट्स नहीं दर्ज किया गया।' },
    find_hospital: { en: 'Find a Hospital', hi: 'अस्पताल खोजें' },
    health_summary: { en: 'Health Summary', hi: 'स्वास्थ्य सारांश' },
    medicines: { en: 'Medications', hi: 'दवाइयाँ' },
    new_upload: { en: 'New Upload', hi: 'नई अपलोड' },
    upload_document: { en: 'Upload Document', hi: 'दस्तावेज़ अपलोड करें' },
    no_checklist_items: { en: 'No checklist items found.', hi: 'कोई चेकलिस्ट आइटम नहीं मिला।' }
  },
  chat: {
    title: { en: 'Ask AI', hi: 'AI से पूछें' },
    nav_dashboard: { en: 'Dashboard', hi: 'डैशबोर्ड' },
    nav_documents: { en: 'Documents', hi: 'दस्तावेज़' },
    nav_summary: { en: 'Summary', hi: 'सारांश' },
    nav_medications: { en: 'Medications', hi: 'दवाइयाँ' },
    nav_checklist: { en: 'Checklist', hi: 'चेकलिस्ट' },
    nav_askai: { en: 'Ask AI', hi: 'AI से पूछें' },
    nav_profile: { en: 'Profile', hi: 'प्रोफ़ाइल' },
    sign_out: { en: 'Sign Out', hi: 'साइन आउट' },
    placeholder: { en: 'Ask about your prescription...', hi: 'अपने नुस्खे के बारे में पूछें...' },
    placeholder_alt: { en: 'Ask anything about your health...', hi: 'अपने स्वास्थ्य के बारे में कुछ भी पूछें...' },
    send: { en: 'Send', hi: 'भेजें' },
    suggested: { en: 'Suggested Questions', hi: 'सुझाए गए प्रश्न' },
    thinking: { en: 'Thinking...', hi: 'सोच रहे हैं...' },
    active_rx_context: { en: 'Active Prescription Context', hi: 'सक्रिय नुस्खा संदर्भ' },
    rx_loaded: { en: 'Your prescription is loaded.', hi: 'आपका नुस्खा लोड है।' },
    no_rx: { en: 'No prescription uploaded yet.', hi: 'अभी तक कोई नुस्खा अपलोड नहीं हुआ।' },
    upload_for_accurate: { en: 'Upload one for accurate answers.', hi: 'सटीक उत्तरों के लिए एक अपलोड करें।' },
    welcome_msg1: { en: "Hi! I'm Aushadh AI. I can answer questions about your uploaded prescription — dosages, timing, side effects, and what your diagnosis means.", hi: 'नमस्ते! मैं Aushadh AI हूं। मैं आपके अपलोड किए गए नुस्खे के बारे में प्रश्नों का उत्तर दे सकता हूं — खुराक, समय, साइड इफेक्ट्स, और आपका निदान क्या मतलब है।' },
    welcome_msg2: { en: "I only answer from what your doctor wrote. For anything not in your prescription, I'll tell you to ask your doctor.", hi: 'मैं केवल आपके डॉक्टर ने जो लिखा है उसी से उत्तर देता हूं। नुस्खे में कुछ नहीं है तो मैं आपको बताऊंगा कि अपने डॉक्टर से पूछें।' },
    aushadh_ai: { en: 'Aushadh AI', hi: 'Aushadh AI' },
    you: { en: 'You', hi: 'आप' },
    disclaimer: { en: 'Aushadh AI answers only from your prescription. Always consult your doctor for medical decisions.', hi: 'Aushadh AI केवल आपके नुस्खे से उत्तर देता है। चिकित्सा निर्णयों के लिए हमेशा अपने डॉक्टर से परामर्श करें।' },
    loaded: { en: 'LOADED', hi: 'लोड' },
    // Chat starter questions
    starter_when_meds: { en: 'When should I take my medicines?', hi: 'मुझे दवाइयाँ कब लेनी है?' },
    starter_foods_avoid: { en: 'What foods should I avoid?', hi: 'मुझे कौन सी दवाइयाँ नहीं लेनी है?' },
    starter_doctor_again: { en: 'When should I see the doctor again?', hi: 'मुझे दोबारा कब दिखाना है?' },
    starter_watch_signs: { en: 'What are the warning signs to watch for?', hi: 'मुझे कौन से चेतावनी के संकेत देखने चाहिए?' },
    upload_one: { en: 'Upload one', hi: 'एक अपलोड करें' }
  },
  profile: {
    title: { en: 'Profile', hi: 'प्रोफ़ाइल' },
    nav_dashboard: { en: 'Dashboard', hi: 'डैशबोर्ड' },
    nav_documents: { en: 'Documents', hi: 'दस्तावेज़' },
    nav_summary: { en: 'Summary', hi: 'सारांश' },
    nav_medications: { en: 'Medications', hi: 'दवाइयाँ' },
    nav_checklist: { en: 'Checklist', hi: 'चेकलिस्ट' },
    nav_askai: { en: 'Ask AI', hi: 'AI से पूछें' },
    nav_profile: { en: 'Profile', hi: 'प्रोफ़ाइल' },
    sign_out: { en: 'Sign Out', hi: 'साइन आउट' },
    name: { en: 'Name', hi: 'नाम' },
    email: { en: 'Email', hi: 'ईमेल' },
    age: { en: 'Age', hi: 'उम्र' },
    language: { en: 'Language', hi: 'भाषा' },
    dark_mode: { en: 'Dark Mode', hi: 'डार्क मोड' },
    save_changes: { en: 'Save Changes', hi: 'बदलाव सहेजें' },
    cancel: { en: 'Cancel', hi: 'रद्द करें' },
    saved: { en: 'Saved!', hi: 'सहेजा गया!' },
    my_profile: { en: 'My Profile', hi: 'मेरी प्रोफ़ाइल' },
    edit_profile: { en: 'Edit Profile', hi: 'एडिट प्रोफ़ाइल' },
    analyses_done: { en: 'Analyses Done', hi: 'विश्लेषण पूर्ण' },
    active_meds: { en: 'Active Meds', hi: 'सक्रिय दवाइयाँ' },
    tasks_pending: { en: 'Tasks Pending', hi: 'कार्य बाकी' },
    last_confidence: { en: 'Last Confidence', hi: 'अंतिम विश्वास' },
    personal_info: { en: 'Personal Information', hi: 'व्यक्तिगत जानकारी' },
    first_name: { en: 'First Name', hi: 'पहला नाम' },
    last_name: { en: 'Last Name', hi: 'अंतिम नाम' },
    email_address: { en: 'Email Address', hi: 'ईमेल पता' },
    phone_number: { en: 'Phone Number', hi: 'फ़ोन नंबर' },
    city: { en: 'City', hi: 'शहर' },
    blood_group: { en: 'Blood Group', hi: 'रक्त समूह' },
    select_blood_group: { en: 'Select blood group', hi: 'रक्त समूह चुनें' },
    preferred_language: { en: 'Preferred Language', hi: 'पसंदीदा भाषा' },
    language_english: { en: 'English', hi: 'अंग्रेज़ी' },
    known_allergies: { en: 'Known Allergies', hi: 'ज्ञात एलर्जी' },
    medical_conditions: { en: 'Medical Conditions', hi: 'चिकित्सा स्थितियाँ' },
    emergency_contact: { en: 'Emergency Contact', hi: 'आपातकालीन संपर्क' },
    contact_name: { en: 'Contact Name', hi: 'संपर्क नाम' },
    phone: { en: 'Phone', hi: 'फ़ोन' },
    relationship: { en: 'Relationship', hi: 'संबंध' },
    primary_doctor: { en: 'Primary Doctor', hi: 'प्राथमिक डॉक्टर' },
    doctor_name: { en: 'Doctor Name', hi: 'डॉक्टर का नाम' },
    specialty: { en: 'Specialty', hi: 'विशेषता' },
    hospital_clinic: { en: 'Hospital / Clinic', hi: 'अस्पताल / क्लीनिक' },
    account: { en: 'Account', hi: 'खाता' },
    clear_data: { en: 'Clear Analysis Data', hi: 'विश्लेषण डेटा साफ़ करें' },
    export_data: { en: 'Export My Data', hi: 'मेरा डेटा निर्यात करें' },
    member: { en: 'Member', hi: 'सदस्य' },
    age_format: { en: 'Age:', hi: 'उम्र:' },
    language_en: { en: '🌐 English', hi: '🌐 हिंदी' },
    rel_spouse: { en: 'Spouse', hi: 'जीवनसाथी' },
    rel_parent: { en: 'Parent', hi: 'माता-पिता' },
    rel_child: { en: 'Child', hi: 'बच्चा' },
    rel_sibling: { en: 'Sibling', hi: 'भाई-बहन' },
    rel_friend: { en: 'Friend', hi: 'मित्र' },
    rel_other: { en: 'Other', hi: 'अन्य' }
  }
};

let currentLang = localStorage.getItem('medbuddy_language') || 'en';

function getCurrentLanguage() {
  return currentLang;
}

function setLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('medbuddy_language', lang);
  applyTranslations();
  document.documentElement.lang = lang === 'hi' ? 'hi' : 'en';
  // Update language toggle buttons
  const enBtn = document.getElementById('lang-en');
  const hiBtn = document.getElementById('lang-hi');
  if (enBtn && hiBtn) {
    enBtn.classList.toggle('active', lang === 'en');
    hiBtn.classList.toggle('active', lang === 'hi');
  }
  // Reload page to refresh all content
  window.location.reload();
}

function translateMedTerm(type, value) {
  if (!value) return value;
  const lang = getCurrentLanguage();
  if (lang !== 'hi') return value;
  
  // Handle instructions specially
  if (type === 'instructions' || type === 'instruction') {
    const terms = TRANSLATIONS.dashboard?.medication_terms?.instructions;
    if (terms) {
      for (const [en, hi] of Object.entries(terms)) {
        const regex = new RegExp(en, 'gi');
        if (regex.test(value)) {
          return value.replace(regex, hi);
        }
      }
    }
  }
  
  // Handle timing and duration
  const terms = TRANSLATIONS.dashboard?.medication_terms?.[type];
  if (!terms) return value;
  let result = value;
  for (const [en, hi] of Object.entries(terms)) {
    const regex = new RegExp(en, 'gi');
    if (regex.test(result)) {
      result = result.replace(regex, hi);
    }
  }
  return result;
}

// ── API: Validate medical image (check if it's a real scan vs document) ─────
async function apiValidateMedicalImage(file) {
  const form = new FormData();
  form.append('file', file);
  
  try {
    const res = await fetch(`${API}/validate-medical-image`, { method: 'POST', body: form });
    
    if (!res.ok) {
      const e = await res.json();
      throw new Error(e.detail || 'Medical image validation failed');
    }
    
    const result = await res.json();
    return result;
  } catch (err) {
    throw err;
  }
}

function translateNotSpecified() {
  const lang = getCurrentLanguage();
  return lang === 'hi' ? 'निर्दिष्ट नहीं' : 'Not specified';
}

async function translateToHindi(text) {
  if (!text || text === '—') return text;
  try {
    const response = await fetch(`https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=en|hi`);
    const data = await response.json();
    return data.responseData?.translatedText || text;
  } catch(e) { return text; }
}

const checklistTranslationsCache = {};

async function translateChecklistItem(text) {
  const lang = getCurrentLanguage();
  if (lang === 'en') return text;
  
  if (checklistTranslationsCache[text]) {
    return checklistTranslationsCache[text];
  }
  
  const translated = await translateToHindi(text);
  checklistTranslationsCache[text] = translated;
  return translated;
}

function t(key) {
  const page = window.location.pathname.split('/').pop().replace('.html', '');
  const langKey = currentLang === 'hi' ? 'hi' : 'en';
  
  if (TRANSLATIONS[page] && TRANSLATIONS[page][key]) {
    return TRANSLATIONS[page][key][langKey] || key;
  }
  return key;
}

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    el.textContent = t(key);
  });
  
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    el.placeholder = t(key);
  });
}

// Initialize language on load
(function initLanguage() {
  const savedLang = localStorage.getItem('medbuddy_language');
  if (savedLang) {
    currentLang = savedLang;
    document.documentElement.lang = savedLang === 'hi' ? 'hi' : 'en';
  }
})();

// ── Auth ──────────────────────────────────────────────
let authValidated = false;

function requireAuth() {
  const current = window.location.pathname.split('/').pop();
  const publicPages = ['index.html', 'login.html', ''];
  const loggedIn = localStorage.getItem('medbuddy_logged_in');
  const token = localStorage.getItem('medbuddy_token');
  
  console.log('=== requireAuth START ===');
  console.log('current page:', current);
  console.log('loggedIn:', loggedIn);
  console.log('token exists:', !!token);
  
  if (!publicPages.includes(current)) {
    if (!loggedIn || !token) {
      console.log('FAIL: No token - redirecting to login');
      sessionStorage.setItem('medbuddy_redirect', window.location.href);
      window.location.replace('/login.html');
      return;
    }
    
    // Skip server validation for demo users
    if (token === 'demo_token') {
      console.log('Demo user - skipping server validation');
      authValidated = true;
      return;
    }
    
    console.log('Token exists, validating with server...');
    
    // Don't block page loading - do auth check in background
    const authUrl = `${API}/auth/me`;
    
    fetch(authUrl, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => {
      console.log('Auth check response:', res.status, res.statusText);
      if (!res.ok) {
        console.log('FAIL: Auth check failed with', res.status);
        clearAllStorage();
        window.location.replace('/login.html');
      } else {
        console.log('Auth OK');
        authValidated = true;
        initSessionTimeout();
      }
    })
    .catch(err => {
      console.error('Auth check exception:', err);
      // Don't redirect on network error - let user see the page
      authValidated = true;
    });
  }
}

function showAuthLoading() {
  // Prevent duplicate overlays
  if (document.getElementById('auth-overlay')) return;
  
  // Create overlay immediately
  const overlay = document.createElement('div');
  overlay.id = 'auth-overlay';
  overlay.style.cssText = 'position:fixed;inset:0;background:#fff;z-index:99999;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:16px';
  overlay.innerHTML = '<div class="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div><p style="color:#181c20;font-family:Public Sans,sans-serif">Verifying session...</p>';
  
  // Insert at beginning of body to ensure it's on top
  document.body.insertBefore(overlay, document.body.firstChild);
  
  // Make body visible in case it was hidden
  document.body.style.display = '';
}

function hideAuthLoading() {
  const overlay = document.getElementById('auth-overlay');
  if (overlay) overlay.remove();
}

function getUser() {
  return JSON.parse(localStorage.getItem('medbuddy_user') || '{}');
}

function saveUser(user, token) {
  localStorage.setItem('medbuddy_user', JSON.stringify(user));
  if (token) {
    localStorage.setItem('medbuddy_token', token);
  }
}

function clearAllStorage() {
  localStorage.removeItem('medbuddy_logged_in');
  localStorage.removeItem('medbuddy_token');
  localStorage.removeItem('medbuddy_user');
  localStorage.removeItem('medbuddy_analysis');
  localStorage.removeItem('medbuddy_history');
  localStorage.removeItem('medbuddy_notifications');
  localStorage.removeItem('medbuddy_dark_mode');
  sessionStorage.removeItem('medbuddy_analysis_backup');
  sessionStorage.removeItem('medbuddy_redirect');
}

function logout() {
  const token = localStorage.getItem('medbuddy_token');
  if (token) {
    fetch(`${API}/auth/logout`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    }).catch(() => {});
  }
  localStorage.removeItem('medbuddy_logged_in');
  localStorage.removeItem('medbuddy_token');
  localStorage.removeItem('medbuddy_user');
  window.location.replace('/login.html');
}

// ── Session Timeout ─────────────────────────────────────────
const SESSION_TIMEOUT_MS = 30 * 60 * 1000;
const SESSION_WARNING_MS = 27 * 60 * 1000;
let sessionTimer = null;
let sessionWarningTimer = null;
let sessionWarningModal = null;

function resetSessionTimer() {
  clearTimeout(sessionTimer);
  clearTimeout(sessionWarningTimer);
  
  if (!localStorage.getItem('medbuddy_logged_in') || !localStorage.getItem('medbuddy_token')) {
    return;
  }
  
  sessionWarningTimer = setTimeout(showSessionWarning, SESSION_WARNING_MS);
  sessionTimer = setTimeout(autoLogout, SESSION_TIMEOUT_MS);
}

function showSessionWarning() {
  if (sessionWarningModal) return;
  
  let timeLeft = 180;
  
  sessionWarningModal = document.createElement('div');
  sessionWarningModal.id = 'session-warning-modal';
  sessionWarningModal.className = 'fixed inset-0 bg-black/60 flex items-center justify-center z-50';
  sessionWarningModal.innerHTML = `
    <div class="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-sm mx-4 shadow-2xl">
      <div class="text-center">
        <span class="material-symbols-outlined text-4xl text-amber-500 mb-2">timer</span>
        <h3 class="text-xl font-bold text-gray-800 dark:text-white mb-2">Session Expiring Soon</h3>
        <p class="text-gray-600 dark:text-gray-300 mb-4">You will be logged out in <span id="session-countdown" class="font-bold text-amber-600">3:00</span> due to inactivity.</p>
        <div class="flex gap-3 justify-center">
          <button id="session-stay-logged" class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors">Stay Logged In</button>
          <button id="session-logout-now" class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors">Logout Now</button>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(sessionWarningModal);
  
  const countdownEl = document.getElementById('session-countdown');
  const countdownInterval = setInterval(() => {
    timeLeft--;
    const mins = Math.floor(timeLeft / 60);
    const secs = timeLeft % 60;
    countdownEl.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
    
    if (timeLeft <= 0) {
      clearInterval(countdownInterval);
    }
  }, 1000);
  
  document.getElementById('session-stay-logged').addEventListener('click', () => {
    clearInterval(countdownInterval);
    closeSessionWarning();
    refreshSession();
  });
  
  document.getElementById('session-logout-now').addEventListener('click', () => {
    clearInterval(countdownInterval);
    closeSessionWarning();
    doAutoLogout();
  });
}

function closeSessionWarning() {
  if (sessionWarningModal) {
    sessionWarningModal.remove();
    sessionWarningModal = null;
  }
  resetSessionTimer();
}

function refreshSession() {
  const token = localStorage.getItem('medbuddy_token');
  if (!token) return;
  
  fetch(`${API}/auth/refresh-session`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  }).catch(() => {});
}

function autoLogout() {
  closeSessionWarning();
  doAutoLogout();
}

function doAutoLogout() {
  const token = localStorage.getItem('medbuddy_token');
  if (token) {
    fetch(`${API}/auth/logout`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    }).catch(() => {});
  }
  localStorage.removeItem('medbuddy_logged_in');
  localStorage.removeItem('medbuddy_token');
  localStorage.removeItem('medbuddy_user');
  window.location.replace('/login.html');
}

function initSessionTimeout() {
  const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
  events.forEach(event => {
    document.addEventListener(event, resetSessionTimer, { passive: true });
  });
  resetSessionTimer();
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

// ── Sidebar Toggle (Mobile) ─────────────────────────────────
let sidebarOpen = false;

function toggleSidebar() {
  const sidebar = document.querySelector('aside');
  const separator = document.querySelector('.sidebar-separator');
  
  if (!sidebarOpen) {
    sidebar.classList.remove('hidden');
    sidebar.classList.add('flex');
    sidebar.classList.add('animate-fade-in');
    if (separator) {
      separator.classList.remove('hidden');
      separator.classList.add('flex', 'animate-fade-in');
    }
    // Add overlay
    if (!document.getElementById('sidebar-overlay')) {
      const overlay = document.createElement('div');
      overlay.id = 'sidebar-overlay';
      overlay.className = 'fixed inset-0 bg-black/50 z-30 md:hidden';
      overlay.onclick = toggleSidebar;
      overlay.style.animation = 'fadeIn 0.2s ease-out';
      document.body.appendChild(overlay);
    }
  } else {
    sidebar.classList.add('hidden');
    sidebar.classList.remove('flex', 'animate-fade-in');
    if (separator) {
      separator.classList.add('hidden');
      separator.classList.remove('flex', 'animate-fade-in');
    }
    const overlay = document.getElementById('sidebar-overlay');
    if (overlay) overlay.remove();
  }
  sidebarOpen = !sidebarOpen;
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

  // Push to MongoDB if logged in
  if (localStorage.getItem('medbuddy_logged_in')) {
    if (data.medications) {
      saveMedicationsToServer(data.medications);
    }
    saveAnalysisToServer(data);
  }

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
    const newHistory = filtered.slice(0, 5);
    localStorage.setItem('medbuddy_history', JSON.stringify(newHistory));

    if (localStorage.getItem('medbuddy_logged_in')) {
      saveAnalysisHistoryToServer(newHistory);
    }

    // Save notification
    saveNotification({
      title: 'New Analysis Complete',
      desc: data.summary_en?.substring(0, 60) || 'Health summary ready',
      type: 'analysis'
    });
  } catch(e) {}
}

async function saveAnalysisToServer(data) {
  try {
    const token = localStorage.getItem('medbuddy_token');
    if (!token) return;
    
    await fetch(`${API}/auth/analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ analysis: data })
    });
  } catch(e) {
  }
}

async function saveAnalysisHistoryToServer(history) {
  try {
    const token = localStorage.getItem('medbuddy_token');
    if (!token) return;
    
    await fetch(`${API}/auth/analysis/history`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ history })
    });
  } catch(e) {
  }
}

async function saveMedicationsToServer(medications) {
  try {
    const token = localStorage.getItem('medbuddy_token');
    if (!token) return;
    
    const response = await fetch(`${API}/auth/medications`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ medications })
    });
  } catch(e) {
  }
}
function getAnalysis() {
  const primary = localStorage.getItem('medbuddy_analysis');
  if (primary) return JSON.parse(primary);
  const backup = sessionStorage.getItem('medbuddy_analysis_backup');
  if (backup) {
    localStorage.setItem('medbuddy_analysis', backup);
    return JSON.parse(backup);
  }
  // Check for demo data (not saved to any storage)
  if (window.DEMO_DATA) return window.DEMO_DATA;
  // Check sessionStorage for demo data backup
  const demoBackup = sessionStorage.getItem('medbuddy_demo_data');
  if (demoBackup) {
    try {
      return JSON.parse(demoBackup);
    } catch(e) {
      console.error('Error parsing demo data:', e);
    }
  }
  return null;
}

async function loadAnalysisFromServer() {
  try {
    const token = localStorage.getItem('medbuddy_token');
    if (!token) return null;
    
    const response = await fetch(`${API}/auth/analysis`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      if (data.analysis) {
        return data.analysis;
      }
    }
  } catch(e) {
  }
  return null;
}

async function loadHistoryFromServer() {
  try {
    const token = localStorage.getItem('medbuddy_token');
    if (!token) return null;
    
    const response = await fetch(`${API}/auth/analysis/history`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      if (data.history && data.history.length > 0) {
        localStorage.setItem('medbuddy_history', JSON.stringify(data.history));
        return data.history;
      }
    }
  } catch(e) {
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

async function loadHistoryFromServer() {
  try {
    const token = localStorage.getItem('medbuddy_token');
    if (!token) return null;
    
    const response = await fetch(`${API}/auth/analysis/history`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (response.ok) {
      const data = await response.json();
      if (data.history && data.history.length > 0) {
        localStorage.setItem('medbuddy_history', JSON.stringify(data.history));
        return data.history;
      }
    }
  } catch(e) {
  }
  return null;
}

// ── API: Clear all user data ───────────────────────────────
async function apiClearAllData() {
  const token = localStorage.getItem('medbuddy_token');
  if (!token) return false;
  
  try {
    const res = await fetch(`${API}/auth/clear-all-data`, {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!res.ok) {
      return false;
    }
    
    return res.ok;
  } catch(e) {
    return false;
  }
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
async function apiAnalyseFile(file, age, language, signal = null) {
  const form = new FormData();
  form.append('file', file);
  if (age) form.append('age', age);
  form.append('language', language || 'English');
  
  try {
    const res = await fetch(`${API}/analyse/file`, { method: 'POST', body: form, signal });
    
    if (!res.ok) {
      let errorMsg = 'Analysis failed';
      try {
        const e = await res.json();
        errorMsg = e.detail || e.message || errorMsg;
      } catch (jsonErr) {
        const text = await res.text();
        errorMsg = text || errorMsg;
      }
      throw new Error(errorMsg);
    }
    
    const result = await res.json();
    return result;
  } catch (err) {
    if (err.name === 'AbortError') {
      throw err;
    }
    throw err;
  }
}
async function apiAnalyseMedicalImage(file, age, language, imageType = null, signal = null) {
  const form = new FormData();
  form.append('file', file);
  if (age) form.append('age', age);
  form.append('language', language || 'English');
  if (imageType) form.append('image_type', imageType);
  
  try {
    const res = await fetch(`${API}/analyse/medical-image`, { method: 'POST', body: form, signal });
    
    if (!res.ok) {
      const e = await res.json();
      throw new Error(e.detail || 'Medical image analysis failed');
    }
    
    const result = await res.json();
    return result;
  } catch (err) {
    if (err.name === 'AbortError') {
      throw err;
    }
    throw err;
  }
}

// ── API: Analyse text ─────────────────────────────────
async function apiAnalyseText(text, age, language) {
  const form = new FormData();
  form.append('text', text);
  if (age) form.append('age', age);
  form.append('language', language || 'English');
  
  try {
    const res = await fetch(`${API}/analyse/text`, { method: 'POST', body: form });
    
    if (!res.ok) {
      const e = await res.json();
      throw new Error(e.detail || 'Analysis failed');
    }
    
    return await res.json();
  } catch (err) {
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
  try {
    const res = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history, context, language: language || 'English' }),
    });
    if (!res.ok) { 
      const e = await res.json().catch(() => ({ detail: 'Server error' })); 
      throw new Error(e.detail || 'Chat failed'); 
    }
    return res.json();
  } catch (e) {
    throw e;
  }
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

// ── Medication Reminder System ─────────────────────────────────────
const MED_TIME_SLOTS = {
  morning: { start: 6, end: 12, label: 'Morning', emoji: '☀️' },
  afternoon: { start: 12, end: 18, label: 'Afternoon', emoji: '🌤️' },
  night: { start: 18, end: 24, label: 'Night', emoji: '🌙' }
};

function getCurrentTimeSlot() {
  const hour = new Date().getHours();
  if (hour >= 6 && hour < 12) return 'morning';
  if (hour >= 12 && hour < 18) return 'afternoon';
  return 'night';
}

function medBelongsToSlot(medTiming, slot) {
  const t = (medTiming || '').toLowerCase();
  if (slot === 'morning') return /morning|am|breakfast|od|once\s*daily/i.test(t);
  if (slot === 'afternoon') return /afternoon|noon|midday|lunch|tds|tid|three\s*times/i.test(t);
  if (slot === 'night') return /night|evening|pm|bedtime|sleep|bd|twice/i.test(t);
  return false;
}

function getMedicationsForSlot(meds, slot) {
  if (!meds || !Array.isArray(meds)) return [];
  return meds.filter(m => medBelongsToSlot(m.timing, slot));
}

function getUnmarkedMedications(meds, slot) {
  if (!meds || meds.length === 0) return [];
  const todayKey = 'taken_' + new Date().toDateString();
  const taken = JSON.parse(localStorage.getItem(todayKey) || '[]');
  const slotMeds = getMedicationsForSlot(meds, slot);
  return slotMeds.filter(m => !taken.includes(m.name));
}

function hasSlotPassed(slot) {
  const hour = new Date().getHours();
  return hour > MED_TIME_SLOTS[slot].end;
}

function showMedicationAlert(meds, slot) {
  const existing = document.getElementById('medication-alert-banner');
  if (existing) existing.remove();
  const slotInfo = MED_TIME_SLOTS[slot];
  const missedMeds = getUnmarkedMedications(meds, slot);
  if (missedMeds.length === 0) return;
  const medList = missedMeds.map(m => `<span class="bg-amber-100 px-2 py-1 rounded-full text-xs font-bold mr-1">${m.name} ${m.dosage || ''}</span>`).join('');
  const alertHtml = `<div id="medication-alert-banner" class="bg-amber-50 border-2 border-amber-300 rounded-xl p-4 mb-4">
    <div class="flex items-start gap-3">
      <span class="text-3xl">${slotInfo.emoji}</span>
      <div class="flex-1">
        <div class="flex items-center justify-between">
          <p class="font-bold text-amber-800 text-sm">⏰ Medication Reminder</p>
          <button onclick="dismissMedAlert()" class="text-amber-500 hover:text-amber-700 text-lg">&times;</button>
        </div>
        <p class="text-sm text-amber-700 mt-1"><strong>${slotInfo.label}</strong> slot passed. Not marked taken:</p>
        <div class="mt-2 flex flex-wrap gap-1">${medList}</div>
        <button onclick="markMissedMeds('${slot}')" class="mt-3 w-full bg-amber-400 hover:bg-amber-500 text-amber-900 font-bold text-sm py-2.5 rounded-lg">Mark All as Taken</button>
      </div>
    </div>
  </div>`;
  const main = document.querySelector('main');
  if (main) main.insertAdjacentHTML('afterbegin', alertHtml);
}

function markMissedMeds(slot) {
  const meds = window.globalMeds;
  if (!meds) return;
  const missedMeds = getUnmarkedMedications(meds, slot);
  const todayKey = 'taken_' + new Date().toDateString();
  let taken = JSON.parse(localStorage.getItem(todayKey) || '[]');
  missedMeds.forEach(m => { if (!taken.includes(m.name)) taken.push(m.name); });
  localStorage.setItem(todayKey, JSON.stringify(taken));
  const banner = document.getElementById('medication-alert-banner');
  if (banner) banner.remove();
  updateReminderBadge();
  if (typeof updateAdherenceDisplayFromLocalStorage === 'function') updateAdherenceDisplayFromLocalStorage();
  showToast(missedMeds.length + ' medication(s) marked as taken!');
}

function dismissMedAlert() {
  const banner = document.getElementById('medication-alert-banner');
  if (banner) banner.style.display = 'none';
  localStorage.setItem('med_alert_dismissed', Date.now().toString());
}

function updateReminderBadge() {
  let meds = window.globalMeds;
  if (!meds || meds.length === 0) {
    const analysis = getAnalysis();
    if (analysis && analysis.medications) meds = analysis.medications;
  }
  if (!meds || meds.length === 0) return;
  const currentSlot = getCurrentTimeSlot();
  const missedMeds = getUnmarkedMedications(meds, currentSlot);
  const count = missedMeds.length;
  ['reminder-badge', 'nav-reminder-badge'].forEach(id => {
    const badge = document.getElementById(id);
    if (badge) {
      if (count > 0) {
        badge.textContent = count > 9 ? '9+' : count;
        badge.classList.remove('hidden');
      } else {
        badge.classList.add('hidden');
      }
    }
  });
}

function checkMedicationAlert() {
  let meds = window.globalMeds;
  if (!meds || meds.length === 0) {
    const analysis = getAnalysis();
    if (analysis && analysis.medications) meds = analysis.medications;
  }
  if (!meds || meds.length === 0) return;
  const dismissedTime = parseInt(localStorage.getItem('med_alert_dismissed') || '0');
  if (Date.now() - dismissedTime < 3600000) return;
  const currentSlot = getCurrentTimeSlot();
  const missedMeds = getUnmarkedMedications(meds, currentSlot);
  if (missedMeds.length > 0 && hasSlotPassed(currentSlot)) {
    showMedicationAlert(meds, currentSlot);
  }
}

function initReminderSystem() {
  setTimeout(() => { checkMedicationAlert(); updateReminderBadge(); }, 1000);
  setInterval(() => { checkMedicationAlert(); updateReminderBadge(); }, 300000);
}

// Add animation style
const reminderStyle = document.createElement('style');
reminderStyle.textContent = `@keyframes pulse-slow { 0%,100%{opacity:1} 50%{opacity:0.85} } .animate-pulse-slow{animation:pulse-slow 2s ease-in-out infinite} @keyframes bounce-in{0%{transform:scale(0.8);opacity:0}50%{transform:scale(1.05)}100%{transform:scale(1);opacity:1}} .animate-bounce-in{animation:bounce-in 0.4s ease forwards} @keyframes fadeIn{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:translateX(0)}} .animate-fade-in{animation:fadeIn 0.2s ease-out}`;
document.head.appendChild(reminderStyle);
// ── End Medication Reminder System ─────────────────────────────────

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
  if (data.recovery_days_min && data.recovery_days_max) {
    msg += `📅 *Recovery:* ${data.recovery_days_min}–${data.recovery_days_max} days\n\n`;
  }
  msg += `🩺 *Condition:* ${data.diagnosis?.simple_english || ''}\n\n`;
  const interactions = data.drug_interactions || [];
  if (interactions.length > 0) {
    msg += `⚠️ *Drug Interactions:*\n`;
    interactions.forEach(i => {
      msg += `  • ${i.drug_a} + ${i.drug_b} [${(i.severity||'Medium').toUpperCase()}]: ${(i.description||'').slice(0,100)}\n`;
    });
    msg += '\n';
  }
  msg += `💊 *Medicines:*\n`;
  (data.medications || []).forEach(m => {
    msg += `  • ${m.name} ${m.dosage} — ${m.timing} for ${m.duration}\n`;
  });
  const findings = data.findings || data.abnormalities || [];
  if (findings.length > 0) {
    msg += `\n🔍 *Medical Findings:*\n`;
    findings.forEach(f => {
      msg += `  • ${f.area||''}: ${(f.observation||f.text||'').slice(0,100)} (${f.severity||'Normal'})\n`;
    });
  }
  msg += `\n🚨 *Emergency:* ${data.emergency || ''}\n\n`;
  msg += `_Simplified by Aushadh AI — always consult your doctor_`;
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

function clearAllNotifications() {
  localStorage.setItem('medbuddy_notifications', JSON.stringify([]));
  localStorage.removeItem('medbuddy_analysis');
  sessionStorage.removeItem('medbuddy_analysis_backup');
  renderNotifications();
  updateNotificationBadge();
}

function createNotificationsPanel() {
  const style = document.createElement('style');
  style.textContent = `
    .mb-notif-panel{position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:90%;max-width:380px;background:#fff;border-radius:20px;box-shadow:0 25px 80px rgba(0,0,0,0.25);z-index:9999;font-family:'Public Sans',sans-serif;max-height:70vh;overflow-y:auto}
    .mb-notif-backdrop{position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);backdrop-filter:blur(8px);z-index:9998}
    .mb-notif-header{padding:16px 18px;border-bottom:1px solid #f1f4fa;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;background:#fff;z-index:1}
    .mb-notif-header-actions{display:flex;gap:8px;align-items:center}
    .mb-notif-header-title{font-weight:700;font-size:16px;color:#181c20}
    .mb-notif-close{background:none;border:none;font-size:20px;cursor:pointer;color:#6e797a;padding:4px}
    .mb-notif-close:hover{color:#181c20}
    .mb-notif-clear{background:#f1f4fa;border:none;border-radius:8px;padding:6px 12px;font-size:12px;font-weight:600;color:#006068;cursor:pointer;transition:all 0.15s}
    .mb-notif-clear:hover{background:#e0f2f3;color:#004d52}
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
  header.innerHTML = '<span class="mb-notif-header-title">🔔 Notifications</span><div class="mb-notif-header-actions"><button class="mb-notif-clear">Clear all</button><button class="mb-notif-close">×</button></div>';
  panel.appendChild(header);
  
  header.querySelector('.mb-notif-clear').addEventListener('click', clearAllNotifications);
  header.querySelector('.mb-notif-close').addEventListener('click', hideNotificationsPanel);
  
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
  
  // Re-attach event listeners after rebuilding
  const clearBtn = panel.querySelector('.mb-notif-clear');
  const closeBtn = panel.querySelector('.mb-notif-close');
  if (clearBtn) clearBtn.addEventListener('click', clearAllNotifications);
  if (closeBtn) closeBtn.addEventListener('click', hideNotificationsPanel);
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
