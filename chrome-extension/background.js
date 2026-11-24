
// Wait until a tab finishes loading.
function waitForTabComplete(tabId) {
    return new Promise((resolve, reject) => {
        const listener = (updatedTabId, changeInfo, tab) => {
            if (updatedTabId === tabId && changeInfo.status === "complete") {
                chrome.tabs.onUpdated.removeListener(listener);
                resolve(tab);
            }
        };

        chrome.tabs.onUpdated.addListener(listener);

        // Check whether the tab has already finished loading.
        chrome.tabs.get(tabId).then(tab => {
            if (tab.status === "complete") {
                chrome.tabs.onUpdated.removeListener(listener);
                resolve(tab);
            }
        }).catch(error => {
            chrome.tabs.onUpdated.removeListener(listener);
            reject(error);
        });
    });
}


chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {

    // 1. Automatic policy detection
    if (message.type === "PRIVACY_POLICY_DETECTED") {

        const tabId = sender.tab?.id;

        if (tabId === undefined) return;

        const key = `privacyLens_${tabId}`;

        chrome.storage.local.set({
            [key]: {
                policy: message.policy,
                pageUrl: message.pageUrl,
                detectedAt: Date.now()
            }
        });

        chrome.action.setBadgeText({
            tabId,
            text: "!"
        });

        chrome.action.setBadgeBackgroundColor({
            tabId,
            color: "#0ea5e9"
        });

        return;
    }


    // 2. Launch the PrivacyLens workspace
    if (message.type === "LAUNCH_WELCOME_PAGE") {

        (async () => {

            const originTabId = sender.tab?.id;

            if (originTabId === undefined || !message.policy?.url) {
                throw new Error("Missing website or policy information.");
            }

            const policyURL = new URL(message.policy.url);

            if (!["https:", "http:"].includes(policyURL.protocol)) {
                throw new Error("Unsupported policy URL.");
            }

            // Create the workspace tab.
            const welcomeTab = await chrome.tabs.create({
                url: "about:blank",
                active: true
            });

            // Save policy information before loading the workspace.
            await chrome.storage.local.set({
                [`privacyLensWelcome_${welcomeTab.id}`]: {
                    policy: message.policy,
                    pageUrl: message.pageUrl || sender.tab.url,
                    originTabId,
                    createdAt: Date.now()
                }
            });

            // Load the workspace.
            await chrome.tabs.update(welcomeTab.id, {
                url: chrome.runtime.getURL("welcome.html")
            });

            sendResponse({
                success: true,
                welcomeTabId: welcomeTab.id
            });

        })().catch(error => {

            console.error("Welcome page error:", error);

            sendResponse({
                success: false,
                error: error.message
            });

        });

        return true;
    }


    // 3. Open policy in the background and return to workspace
    if (message.type === "OPEN_POLICY_TAB") {

        (async () => {

            const workspaceTabId = sender.tab?.id;
            const originTabId = message.originTabId;

            if (
                workspaceTabId === undefined ||
                originTabId === undefined ||
                !message.policyUrl
            ) {
                throw new Error("Missing workspace, website or policy information.");
            }

            const policyURL = new URL(message.policyUrl);

            if (!["https:", "http:"].includes(policyURL.protocol)) {
                throw new Error("Unsupported policy URL.");
            }

            const workspaceTab = await chrome.tabs.get(workspaceTabId);
            const originalTab = await chrome.tabs.get(originTabId);

            // Open policy in the same window, without taking focus.
            const policyTab = await chrome.tabs.create({
                url: policyURL.href,
                active: false,
                windowId: workspaceTab.windowId
            });

            // Save the relationship between all three tabs.
            await chrome.storage.local.set({
                [`privacyLensOrigin_${policyTab.id}`]: {
                    originTabId: originalTab.id,
                    originUrl: originalTab.url,
                    policyUrl: policyURL.href,
                    policyTabId: policyTab.id,
                    workspaceTabId: workspaceTab.id
                },

                [`privacyLensWorkspace_${workspaceTab.id}`]: {
                    originTabId: originalTab.id,
                    policyTabId: policyTab.id,
                    policyUrl: policyURL.href
                }
            });

            console.log("PRIVACYLENS POLICY TAB OPENED", {
                originTabId: originalTab.id,
                workspaceTabId: workspaceTab.id,
                policyTabId: policyTab.id,
                policyUrl: policyURL.href
            });

            // Wait for the policy page to finish loading.
            await waitForTabComplete(policyTab.id);

            // Bring the workspace back into focus.
            await chrome.tabs.update(workspaceTab.id, {
                active: true
            });

            await chrome.windows.update(workspaceTab.windowId, {
                focused: true
            });

            sendResponse({
                success: true,
                policyTabId: policyTab.id,
                workspaceTabId: workspaceTab.id
            });

        })().catch(error => {

            console.error("Open policy error:", error);

            sendResponse({
                success: false,
                error: error.message
            });

        });

        return true;
    }


    // 4. Return to the original website
    if (message.type === "RETURN_TO_ORIGINAL") {

        (async () => {

            const policyTabId = message.policyTabId;
            const action = message.action;

            const key = `privacyLensOrigin_${policyTabId}`;

            const saved = await chrome.storage.local.get(key);
            const origin = saved[key];

            if (!origin || origin.originTabId === undefined) {
                throw new Error(
                    "Original website information not found."
                );
            }

            const originalTab = await chrome.tabs.get(origin.originTabId);

            let wentBack = false;

            if (action === "back") {
                try {
                    await chrome.tabs.goBack(originalTab.id);
                    wentBack = true;
                } catch (error) {
                    console.warn(
                        "No previous page available in browser history.",
                        error
                    );
                }
            }

            // Close the policy tab.
            await chrome.tabs.remove(policyTabId);

            // Activate the original website.
            await chrome.tabs.update(originalTab.id, {
                active: true
            });

            await chrome.windows.update(originalTab.windowId, {
                focused: true
            });

            // Clean up saved associations.
            await chrome.storage.local.remove([
                key,
                `privacyLensWorkspace_${origin.workspaceTabId}`
            ]);

            sendResponse({
                success: true,
                action,
                wentBack
            });

        })().catch(error => {

            console.error("Return navigation error:", error);

            sendResponse({
                success: false,
                error: error.message
            });

        });

        return true;
    }

});
