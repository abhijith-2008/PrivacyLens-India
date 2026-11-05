PrivacyLens India
A student project exploring how privacy-policy text can be made easier
to review.
Overview
PrivacyLens India is a proposed web application where a user can paste
the privacy policy of a website or application and receive three
separate outputs:
1. Extractive overview -- a short overview created by selecting
   informative sentences from the original policy.
2. Privacy-practice classification -- possible privacy-practice
   categories associated with policy passages, with supporting text
   where available.
3. DPDP topic checklist -- an informational check for wording
   related to selected topics from India's Digital Personal Data
   Protection (DPDP) framework.
The aim is to help users find relevant information and inspect the
original evidence more quickly. PrivacyLens is not a legal-compliance
checker and does not provide legal advice.
Problem
Privacy policies are often long and contain legal or technical language.
Details about data collection, use, sharing, retention, and user choices
can be difficult to locate. This project explores a way to organise
those details and point users towards relevant passages.
Planned Features
- Paste privacy-policy text into a simple interface.
- Generate a short extractive overview using sentences from the
  supplied text.
- Identify possible privacy-practice categories using a planned
  text-classification model.
- Display supporting policy excerpts where possible.
- Check selected DPDP-related topics separately using transparent
  text-matching rules.
- Handle empty input and common analysis errors clearly.
Proposed Technology
  Area                   Technology
  Programming language   Python
Web interface          Streamlit
Text processing        Python utilities and regular expressions
Machine learning       scikit-learn, TF-IDF, multi-label classification
Dataset preparation    pandas
Model persistence      joblib
Testing                Python unittest
Version control        Git and GitHub

The OPP-115 dataset is being considered for the privacy-practice
classification component. Its documentation and usage terms will be
reviewed before use or redistribution.
Planned Development Roadmap
1. Dataset inspection and preparation -- understand the data,
   labels, quality, and permitted use.
2. Basic text analysis and interface -- set up the application,
   validate input, and build the extractive overview.
3. Baseline classification -- train and evaluate an initial
   multi-label model.
4. DPDP checklist and testing -- add selected checklist rules, test
   the workflow, and document limitations.
The roadmap may be adjusted as the project develops.
Scope and Limitations
- The initial version will analyse text pasted by the user.
- Automatic website crawling is outside the initial scope.
- OPP-115 categories describe privacy practices; they are not DPDP
  legal-compliance labels.
- A detected phrase is not proof of compliance, and a missing match is
  not proof of non-compliance.
- Model predictions may be incomplete or incorrect. Evidence excerpts
  are included to support manual review.
- The application is an educational prototype, not a substitute for
  the original policy or professional legal advice.# PrivacyLens-India
