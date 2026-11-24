
// PrivacyLens India - Automatic Policy Detection V3

window.privacyLensDetectPolicy = function () {

    const currentPageText = [
        location.href,
        document.title,
        document.querySelector("h1")?.innerText || ""
    ].join(" ").toLowerCase();

    const currentPageLooksLikePolicy =
        /privacy[\s_-]*(policy|notice|statement)/i.test(currentPageText);

    if (currentPageLooksLikePolicy) {
        return {
            found: true,
            type: "current_page",
            url: location.href,
            text: document.title || "Privacy Policy"
        };
    }

    const links = Array.from(
        document.querySelectorAll("a[href]")
    );

    const candidates = links.map(link => {

        const text = (
            link.innerText ||
            link.textContent ||
            ""
        ).trim().toLowerCase();

        const href = link.href.toLowerCase();

        const aria = (
            link.getAttribute("aria-label") || ""
        ).toLowerCase();

        const title = (
            link.getAttribute("title") || ""
        ).toLowerCase();

        const combined = `${text} ${href} ${aria} ${title}`;

        let score = 0;

        if (/privacy[\s_-]*policy/.test(combined)) score += 12;
        if (/privacy[\s_-]*notice/.test(combined)) score += 10;
        if (/privacy[\s_-]*statement/.test(combined)) score += 10;

        if (text === "privacy") score += 8;
        if (aria === "privacy" || title === "privacy") score += 7;

        if (/\/privacy(?:\/|$|[?#_-])/.test(href)) score += 8;
        if (href.includes("privacy-policy")) score += 8;

        if (combined.includes("data protection")) score += 5;
        if (combined.includes("personal data")) score += 4;

        if (
            /privacy[\s_-]*settings|cookie[\s_-]*settings|privacy[\s_-]*preferences/.test(combined)
        ) {
            score -= 10;
        }

        return {
            url: link.href,
            text: text || aria || title || link.href,
            score
        };
    });

    const matching = candidates
        .filter(item => {
            try {
                const url = new URL(item.url);

                return (
                    item.score >= 7 &&
                    ["https:", "http:"].includes(url.protocol)
                );
            } catch {
                return false;
            }
        })
        .sort((a, b) => b.score - a.score);

    if (matching.length > 0) {
        return {
            found: true,
            type: "policy_link",
            url: matching[0].url,
            text: matching[0].text,
            confidence: matching[0].score
        };
    }

    return {
        found: false,
        message: "No likely privacy policy link was found."
    };
};


// Show a notification when a likely policy is detected.
(function showPrivacyLensNotification() {

    // Prevent duplicate notifications if the script is injected again.
    if (window.__privacyLensNotificationInitialized) return;

    window.__privacyLensNotificationInitialized = true;

    const policy = window.privacyLensDetectPolicy();

    if (!policy.found) return;
    // Save the detected policy through the background worker.
    chrome.runtime.sendMessage({
        type: "PRIVACY_POLICY_DETECTED",
        policy: policy,
        pageUrl: location.href
    });

    // Avoid repeatedly notifying on the same page.
    if (document.getElementById("privacyLensAutoNotice")) return;

    const host = document.createElement("div");
    host.id = "privacyLensAutoNotice";

    const shadow = host.attachShadow({ mode: "closed" });

    const style = document.createElement("style");

    style.textContent = `
        .notice {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 320px;
            box-sizing: border-box;
            z-index: 2147483647;
            padding: 17px;
            border: 1px solid #334155;
            border-radius: 14px;
            background: #101b2d;
            color: #f8fafc;
            font-family: Arial, sans-serif;
            box-shadow: 0 8px 30px rgba(0,0,0,.3);
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .brand {
            font-size: 15px;
            font-weight: 700;
            color: #38bdf8;
        }

        .close {
            border: none;
            background: transparent;
            color: #cbd5e1;
            font-size: 22px;
            cursor: pointer;
        }

        .heading {
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 7px;
        }

        .message {
            font-size: 13px;
            line-height: 1.5;
            color: #cbd5e1;
        }

        .hint {
            margin-top: 12px;
            padding: 10px;
            border-radius: 8px;
            background: #1e293b;
            color: #bae6fd;
            font-size: 12px;
            line-height: 1.5;
        }

        .launch {
            width: 100%;
            margin-top: 12px;
            padding: 11px;
            border: none;
            border-radius: 8px;
            background: #0ea5e9;
            color: #ffffff;
            font-size: 13px;
            font-weight: 700;
            cursor: pointer;
        }

        .launch:hover {
            background: #0284c7;
        }

    `;

    const card = document.createElement("div");
    card.className = "notice";

    const header = document.createElement("div");
    header.className = "header";

    const brand = document.createElement("div");
    brand.className = "brand";
    brand.textContent = "PrivacyLens";

    const close = document.createElement("button");
    close.className = "close";
    close.type = "button";
    close.textContent = "×";
    close.setAttribute("aria-label", "Dismiss notification");

    close.addEventListener("click", () => host.remove());

    header.append(brand, close);

    const heading = document.createElement("div");
    heading.className = "heading";
    heading.textContent = "Privacy policy detected!";

    const message = document.createElement("div");
    message.className = "message";
    message.textContent =
        "We found a likely privacy policy on this website.";


        const hint = document.createElement("div");
        hint.className = "hint";
        hint.textContent =
            "Want to understand how your data is handled? Start with PrivacyLens.";

        const launchButton = document.createElement("button");
        launchButton.className = "launch";
        launchButton.type = "button";
        launchButton.textContent = "Analyse Privacy Policy →";

        launchButton.addEventListener("click", () => {

            chrome.runtime.sendMessage({
                type: "LAUNCH_WELCOME_PAGE",
                policy: policy,
                pageUrl: location.href
            }, (response) => {

                if (chrome.runtime.lastError) {
                    console.error(
                        "PrivacyLens launch error:",
                        chrome.runtime.lastError.message
                    );
                    return;
                }

                if (response?.success) {
                    host.remove();
                } else {
                    console.error(
                        "PrivacyLens could not open:",
                        response?.error
                    );
                }

            });

        });


    card.append(header, heading, message, hint, launchButton);
    shadow.append(style, card);
    document.documentElement.appendChild(host);

})();
