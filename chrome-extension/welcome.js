
// ==========================================
// PRIVACYLENS INDIA — ANALYSIS WORKSPACE
// ==========================================

// Website and policy elements
const websiteName = document.getElementById("websiteName");
const websiteUrl = document.getElementById("websiteUrl");
const policyInfo = document.getElementById("policyInfo");
const policyUrl = document.getElementById("policyUrl");
const policyLink = document.getElementById("policyLink");

// Status
const statusText = document.getElementById("statusText");
const statusIndicator = document.getElementById("statusIndicator");

// Extraction
const extractBtn = document.getElementById("extractBtn");
const extractedSection = document.getElementById("extractedSection");
const extractedText = document.getElementById("extractedText");
const extractedLength = document.getElementById("extractedLength");
const runAnalysisBtn = document.getElementById("runAnalysisBtn");

// Analysis results
const results = document.getElementById("results");
const summaryContent = document.getElementById("summaryContent");
const findingsContent = document.getElementById("findingsContent");
const checklistContent = document.getElementById("checklistContent");

// Nutrition Label
const nutritionLabel = document.getElementById("nutritionLabel");
const labelWebsiteName = document.getElementById("labelWebsiteName");
const policyUpdated = document.getElementById("policyUpdated");
const nutritionItems = document.getElementById("nutritionItems");
const importantConsiderations = document.getElementById("importantConsiderations");

// Navigation
const continueBtn = document.getElementById("continueBtn");
const reviewDetailsBtn = document.getElementById("reviewDetailsBtn");
const goBackBtn = document.getElementById("goBackBtn");

// Privacy concern selection
const concernCheckboxes = document.querySelectorAll(
    '.concern-option input[type="checkbox"]'
);
// ==========================================
// PRIVACY EMAIL COMPOSER ELEMENTS
// ==========================================

const concernEmailBtn = document.getElementById("concernEmailBtn");

const grievancePreview = document.getElementById("grievancePreview");

const emailDraftStatus = document.getElementById("emailDraftStatus");

const grievanceRecipient = document.getElementById("grievanceRecipient");

const grievanceContactStatus = document.getElementById("grievanceContactStatus");

const emailSubject = document.getElementById("emailSubject");

const emailMessage = document.getElementById("emailMessage");

const openGmailBtn = document.getElementById("openGmailBtn");


// ==========================================
// WORKSPACE STATE
// ==========================================

let detectedData = null;
let welcomeTabId = null;
let originTabId = null;
let policyTabId = null;

let currentPolicyText = "";
// ==========================================
// PRIVACY CONCERN INTEGRATION STATE
// ==========================================

let latestAnalysisData = null;
let latestQwenData = null;
let privacyConcernContext = null;

// Map user concerns to existing OPP-115 categories.




// Match selected concerns with available analysis evidence.

// ==========================================
// GET SELECTED PRIVACY CONCERNS
// ==========================================

function getSelectedPrivacyConcerns() {

    return Array.from(concernCheckboxes)
        .filter(checkbox => checkbox.checked)
        .map(checkbox => checkbox.value);

}
// ==========================================
// QWEN PRIVACY CONCERN MAPPING
// ==========================================

function preparePrivacyConcernContext() {

    const selectedConcerns = getSelectedPrivacyConcerns();

    const qwenFindings =
        latestQwenData?.findings || [];

    const matchedConcerns = selectedConcerns.map(concern => {

        const finding = qwenFindings.find(
            item => item.area === concern
        );

        return {
            concern: concern,

            status: finding?.status || "not_identified",

            explanation: finding?.explanation || "",

            evidence: finding?.evidence || []

        };

    });

    privacyConcernContext = {

        website: websiteName.textContent,

        policyUrl: detectedData?.policy?.url || "",

        selectedConcerns: selectedConcerns,

        matchedConcerns: matchedConcerns,

        grievanceContact:
            latestQwenData?.grievance_contact || null

    };

    return privacyConcernContext;

}


// ==========================================
// STATUS
// ==========================================

function updateStatus(message, color = "#22c55e") {

    statusText.textContent = message;
    statusIndicator.style.background = color;

}


// ==========================================
// LOAD WORKSPACE INFORMATION
// ==========================================

async function initializeWorkspace() {

    try {

        const currentTab = await chrome.tabs.getCurrent();

        if (currentTab?.id === undefined) {
            throw new Error("Unable to identify workspace tab.");
        }

        welcomeTabId = currentTab.id;

        const welcomeKey = `privacyLensWelcome_${welcomeTabId}`;

        const saved = await chrome.storage.local.get(welcomeKey);

        detectedData = saved[welcomeKey];

        // Load previously saved workspace information if available.
        const workspaceKey = `privacyLensWorkspace_${welcomeTabId}`;

        const workspaceSaved = await chrome.storage.local.get(workspaceKey);

        const workspaceData = workspaceSaved[workspaceKey];

        if (!detectedData && !workspaceData) {
            throw new Error("Policy information not found. Please detect it again.");
        }

        if (detectedData) {
            originTabId = detectedData.originTabId;
        }

        if (workspaceData) {
            originTabId = workspaceData.originTabId;
            policyTabId = workspaceData.policyTabId;
        }

        const pageUrl = detectedData?.pageUrl;

        if (!pageUrl) {
            throw new Error("Original website information is unavailable.");
        }

        const origin = new URL(pageUrl);

        websiteName.textContent = origin.hostname;
        const sidebarWebsiteName =
            document.getElementById("sidebarWebsiteName");

        if (sidebarWebsiteName) {
            sidebarWebsiteName.textContent = origin.hostname;
        }
        websiteUrl.textContent = pageUrl;

        const policy = detectedData.policy;

        policyUrl.textContent = policy.url;

        policyLink.href = policy.url;

        policyLink.textContent = "View detected policy ↗";

        policyInfo.classList.remove("hidden");

        extractBtn.disabled = false;

        updateStatus("Privacy policy detected. Ready to extract.");

    } catch (error) {

        console.error("Workspace initialization error:", error);

        updateStatus(error.message, "#ef4444");

    }

}


// ==========================================
// EXTRACT POLICY TEXT
// ==========================================

extractBtn.addEventListener("click", async () => {

    if (!detectedData?.policy?.url) {
        updateStatus("Policy information unavailable.", "#ef4444");
        return;
    }

    extractBtn.disabled = true;

    updateStatus("Opening privacy policy...", "#f59e0b");

    try {

        // Reuse an existing policy tab if one is already open.
        if (policyTabId !== null) {

            try {
                await chrome.tabs.get(policyTabId);
            } catch {
                policyTabId = null;
            }

        }

        // Open the policy in the background if necessary.
        if (policyTabId === null) {

            const response = await chrome.runtime.sendMessage({

                type: "OPEN_POLICY_TAB",

                policyUrl: detectedData.policy.url,

                originTabId: originTabId

            });

            if (!response?.success) {
                throw new Error(
                    response?.error || "Unable to open privacy policy."
                );
            }

            policyTabId = response.policyTabId;

        }

        updateStatus("Extracting policy text...", "#f59e0b");

        // Extract text from the actual policy tab.
        const response = await chrome.scripting.executeScript({

            target: {
                tabId: policyTabId
            },

            func: () => {

                const selectors = [
                    "main",
                    "article",
                    '[role="main"]',
                    ".privacy-policy",
                    "#privacy-policy",
                    ".policy-content",
                    "#content"
                ];

                const candidates = selectors.flatMap(selector =>
                    Array.from(document.querySelectorAll(selector))
                );

                let bestRoot = null;
                let bestScore = 0;

                candidates.forEach(element => {

                    const text = element.innerText || "";
                    const lower = text.toLowerCase();

                    if (text.length < 300) return;

                    let score = Math.min(text.length, 30000);

                    if (lower.includes("privacy policy")) score += 5000;
                    if (lower.includes("personal information")) score += 1000;
                    if (lower.includes("data collection")) score += 1000;
                    if (lower.includes("data retention")) score += 1000;

                    if (score > bestScore) {
                        bestScore = score;
                        bestRoot = element;
                    }

                });

                const root = (bestRoot || document.body).cloneNode(true);

                root.querySelectorAll(`
                    script,
                    style,
                    noscript,
                    svg,
                    iframe,
                    nav,
                    footer,
                    aside,
                    button,
                    input,
                    select,
                    textarea,
                    form,
                    [role="navigation"],
                    [aria-hidden="true"]
                `).forEach(element => element.remove());

                let text = root.innerText || root.textContent || "";

                text = text
                    .replace(/\r/g, "")
                    .replace(/[ \t]+/g, " ")
                    .replace(/\n[ \t]*\n[ \t]*\n/g, "\n\n")
                    .trim();

                const unwantedLines = [
                    "skip to main content",
                    "back to top",
                    "home",
                    "menu"
                ];

                text = text
                    .split("\n")
                    .filter(line =>
                        !unwantedLines.includes(line.trim().toLowerCase())
                    )
                    .join("\n")
                    .trim();

                return {
                    url: location.href,
                    title: document.title,
                    text
                };

            }

        });

        const page = response[0]?.result;

        if (!page || !page.text || page.text.trim().length < 50) {
            throw new Error("Not enough readable policy text found.");
        }

        currentPolicyText = page.text.trim();

        extractedText.textContent = currentPolicyText;

        extractedLength.textContent =
            `${currentPolicyText.length.toLocaleString()} characters extracted`;

        extractedSection.classList.remove("hidden");

        extractBtn.textContent = "Policy Extracted ✓";

        updateStatus("Policy text extracted successfully!");

    } catch (error) {

        console.error("Policy extraction error:", error);

        updateStatus(
            error.message || "Policy extraction failed.",
            "#ef4444"
        );

    } finally {

        extractBtn.disabled = false;

    }

});


// ==========================================
// PRIVACY NUTRITION LABEL
// ==========================================

function renderNutritionLabel(data) {

    const categories = data.privacy_findings?.categories || [];

    nutritionItems.replaceChildren();
    importantConsiderations.replaceChildren();

    labelWebsiteName.textContent =
        websiteName.textContent || "Current website";

    const dateMatch = currentPolicyText.match(
        /last updated(?:\s+on)?\s*:?\s*([^\n]+)/i
    );

    policyUpdated.textContent = dateMatch
        ? `Policy ${dateMatch[0].trim()}`
        : "Policy update date not identified.";

    const categoryMap = {

        "First Party Collection/Use":
            "Personal information collection",

        "Third Party Sharing/Collection":
            "Third-party sharing",

        "User Choice/Control":
            "Your available choices",

        "Data Retention":
            "Data retention",

        "Data Security":
            "Security safeguards",

        "User Access, Edit and Deletion":
            "Access and deletion rights",

        "Policy Change":
            "Policy updates",

        "International and Specific Audiences":
            "Specific audiences",

        "Other":
            "Other privacy practices"

    };


    // Display identified privacy topics.

    if (categories.length === 0) {

        nutritionItems.textContent =
            "No privacy topics were identified.";

    } else {

        categories.forEach(finding => {

            const item = document.createElement("div");
            item.className = "nutrition-item";

            const name = document.createElement("span");
            name.className = "nutrition-item-name";

            name.textContent =
                categoryMap[finding.category] || finding.category;

            const status = document.createElement("span");
            status.className = "nutrition-status";
            status.textContent = "Discussed";

            item.append(name, status);

            nutritionItems.appendChild(item);

        });

    }


    // Important considerations.

    const priorityCategories = [

        "First Party Collection/Use",
        "Third Party Sharing/Collection",
        "User Choice/Control",
        "Data Retention",
        "User Access, Edit and Deletion"

    ];

    const descriptions = {

        "First Party Collection/Use":
            "The policy describes collecting and using personal information for services, personalisation and other purposes.",

        "Third Party Sharing/Collection":
            "The policy describes sharing information with external organisations or service providers.",

        "User Choice/Control":
            "The policy describes choices such as managing communication preferences and opting out of some messages.",

        "Data Retention":
            "The policy describes retaining some information for stated purposes, legal obligations or business needs.",

        "User Access, Edit and Deletion":
            "The policy describes ways to review, correct or delete information, subject to stated conditions."

    };

    const priorityFindings = categories.filter(finding =>
        priorityCategories.includes(finding.category)
    );

    if (priorityFindings.length === 0) {

        importantConsiderations.textContent =
            "No priority considerations were identified.";

    } else {

        priorityFindings.forEach(finding => {

            const card = document.createElement("div");
            card.className = "consideration";

            const title = document.createElement("strong");

            title.textContent =
                categoryMap[finding.category] || finding.category;

            const description = document.createElement("p");

            description.textContent =
                descriptions[finding.category] ||
                finding.plain_english ||
                "This topic appears in the supplied policy.";

            card.append(title, description);

            const evidence = finding.evidence?.[0]?.excerpt;

            if (evidence) {

                const evidenceText = document.createElement("p");

                evidenceText.textContent =
                    `Policy evidence: ${evidence.slice(0, 220)}${evidence.length > 220 ? "…" : ""}`;

                evidenceText.style.color = "#94a3b8";
                evidenceText.style.fontSize = "10px";

                card.appendChild(evidenceText);

            }

            importantConsiderations.appendChild(card);

        });

    }

    nutritionLabel.classList.remove("hidden");

}


// ==========================================
// EVIDENCE HIGHLIGHTING
// ==========================================

function highlightEvidence(excerpt) {

    if (!currentPolicyText || !excerpt) {

        updateStatus("Policy text or evidence unavailable.", "#ef4444");

        return;

    }

    const policyText = currentPolicyText;

    let matchIndex = policyText.indexOf(excerpt);

    let matchedLength = excerpt.length;

    if (matchIndex === -1) {

        const searchText = excerpt.slice(0, 100);

        matchIndex = policyText.indexOf(searchText);

        matchedLength = searchText.length;

    }

    if (matchIndex === -1) {

        updateStatus(
            "Exact evidence match not found in extracted policy.",
            "#f59e0b"
        );

        return;

    }

    extractedText.replaceChildren();

    const before = policyText.slice(0, matchIndex);

    const matched = policyText.slice(
        matchIndex,
        matchIndex + matchedLength
    );

    const after = policyText.slice(matchIndex + matchedLength);

    extractedText.appendChild(
        document.createTextNode(before)
    );

    const highlight = document.createElement("mark");

    highlight.className = "evidence-highlight";
    highlight.textContent = matched;

    extractedText.appendChild(highlight);

    extractedText.appendChild(
        document.createTextNode(after)
    );

    extractedSection.classList.remove("hidden");

    extractedSection.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    setTimeout(() => {

        highlight.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    }, 250);

    updateStatus("Supporting evidence highlighted!");

}


// ==========================================
// ANALYSE WITH PRIVACYLENS AI
// ==========================================

runAnalysisBtn.addEventListener("click", async () => {

    if (!currentPolicyText || currentPolicyText.length < 50) {

        updateStatus(
            "Please extract a valid policy first.",
            "#ef4444"
        );

        return;

    }

    runAnalysisBtn.disabled = true;
    runAnalysisBtn.textContent = "Analysing...";

    updateStatus("Sending policy to PrivacyLens AI...", "#f59e0b");

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/analyze",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },

                body: JSON.stringify({
                    policy_text: currentPolicyText
                })
            }
        );

        const data = await response.json();
        // Save analysis results for future privacy concern integration.
        latestAnalysisData = data;

        if (!response.ok) {

            throw new Error(
                data.detail || "Backend analysis failed."
            );

        }


        // POLICY SUMMARY

        summaryContent.replaceChildren();

        if (data.summary?.sentences?.length) {

            const summaryList = document.createElement("ul");

            data.summary.sentences.forEach(sentence => {

                const item = document.createElement("li");

                item.textContent = sentence;

                summaryList.appendChild(item);

            });

            summaryContent.appendChild(summaryList);

        } else {

            summaryContent.textContent = "No summary available.";

        }


        // OPP-115 FINDINGS

        findingsContent.replaceChildren();

        const findings = data.privacy_findings?.categories || [];

        if (findings.length === 0) {

            findingsContent.textContent = "No categories detected.";

        }

        findings.forEach(finding => {

            const card = document.createElement("div");

            card.style.marginBottom = "12px";

            const title = document.createElement("strong");

            title.textContent = finding.category;

            const description = document.createElement("p");

            description.textContent = finding.plain_english || "";

            const score = document.createElement("p");

            score.textContent = `Model output: ${finding.max_score}`;

            card.append(title, description, score);


            (finding.evidence || []).forEach(evidence => {

                const evidenceButton = document.createElement("button");

                evidenceButton.className = "evidence-link";

                evidenceButton.type = "button";

                evidenceButton.textContent =
                    `🔎 View evidence: ${evidence.excerpt}`;

                evidenceButton.addEventListener("click", () => {

                    highlightEvidence(evidence.excerpt);

                });

                card.appendChild(evidenceButton);

            });

            findingsContent.appendChild(card);

        });


        // DPDP AWARENESS CHECKLIST

        // DPDP CHECKLIST — WAITING FOR QWEN

        checklistContent.replaceChildren();

        checklistContent.textContent =
            "Generating AI-powered DPDP awareness checklist...";


        
// ==========================================
// NUTRITION LABEL
// ==========================================

renderNutritionLabel(data);


// ==========================================
// LOCAL QWEN ANALYSIS
// ==========================================

latestQwenData = null;

updateStatus(
    "Running detailed local AI privacy analysis...",
    "#f59e0b"
);

try {

    const qwenResponse = await fetch(
        "http://127.0.0.1:8000/analyze-privacy-details",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },

            body: JSON.stringify({
                policy_text: currentPolicyText
            })
        }
    );

    const qwenResult = await qwenResponse.json();

    if (!qwenResponse.ok) {

        throw new Error(
            qwenResult.detail || "Qwen analysis failed."
        );

    }

    latestQwenData = qwenResult.privacy_details;

    console.log(
        "PrivacyLens Qwen results:",
        latestQwenData
    );
        // ==========================================
    // QWEN-POWERED DPDP AWARENESS CHECKLIST
    // ==========================================

    checklistContent.replaceChildren();

    const dpdpChecklist = qwenResult.dpdp_checklist || [];

    if (dpdpChecklist.length === 0) {

        checklistContent.textContent =
            "No DPDP checklist results available.";

    } else {

        dpdpChecklist.forEach(item => {

            const card = document.createElement("div");

            card.style.marginBottom = "16px";
            card.className = "dpdp-checklist-card";

            // Title
            const title = document.createElement("strong");

            title.textContent = item.title;

            // Status
            const status = document.createElement("p");

            status.textContent =
                `Status: ${item.status.replaceAll("_", " ")}`;

            // Explanation
            const explanation = document.createElement("p");

            explanation.textContent =
                item.explanation || "No explanation provided.";

            // Legal reference
            const reference = document.createElement("p");

            reference.textContent =
                `Reference: ${item.reference}`;

            // Why it matters
            const why = document.createElement("p");

            why.textContent =
                item.why_it_matters || "";

            card.append(
                title,
                status,
                explanation,
                reference,
                why
            );

            // Evidence
            (item.evidence || []).forEach(excerpt => {

                const evidenceButton =
                    document.createElement("button");

                evidenceButton.type = "button";
                evidenceButton.className = "evidence-link";

                evidenceButton.textContent =
                    `🔎 View evidence: ${excerpt}`;

                evidenceButton.addEventListener("click", () => {

                    highlightEvidence(excerpt);

                });

                card.appendChild(evidenceButton);

            });

            // Manual review disclaimer
            if (item.manual_review_required) {

                const review = document.createElement("p");

                review.textContent =
                    "⚠ Manual review required. This is an informational finding, not a legal compliance verdict.";

                review.style.color = "#f59e0b";
                review.style.fontSize = "12px";

                card.appendChild(review);

            }

            checklistContent.appendChild(card);

        });

    }

    // Prepare selected concerns using Qwen evidence.
    preparePrivacyConcernContext();

    updateStatus(
        "OPP-115 and Qwen analysis completed!"
    );

} catch (qwenError) {

    console.error(
        "Qwen analysis error:",
        qwenError
    );

    updateStatus(
        "OPP-115 analysis completed, but Qwen analysis failed: " +
        qwenError.message,
        "#f59e0b"
    );

}


        // Keep detailed analysis as a secondary view.
        results.classList.add("hidden");

        nutritionLabel.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

        updateStatus("Privacy analysis completed!");

    } catch (error) {

        console.error("PrivacyLens API error:", error);

        updateStatus(
            error.message || "Unable to connect to the backend.",
            "#ef4444"
        );

    } finally {

        runAnalysisBtn.disabled = false;

        runAnalysisBtn.textContent =
            "Analyse with PrivacyLens AI";

    }

});


// ==========================================
// REVIEW DETAILS
// ==========================================

reviewDetailsBtn.addEventListener("click", () => {

    results.classList.remove("hidden");

    results.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

});


// ==========================================
// CONTINUE / GO BACK
// ==========================================

async function returnToOriginalWebsite(action) {

    try {

        if (policyTabId === null) {

            throw new Error("Policy tab information unavailable.");

        }

        const response = await chrome.runtime.sendMessage({

            type: "RETURN_TO_ORIGINAL",

            policyTabId: policyTabId,

            action: action

        });

        if (!response?.success) {

            throw new Error(
                response?.error || "Navigation failed."
            );

        }

        // Clean up workspace storage.
        await chrome.storage.local.remove([
            `privacyLensWelcome_${welcomeTabId}`,
            `privacyLensWorkspace_${welcomeTabId}`
        ]);

        // Close workspace after returning to the original website.
        await chrome.tabs.remove(welcomeTabId);

    } catch (error) {

        console.error("Navigation error:", error);

        updateStatus(
            error.message || "Navigation failed.",
            "#ef4444"
        );

    }

}


// Continue to original website.
continueBtn.addEventListener("click", async () => {

    await returnToOriginalWebsite("continue");

});


// Go back to original website history.
goBackBtn.addEventListener("click", async () => {

    await returnToOriginalWebsite("back");

});


// ==========================================
// GENERATE PRIVACY CONCERN EMAIL
// ==========================================

concernEmailBtn.addEventListener("click", async () => {

    if (!currentPolicyText || !latestQwenData) {

        updateStatus(
            "Please extract and analyse the policy first.",
            "#ef4444"
        );

        return;
    }

    const selectedConcerns = getSelectedPrivacyConcerns();

    if (selectedConcerns.length === 0) {

        updateStatus(
            "Please select at least one privacy concern.",
            "#ef4444"
        );

        return;
    }

    // Refresh context using the latest checkbox selections.
    const context = preparePrivacyConcernContext();

    concernEmailBtn.disabled = true;
    concernEmailBtn.textContent = "Generating email...";

    emailDraftStatus.textContent =
        "Qwen is preparing your privacy concern email. This may take a few minutes.";

    grievancePreview.classList.remove("hidden");

    grievancePreview.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    openGmailBtn.disabled = true;

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/generate-privacy-email",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },

                body: JSON.stringify({
                    context: context
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Email generation failed."
            );
        }

        const draft = data.email_draft;

        if (!draft?.subject || !draft?.body) {
            throw new Error("Incomplete email draft received.");
        }

        // Populate the editable email fields.
        emailSubject.value = draft.subject;
        emailMessage.value = draft.body;

        // Use only the contact already validated by the backend.
        const contact = latestQwenData.grievance_contact;

        if (
            contact?.status === "identified" &&
            contact?.email
        ) {

            grievanceRecipient.value = contact.email;

            grievanceContactStatus.textContent =
                `Policy identifies ${contact.designation || "a designated privacy contact"}. Please verify the address before sending.`;

        } else {

            grievanceRecipient.value = "";

            grievanceContactStatus.textContent =
                "No designated grievance email was identified in the policy. Please enter the recipient manually.";

        }

        emailDraftStatus.textContent =
            "Your email draft is ready. Review and edit it before opening Gmail.";

        updateStatus("Privacy concern email generated successfully!");

        openGmailBtn.disabled = !isValidRecipient(
            grievanceRecipient.value
        );

    } catch (error) {

        console.error("Email generation error:", error);

        emailDraftStatus.textContent =
            "Unable to generate the email: " + error.message;

        updateStatus(
            "Email generation failed: " + error.message,
            "#ef4444"
        );

    } finally {

        concernEmailBtn.disabled = false;
        concernEmailBtn.textContent = "✉ Raise a Privacy Concern";

    }

});


// ==========================================
// RECIPIENT VALIDATION
// ==========================================

function isValidRecipient(email) {

    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
        email.trim()
    );

}

grievanceRecipient.addEventListener("input", () => {

    openGmailBtn.disabled =
        !emailSubject.value.trim() ||
        !emailMessage.value.trim() ||
        !isValidRecipient(grievanceRecipient.value);

});

emailSubject.addEventListener("input", () => {

    openGmailBtn.disabled =
        !emailSubject.value.trim() ||
        !emailMessage.value.trim() ||
        !isValidRecipient(grievanceRecipient.value);

});

emailMessage.addEventListener("input", () => {

    openGmailBtn.disabled =
        !emailSubject.value.trim() ||
        !emailMessage.value.trim() ||
        !isValidRecipient(grievanceRecipient.value);

});


// ==========================================
// OPEN PREFILLED GMAIL COMPOSE
// ==========================================

openGmailBtn.addEventListener("click", async () => {

    const recipient = grievanceRecipient.value.trim();
    const subject = emailSubject.value.trim();
    const message = emailMessage.value.trim();

    if (!isValidRecipient(recipient)) {

        updateStatus(
            "Please enter a valid recipient email address.",
            "#ef4444"
        );

        return;
    }

    if (!subject || !message) {

        updateStatus(
            "Please complete the email subject and message.",
            "#ef4444"
        );

        return;
    }

    const gmailUrl =
        "https://mail.google.com/mail/?view=cm&fs=1" +
        "&to=" + encodeURIComponent(recipient) +
        "&su=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(message);

    try {

        await chrome.tabs.create({
            url: gmailUrl,
            active: true
        });

        updateStatus(
            "Gmail opened. Review your email before sending."
        );

    } catch (error) {

        console.error("Gmail opening error:", error);

        updateStatus(
            "Unable to open Gmail: " + error.message,
            "#ef4444"
        );

    }

});

// ==========================================
// START WORKSPACE
// ==========================================

initializeWorkspace();
