(function () {
  const apiHost = window.location.hostname || "127.0.0.1";
  const apiProtocol = window.location.protocol === "https:" ? "https:" : "http:";
  const localHosts = new Set(["localhost", "127.0.0.1", "::1"]);
  const isSeparateFrontendServer = window.location.port === "5713";
  const DEFAULT_API_BASE = isSeparateFrontendServer || localHosts.has(apiHost)
    ? `${apiProtocol}//${apiHost}:8000/api`
    : `${window.location.origin}/api`;

  function splitLine(line) {
    const delimiter = line.includes("\t") ? "\t" : ",";
    return line.split(delimiter).map((item) => item.trim());
  }

  function parseDelimited(text) {
    const lines = String(text || "")
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean);
    if (!lines.length) return [];

    const headers = splitLine(lines[0]).map((header, index) => header || `field_${index + 1}`);
    return lines.slice(1).map((line) => {
      const cells = splitLine(line);
      return headers.reduce((row, header, index) => {
        const raw = cells[index] || "";
        const numeric = Number(raw);
        row[header] = raw !== "" && Number.isFinite(numeric) ? numeric : raw;
        return row;
      }, {});
    });
  }

  function readFileAsText(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result || "");
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }

  function fileToPreview(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  const SAMPLE_PATIENTS = [
    {
      id: "cardiac-01",
      disease: "Cardiovascular disease",
      accent: "#0f766e",
      ehr: { age: 63, gender: "Male", bloodPressure: "152/94", sugarLevel: 145, heartRate: 98, medicalHistory: "Hypertension, chest pain, family history of heart disease" },
      genes: [["LDLR", "rs688", 0.78], ["APOE4", "rs429358", 0.71], ["MTHFR", "C677T", 0.52]],
      wearable: { baseHr: 88, stress: 20, steps: 3100, spo2: 96.2, sleep: 5.1 },
      findings: "Mild cardiomegaly with vascular congestion.",
      reportText: "LDL elevated, borderline glucose, abnormal cardiac enzyme trend.",
    },
    {
      id: "diabetes-02",
      disease: "Type 2 diabetes / metabolic disorder",
      accent: "#dc6b3d",
      ehr: { age: 54, gender: "Female", bloodPressure: "136/86", sugarLevel: 222, heartRate: 84, medicalHistory: "Diabetes, obesity, fatigue, increased thirst" },
      genes: [["MTHFR", "C677T", 0.64], ["TCF7L2", "rs7903146", 0.74], ["LDLR", "rs688", 0.44]],
      wearable: { baseHr: 82, stress: 12, steps: 2400, spo2: 97.4, sleep: 5.8 },
      findings: "No acute chest opacity. Report mentions elevated glucose.",
      reportText: "Fasting glucose high, HbA1c high, triglycerides abnormal.",
    },
    {
      id: "neuro-03",
      disease: "Neurological event risk",
      accent: "#2563eb",
      ehr: { age: 70, gender: "Male", bloodPressure: "148/90", sugarLevel: 126, heartRate: 91, medicalHistory: "Previous transient ischemia, memory issues, dizziness" },
      genes: [["APOE4", "rs429358", 0.86], ["MTHFR", "C677T", 0.61], ["JAK2", "V617F", 0.37]],
      wearable: { baseHr: 86, stress: 15, steps: 2800, spo2: 96.8, sleep: 4.9 },
      findings: "Report notes possible ischemia, no large lesion.",
      reportText: "Inflammatory markers mildly elevated, coagulation profile borderline.",
    },
    {
      id: "resp-04",
      disease: "Respiratory / pulmonary infection",
      accent: "#0891b2",
      ehr: { age: 47, gender: "Female", bloodPressure: "124/80", sugarLevel: 108, heartRate: 103, medicalHistory: "Asthma, cough, shortness of breath, fever" },
      genes: [["CFTR", "F508del", 0.46], ["HBB", "rs334", 0.28], ["EGFR", "rs2227983", 0.31]],
      wearable: { baseHr: 94, stress: 18, steps: 1900, spo2: 93.8, sleep: 4.3 },
      findings: "Lower-zone infiltrate and opacity suggest infection.",
      reportText: "WBC count elevated, CRP elevated, oxygen saturation low.",
    },
    {
      id: "renal-05",
      disease: "Kidney / renal complication",
      accent: "#7c3aed",
      ehr: { age: 59, gender: "Male", bloodPressure: "158/96", sugarLevel: 178, heartRate: 86, medicalHistory: "Chronic kidney disease, diabetes, hypertension, creatinine elevated" },
      genes: [["APOL1", "G1", 0.69], ["MTHFR", "C677T", 0.55], ["LDLR", "rs688", 0.41]],
      wearable: { baseHr: 84, stress: 10, steps: 2200, spo2: 96.9, sleep: 5.0 },
      findings: "No focal chest lesion. Report highlights renal panel abnormality.",
      reportText: "Creatinine high, urea high, eGFR reduced, glucose abnormal.",
    },
    {
      id: "oncology-06",
      disease: "Cancer / abnormal lesion risk",
      accent: "#be123c",
      ehr: { age: 66, gender: "Female", bloodPressure: "132/82", sugarLevel: 118, heartRate: 88, medicalHistory: "Unexplained weight loss, prior cancer screening abnormality" },
      genes: [["BRCA1", "185delAG", 0.81], ["TP53", "rs1042522", 0.73], ["EGFR", "L858R", 0.59]],
      wearable: { baseHr: 80, stress: 9, steps: 3300, spo2: 96.6, sleep: 5.6 },
      findings: "Small nodule and suspicious lesion noted in scan report.",
      reportText: "Anemia present, inflammatory markers abnormal.",
    },
    {
      id: "healthy-07",
      disease: "Low general disease risk",
      accent: "#16a34a",
      ehr: { age: 31, gender: "Female", bloodPressure: "112/72", sugarLevel: 92, heartRate: 68, medicalHistory: "No major medical history, active lifestyle" },
      genes: [["HBB", "rs334", 0.12], ["CFTR", "rs113993960", 0.1], ["LDLR", "rs688", 0.18]],
      wearable: { baseHr: 66, stress: 4, steps: 9800, spo2: 98.5, sleep: 7.6 },
      findings: "Normal scan appearance with no abnormal opacity.",
      reportText: "CBC, lipid panel, and glucose values within normal range.",
    },
    {
      id: "cardio-metabolic-08",
      disease: "Cardiometabolic syndrome",
      accent: "#b7791f",
      ehr: { age: 49, gender: "Male", bloodPressure: "144/91", sugarLevel: 184, heartRate: 89, medicalHistory: "Hypertension, prediabetes, smoking, high cholesterol" },
      genes: [["LDLR", "rs688", 0.76], ["TCF7L2", "rs7903146", 0.62], ["MTHFR", "C677T", 0.51]],
      wearable: { baseHr: 84, stress: 14, steps: 2600, spo2: 96.1, sleep: 5.4 },
      findings: "Mild vascular congestion, no focal mass.",
      reportText: "LDL high, glucose high, triglycerides high.",
    },
    {
      id: "neuro-cardio-09",
      disease: "Stroke and cardiac event risk",
      accent: "#1d4ed8",
      ehr: { age: 74, gender: "Female", bloodPressure: "166/98", sugarLevel: 139, heartRate: 101, medicalHistory: "Stroke history, atrial fibrillation, hypertension" },
      genes: [["APOE4", "rs429358", 0.79], ["JAK2", "V617F", 0.48], ["LDLR", "rs688", 0.63]],
      wearable: { baseHr: 92, stress: 22, steps: 1700, spo2: 95.7, sleep: 4.8 },
      findings: "Possible ischemia. Cardiomegaly also noted.",
      reportText: "Coagulation profile abnormal, BNP elevated.",
    },
    {
      id: "pulmonary-edema-10",
      disease: "Pulmonary edema / respiratory stress",
      accent: "#0e7490",
      ehr: { age: 61, gender: "Male", bloodPressure: "150/92", sugarLevel: 134, heartRate: 108, medicalHistory: "Breathlessness, cardiac history, overnight oxygen drop" },
      genes: [["LDLR", "rs688", 0.57], ["MTHFR", "C677T", 0.43], ["HBB", "rs334", 0.25]],
      wearable: { baseHr: 96, stress: 24, steps: 2100, spo2: 92.9, sleep: 4.1 },
      findings: "Bilateral edema and vascular opacity observed.",
      reportText: "Oxygen saturation low, BNP elevated, inflammatory values abnormal.",
    },
    {
      id: "anemia-11",
      disease: "Blood disorder / anemia risk",
      accent: "#9333ea",
      ehr: { age: 38, gender: "Female", bloodPressure: "118/76", sugarLevel: 96, heartRate: 99, medicalHistory: "Fatigue, dizziness, low hemoglobin noted previously" },
      genes: [["HBB", "rs334", 0.72], ["MTHFR", "C677T", 0.38], ["TP53", "rs1042522", 0.22]],
      wearable: { baseHr: 90, stress: 10, steps: 4300, spo2: 97.8, sleep: 6.2 },
      findings: "Normal chest image, blood report abnormal.",
      reportText: "Hemoglobin low, ferritin low, RBC indices abnormal.",
    },
    {
      id: "infection-12",
      disease: "Systemic infection / inflammatory risk",
      accent: "#ea580c",
      ehr: { age: 44, gender: "Male", bloodPressure: "128/84", sugarLevel: 116, heartRate: 112, medicalHistory: "Fever, infection symptoms, weakness, cough" },
      genes: [["CFTR", "F508del", 0.35], ["EGFR", "rs2227983", 0.29], ["JAK2", "V617F", 0.33]],
      wearable: { baseHr: 102, stress: 18, steps: 1500, spo2: 94.6, sleep: 3.9 },
      findings: "Patchy opacity with possible infection.",
      reportText: "WBC elevated, CRP elevated, neutrophil count abnormal.",
    },
  ];

  let lastSampleIndex = -1;

  function escapeSvgText(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function samplePreview(title, subtitle, accent) {
    const svg = `
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 420">
        <rect width="640" height="420" fill="#f8fafc"/>
        <rect x="34" y="34" width="572" height="352" rx="18" fill="#ffffff" stroke="#d8e1ea" stroke-width="3"/>
        <circle cx="232" cy="205" r="112" fill="${accent}" opacity="0.16"/>
        <circle cx="366" cy="182" r="84" fill="${accent}" opacity="0.24"/>
        <path d="M172 265 C230 185, 287 286, 350 205 S470 158, 506 244" fill="none" stroke="${accent}" stroke-width="18" stroke-linecap="round" opacity="0.45"/>
        <text x="58" y="86" fill="#14213d" font-family="Arial" font-size="30" font-weight="700">${escapeSvgText(title)}</text>
        <text x="58" y="128" fill="#64748b" font-family="Arial" font-size="22">${escapeSvgText(subtitle)}</text>
        <text x="58" y="354" fill="${accent}" font-family="Arial" font-size="20" font-weight="700">Generated sample preview</text>
      </svg>
    `;
    return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
  }

  function buildGenomicsRows(patient, offset) {
    return patient.genes.map(([gene, variant, riskScore], index) => ({
      gene,
      variant,
      risk_score: Number(Math.min(0.95, riskScore + ((offset + index) % 3) * 0.015).toFixed(2)),
      note: `${patient.disease} marker`,
    }));
  }

  function buildWearableRows(profile, offset) {
    const rows = [];
    for (let index = 0; index < 48; index += 1) {
      const hour = String(Math.floor(index / 2)).padStart(2, "0");
      const minute = index % 2 === 0 ? "00" : "30";
      const activityWave = Math.sin((index + offset) / 4);
      const stressBump = index > 20 && index < 34 ? profile.stress : profile.stress * 0.2;
      const heartRate = Math.round(profile.baseHr + activityWave * 6 + stressBump + (index % 4));
      const steps = Math.max(0, Math.round(profile.steps * (index + 1) / 48 + Math.sin(index / 3) * 95));
      const spo2 = Math.round((profile.spo2 - (stressBump > 10 ? 1.2 : 0) + Math.sin(index / 5) * 0.4) * 10) / 10;
      const sleep = index < 14 ? Math.round((profile.sleep / 14) * 10) / 10 : 0;
      rows.push({ time: `${hour}:${minute}`, heart_rate: heartRate, steps, spo2, sleep });
    }
    return rows;
  }

  function buildSamplePatient(patient, index) {
    const patientNo = String(index + 1).padStart(2, "0");
    return {
      id: patient.id,
      disease: patient.disease,
      ehr: { ...patient.ehr },
      genomics: {
        source: `sample patient ${patientNo} genomics`,
        rows: buildGenomicsRows(patient, index),
      },
      wearable: {
        source: `sample patient ${patientNo} wearable simulation`,
        simulated: true,
        rows: buildWearableRows(patient.wearable, index),
      },
      medicalImage: {
        hasImage: true,
        name: `${patient.id}_scan.svg`,
        type: "image/svg+xml",
        size: 180000 + index * 7311,
        findings: patient.findings,
        previewUrl: samplePreview("X-ray / scan preview", patient.disease, patient.accent),
      },
      reportImage: {
        hasImage: true,
        name: `${patient.id}_blood_report.svg`,
        type: "image/svg+xml",
        size: 94000 + index * 5103,
        reportText: patient.reportText,
        previewUrl: samplePreview("Blood report preview", patient.reportText.slice(0, 54), patient.accent),
      },
    };
  }

  function randomSamplePatient() {
    let index = Math.floor(Math.random() * SAMPLE_PATIENTS.length);
    if (SAMPLE_PATIENTS.length > 1 && index === lastSampleIndex) {
      index = (index + 1) % SAMPLE_PATIENTS.length;
    }
    lastSampleIndex = index;
    return buildSamplePatient(SAMPLE_PATIENTS[index], index);
  }

  function sampleGenomicsRows() {
    return randomSamplePatient().genomics.rows;
  }

  function simulateWearableRows() {
    const rows = [];
    for (let index = 0; index < 48; index += 1) {
      const hour = String(Math.floor(index / 2)).padStart(2, "0");
      const minute = index % 2 === 0 ? "00" : "30";
      const activityWave = Math.sin(index / 4);
      const stressBump = index > 22 && index < 34 ? 18 : 0;
      const heartRate = Math.round(74 + activityWave * 8 + stressBump + (index % 5));
      const steps = Math.max(0, Math.round(80 + index * 55 + Math.sin(index / 3) * 140));
      const spo2 = Math.round((97 - (stressBump ? 1.8 : 0) + Math.sin(index / 5) * 0.7) * 10) / 10;
      const sleep = index < 13 ? 0.5 : 0;
      rows.push({ time: `${hour}:${minute}`, heart_rate: heartRate, steps, spo2, sleep });
    }
    return rows;
  }

  function toPercent(value) {
    return `${Math.round((Number(value) || 0) * 100)}%`;
  }

  window.AppUtils = {
    DEFAULT_API_BASE,
    parseDelimited,
    readFileAsText,
    fileToPreview,
    randomSamplePatient,
    sampleGenomicsRows,
    simulateWearableRows,
    toPercent,
  };
})();
