
const detectBtn = document.getElementById("detectBtn");
const analyzeBtn = document.getElementById("analyzeBtn");
const extractBtn = document.getElementById("extractBtn");
const runAnalysisBtn = document.getElementById("runAnalysisBtn");

const summaryContent = document.getElementById("summaryContent");
const findingsContent = document.getElementById("findingsContent");
const checklistContent = document.getElementById("checklistContent");
const websiteName = document.getElementById("websiteName");
const websiteUrl = document.getElementById("websiteUrl");

const statusText = document.getElementById("statusText");
const statusIndicator = document.getElementById("statusIndicator");

const policyInfo = document.getElementById("policyInfo");
const policyUrl = document.getElementById("policyUrl");

const extractedSection = document.getElementById("extractedSection");
const extractedText = document.getElementById("extractedText");
const extractedLength = document.getElementById("extractedLength");

const results = document.getElementById("results");
const nutritionLabel = document.getElementById("nutritionLabel");
const labelWebsiteName = document.getElementById("labelWebsiteName");
const policyUpdated = document.getElementById("policyUpdated");
const nutritionItems = document.getElementById("nutritionItems");
const importantConsiderations = document.getElementById("importantConsiderations");

const continueBtn = document.getElementById("continueBtn");
const reviewDetailsBtn = document.getElementById("reviewDetailsBtn");
const goBackBtn = document.getElementById("goBackBtn");

let detectedPolicy = null;
let currentPolicyText = "";
let activeTabId = null;


// Update status
function updateStatus(message, color = "#22c55e") {
    statusText.textContent = message;
    statusIndicator.style.background = color;
}


// Get active tab
async function getActiveTab() {
    const tabs = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    return tabs[0];
}


// Update website information
async function loadWebsiteInfo() {
    const tab = await getActiveTab();

    if (!tab || !tab.url) {
        websiteName.textContent = "Website unavailable";
        websiteUrl.textContent = "";
        return;
    }

    activeTabId = tab.id;

    websiteName.textContent = tab.title || "Current website";
    websiteUrl.textContent = tab.url;
}


// Display detected policy in popup
function displayDetectedPolicy(detection) {

    detectedPolicy = detection;

    policyUrl.textContent = detection.url;
    policyInfo.classList.remove("hidden");

    extractedSection.classList.add("hidden");
    results.classList.add("hidden");

    currentPolicyText = "";

    if (detection.type === "current_page") {

        analyzeBtn.classList.add("hidden");
        extractBtn.classList.remove("hidden");

        updateStatus("Privacy policy page detected!");

    } else {

        analyzeBtn.classList.remove("hidden");
        extractBtn.classList.add("hidden");

        updateStatus("Privacy policy link detected!");
    }

    detectBtn.textContent = "Refresh Detection";
}


// Automatically load previously detected policy
async function loadSavedDetection() {

    try {
        const tab = await getActiveTab();

        if (!tab || !tab.id) return;

        activeTabId = tab.id;

        const key = `privacyLens_${tab.id}`;

        const saved = await chrome.storage.local.get(key);

        const storedData = saved[key];

        if (!storedData || !storedData.policy) {
            updateStatus("Ready to scan");
            return;
        }

        // Make sure the saved detection belongs to this page.
        if (storedData.pageUrl !== tab.url) {
            updateStatus("Ready to scan");
            return;
        }

        displayDetectedPolicy(storedData.policy);

        // Clear the notification badge for this tab.
        chrome.action.setBadgeText({
            tabId: tab.id,
            text: ""
        });

    } catch (error) {
        console.error("Saved detection error:", error);
        updateStatus("Ready to scan");
    }
}


// Manual detection fallback
detectBtn.addEventListener("click", async () => {

    detectBtn.disabled = true;

    policyInfo.classList.add("hidden");
    extractedSection.classList.add("hidden");
    extractBtn.classList.add("hidden");
    analyzeBtn.classList.add("hidden");
    results.classList.add("hidden");

    detectedPolicy = null;
    currentPolicyText = "";

    updateStatus("Searching for privacy policy...", "#f59e0b");

    try {
        const tab = await getActiveTab();

        if (!tab || !tab.id || !tab.url) {
            throw new Error("Unable to access the current tab.");
        }

        activeTabId = tab.id;

        if (
            tab.url.startsWith("chrome://") ||
            tab.url.startsWith("chrome-extension://") ||
            tab.url.startsWith("edge://")
        ) {
            throw new Error("Open a normal website before scanning.");
        }

        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ["content.js"]
        });

        const response = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => window.privacyLensDetectPolicy()
        });

        const detection = response[0]?.result;

        if (!detection || !detection.found) {
            updateStatus("No privacy policy found.", "#ef4444");
            return;
        }

        displayDetectedPolicy(detection);

    } catch (error) {
        console.error(error);
        updateStatus(error.message || "Detection failed.", "#ef4444");

    } finally {
        detectBtn.disabled = false;
    }
});


// Open detected privacy policy in a new tab

// Open policy in a new tab and remember the original website


analyzeBtn.addEventListener("click", async () => {

    if (!detectedPolicy?.url) {
        updateStatus("No policy URL available.", "#ef4444");
        return;
    }

    try {
        const originalTab = await getActiveTab();

        if (!originalTab?.id) {
            throw new Error("Original website tab unavailable.");
        }

        updateStatus("Opening privacy policy...", "#f59e0b");

        const response = await chrome.runtime.sendMessage({
            type: "OPEN_POLICY_TAB",
            policyUrl: detectedPolicy.url,
            originTabId: originalTab.id
        });

        if (!response?.success) {
            throw new Error(response?.error || "Could not open policy.");
        }

    } catch (error) {
        console.error(error);
        updateStatus(error.message, "#ef4444");
    }
});




// Extract text from the current policy page
extractBtn.addEventListener("click", async () => {

    extractBtn.disabled = true;

    updateStatus("Extracting policy text...", "#f59e0b");

    try {
        const tab = await getActiveTab();

        if (!tab || !tab.id) {
            throw new Error("Unable to access the current tab.");
        }


        const response = await chrome.scripting.executeScript({
            target: { tabId: tab.id },

            func: () => {

                // Find likely main content containers.
                const selectors = [
                    "main",
                    "article",
                    '[role="main"]',
                    ".privacy-policy",
                    "#privacy-policy",
                    ".policy-content",
                    "#content"
                ];

                const candidates = selectors
                    .flatMap(selector =>
                        Array.from(document.querySelectorAll(selector))
                    );

                // Select the most relevant content container.
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

                // Use main content if found, otherwise fall back to body.
                const root = (bestRoot || document.body).cloneNode(true);

                // Remove unrelated page elements.
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

                // Extract readable text.
                let text = root.innerText || root.textContent || "";

                // Clean up whitespace.
                text = text
                    .replace(/\r/g, "")
                    .replace(/[ \t]+/g, " ")
                    .replace(/\n[ \t]*\n[ \t]*\n/g, "\n\n")
                    .trim();

                // Remove common navigation-only lines.
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
                    text: text
                };
            }
        });



        const page = response[0]?.result;

        if (!page || page.text.trim().length < 50) {
            throw new Error("Not enough readable text found.");
        }

        currentPolicyText = page.text.trim();

        extractedText.textContent = currentPolicyText;

        extractedLength.textContent =
            `${currentPolicyText.length.toLocaleString()} characters extracted`;

        extractedSection.classList.remove("hidden");

        updateStatus("Policy text extracted successfully!");

    } catch (error) {
        console.error(error);

        updateStatus(
            error.message || "Text extraction failed.",
            "#ef4444"
        );

    } finally {
        extractBtn.disabled = false;
    }
});


// Listen for new automatic detections while popup is open
chrome.storage.onChanged.addListener(async (changes, areaName) => {

    if (areaName !== "local" || activeTabId === null) return;

    const key = `privacyLens_${activeTabId}`;

    if (!changes[key] || !changes[key].newValue) return;

    const tab = await getActiveTab();

    if (!tab || tab.id !== activeTabId) return;

    const savedData = changes[key].newValue;

    if (savedData.pageUrl !== tab.url) return;

    displayDetectedPolicy(savedData.policy);
});


function renderNutritionLabel(data) {

    const categories = data.privacy_findings?.categories || [];

    nutritionItems.replaceChildren();
    importantConsiderations.replaceChildren();

    labelWebsiteName.textContent =
        websiteName.textContent || "Current website";

    // Extract policy update date from the extracted policy.
    const dateMatch = currentPolicyText.match(
        /last updated(?:\s+on)?\s*:?\s*([^\n]+)/i
    );

    policyUpdated.textContent = dateMatch
        ? `Policy ${dateMatch[0].trim()}`
        : "Policy update date not identified.";

    const categoryMap = {
        "First Party Collection/Use": "Personal information collection",
        "Third Party Sharing/Collection": "Third-party sharing",
        "User Choice/Control": "Your available choices",
        "Data Retention": "Data retention",
        "Data Security": "Security safeguards",
        "User Access, Edit and Deletion": "Access and deletion rights",
        "Policy Change": "Policy updates",
        "International and Specific Audiences": "Specific audiences",
        "Other": "Other privacy practices"
    };

    // Show detected privacy topics.
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

    // Select findings that deserve attention.
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

            // Include one short supporting excerpt.
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

function highlightEvidence(excerpt) {

    if (!currentPolicyText || !excerpt) {
        updateStatus("Policy text or evidence unavailable.", "#ef4444");
        return;
    }

    const policyText = currentPolicyText;

    // Try to find the complete evidence excerpt first.
    let matchIndex = policyText.indexOf(excerpt);

    // If the complete excerpt is unavailable, try its first 100 characters.
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

    // Rebuild the policy preview with a highlighted match.
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

    // Reveal the extracted policy.
    extractedSection.classList.remove("hidden");

    extractedSection.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

    // Bring the highlighted evidence into view.
    setTimeout(() => {
        highlight.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    }, 250);

    updateStatus("Supporting evidence highlighted!", "#22c55e");
}


// Initialize popup
async function initializePopup() {
    await loadWebsiteInfo();
    await loadSavedDetection();
}

initializePopup();


// Send extracted policy text to FastAPI backend
runAnalysisBtn.addEventListener("click", async () => {

    if (!currentPolicyText || currentPolicyText.length < 50) {
        updateStatus("Please extract a valid policy first.", "#ef4444");
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

        if (!response.ok) {
            throw new Error(
                data.detail || "Backend analysis failed."
            );
        }

        // Display summary
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


        // Display ML findings
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


        // Display DPDP checklist
        checklistContent.replaceChildren();

        (data.dpdp_checklist || []).forEach(item => {

            const card = document.createElement("div");
            card.style.marginBottom = "12px";

            const title = document.createElement("strong");
            title.textContent = item.title;

            const status = document.createElement("p");
            status.textContent = `Status: ${item.status}`;

            const explanation = document.createElement("p");
            explanation.textContent = item.explanation;

            card.append(title, status, explanation);

            (item.evidence || []).forEach(text => {

                const evidence = document.createElement("p");

                evidence.textContent = `Evidence: ${text}`;

                card.appendChild(evidence);
            });

            checklistContent.appendChild(card);
        });

        // Build the user-facing Privacy Nutrition Label.
        renderNutritionLabel(data);

        // Keep detailed analysis available as a secondary view.
        results.classList.add("hidden");

        updateStatus("Privacy analysis completed!", "#22c55e");

    } catch (error) {
        console.error("PrivacyLens API error:", error);

        updateStatus(
            error.message || "Unable to connect to the backend.",
            "#ef4444"
        );

    } finally {
        runAnalysisBtn.disabled = false;
        runAnalysisBtn.textContent = "Analyse with PrivacyLens AI";
    }
});
// Review Details button
reviewDetailsBtn.addEventListener("click", () => {

    results.classList.remove("hidden");

    results.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
});
// Return to the original website

async function returnToOriginalWebsite(action) {

    try {
        const currentTab = await getActiveTab();

        if (!currentTab?.id) {
            throw new Error("Current policy tab unavailable.");
        }

        const response = await chrome.runtime.sendMessage({
            type: "RETURN_TO_ORIGINAL",
            policyTabId: currentTab.id,
            action: action
        });

        if (!response?.success) {
            throw new Error(
                response?.error || "Navigation failed."
            );
        }

    } catch (error) {
        console.error("Navigation error:", error);

        updateStatus(
            error.message || "Navigation failed.",
            "#ef4444"
        );
    }
}


// Continue to website
continueBtn.addEventListener("click", async () => {
    await returnToOriginalWebsite("continue");
});


// Go back to search page
goBackBtn.addEventListener("click", async () => {
    await returnToOriginalWebsite("back");
});
