# PrivacyLens India
### AI-Powered Privacy Policy Analysis — Installation & User Guide

## 1. Project Overview

PrivacyLens India is a Chrome extension supported by a Python-based AI backend. It helps users understand website privacy policies through automated text analysis, privacy-practice classification and evidence-based explanations.

### Key Features

- Automatic detection of likely privacy-policy links.
- User-controlled policy extraction.
- AI-powered privacy-practice classification using the OPP-115-based model.
- Privacy Nutrition Label.
- Evidence Explorer for reviewing relevant policy statements.
- Informational DPDP awareness checklist (experimental).

**Important:** PrivacyLens provides informational analysis, not legal advice or a determination of DPDP Act compliance.

---

## 2. System Requirements

| Component | Requirement |
|---|---|
| Operating system | Windows 10/11 |
| Browser | Google Chrome |
| Python | Compatible Python installation |
| Git | For cloning the repository |
| Internet | Required to access websites and install dependencies |
| Backend | FastAPI + Uvicorn |
| ML model | `privacylens_model.joblib` |

---

## 3. Download the Project

Open PowerShell or Command Prompt.

Clone the repository:

```bash
git clone https://github.com/abhijith-2008/PrivacyLens-India.git
```

Navigate into the downloaded project:

```bash
cd PrivacyLens-India
```

Make sure the repository contains:

```text
PrivacyLens-India/
│
├── api.py
├── app.py
├── analyzer.py
├── report.py
├── dpdp_checklist.py
├── requirements.txt
├── privacylens_model.joblib
│
└── chrome-extension/
    ├── manifest.json
    ├── background.js
    ├── content.js
    ├── popup.html
    ├── popup.css
    ├── popup.js
    ├── welcome.html
    ├── welcome.css
    ├── welcome.js
    └── workspace.css
```

The model artifact must also be present in the repository or supplied separately.

---

## 4. Backend Installation

### Step 1: Create a virtual environment

```bash
python -m venv venv
```

### Step 2: Activate the environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use Command Prompt:

```cmd
venv\Scripts\activate.bat
```

### Step 3: Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install Uvicorn if it is not already included:

```bash
python -m pip install "uvicorn[standard]"
```

### Step 4: Start the FastAPI backend

From the project root:

```bash
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Keep this terminal running while using the extension.

### Step 5: Verify the backend

Open:

http://127.0.0.1:8000/health

The backend should return a successful health response.

You can also inspect the API documentation at:

http://127.0.0.1:8000/docs

---

## 5. Chrome Extension Installation

### Step 1: Open Chrome Extensions

Enter this address in Chrome:

```text
chrome://extensions
```

### Step 2: Enable Developer Mode

Turn on **Developer mode** in the upper-right corner.

### Step 3: Load the extension

1. Click **Load unpacked**.
2. Navigate to the downloaded project directory.
3. Select the `chrome-extension` folder.
4. Click **Select Folder**.

PrivacyLens India should now appear in your installed extensions.

### Step 4: Pin the extension

1. Open Chrome's Extensions menu.
2. Find PrivacyLens India.
3. Click the pin icon.

---

## 6. How to Use PrivacyLens India

### Step 1: Start the backend

Ensure the FastAPI server is running at:

```text
http://127.0.0.1:8000
```

### Step 2: Visit a website

Open a website whose privacy policy you want to examine.

For example:
- Crunchyroll
- Zomato
- Other websites with accessible privacy policies.

### Step 3: Detect the privacy policy

PrivacyLens checks the page for likely privacy-policy links and displays an in-page notification when one is detected.

### Step 4: Launch the analysis workspace

Click **Analyse Policy** in the notification.

### Step 5: Extract the policy

In the PrivacyLens workspace, use the extraction control to retrieve the privacy-policy text.

Review the extracted text before proceeding.

### Step 6: Run AI analysis

Click **Analyse with PrivacyLens AI**.

The backend processes the supplied policy text and generates the analysis results.

### Step 7: Explore the results

Review the available sections:

- Privacy Nutrition Label
- AI Privacy Findings
- Evidence Explorer
- DPDP Awareness Checklist, if enabled

### Step 8: Make your own decision

Review the evidence and decide whether you want to continue to the website or return to the previous page.

PrivacyLens does not automatically accept or reject website consent requests.

---

## 7. Technology Stack

| Layer | Technology |
|---|---|
| Browser extension | JavaScript, HTML, CSS |
| Extension architecture | Chrome Manifest V3 |
| Backend API | Python, FastAPI |
| ASGI server | Uvicorn |
| Machine learning | Scikit-learn |
| Feature extraction | Existing trained feature pipeline |
| Model persistence | Joblib |
| Privacy classification | OPP-115-based classification |

---

## 8. Troubleshooting

### Backend is not starting

Try:

```bash
python -m pip install -r requirements.txt
python -m pip install "uvicorn[standard]"
```

Then restart Uvicorn.

### Extension cannot connect to backend

1. Check whether Uvicorn is running.
2. Open `http://127.0.0.1:8000/health`.
3. Confirm the backend URL configured in the extension is correct.
4. Check the FastAPI terminal for errors.

### Extension does not detect a policy

- Wait for the website to finish loading.
- Check whether the website has an accessible privacy-policy link.
- Try another website.
- Reload the extension from `chrome://extensions`.

### Extension files were modified

After modifying extension files:

1. Open `chrome://extensions`.
2. Click Reload on PrivacyLens India.
3. Refresh the website being tested.

### Model artifact is missing

Ensure that:

```text
privacylens_model.joblib
```

exists in the project root.

The model must be supplied separately if it is not included in the repository.

---

## 9. Privacy and Limitations

- Automatic detection is performed locally by the browser extension.
- Policy extraction and AI analysis are initiated by explicit user actions.
- The local development backend processes the submitted policy text.
- OPP-115 classifications are not calibrated legal-risk probabilities.
- Policy statements do not independently establish an organisation's actual practices.
- The application does not replace professional legal advice.

---

## 10. Conclusion

PrivacyLens India aims to make complex privacy policies easier to understand by combining browser-based policy detection, machine-learning classification and evidence-based explanations.

It supports informed decision-making by helping users examine what an organisation says about collecting, using, sharing and retaining personal information.

**PrivacyLens India — Understand Before You Agree.**
