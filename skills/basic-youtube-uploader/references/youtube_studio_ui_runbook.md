# Simple YouTube Studio Browser Upload Runbook (`youtube_studio_ui_runbook.md`)

This runbook details the exact browser actions needed to upload a local video file to YouTube Studio (`https://studio.youtube.com`), write a **Title** and **Description**, set Visibility to **Unlisted**, and save it cleanly using either **Chrome (`chrome-devtools`)** or the **ChatGPT internal browser** as an automatic fallback.

---

## Step 1: Open YouTube Studio & Start Upload (Chrome or ChatGPT Internal Browser)

1. **Choose Browser (Automatic Fallback)**:
   - Try opening or connecting to the Chrome browser via `chrome-devtools` (`list_pages` / `navigate_page`).
   - **If the agent is unable to open Chrome**: Immediately switch to the **ChatGPT internal browser** (built-in browser tool) and execute all steps below inside the internal browser.
2. **Navigate to YouTube Studio**:
   - Open `https://studio.youtube.com` and inspect the dashboard.
   - *If redirected to Google Sign-In*: Ask the user to log in on the open browser window and wait for confirmation.
3. **Open the Upload Dialog**:
   - Click the **`"Create"`** button in the top-right header (`button "Create"`), then click **`"Upload videos"`** (`menuitem "Upload videos"`), OR click the **`"Upload videos"`** button directly on the dashboard.
4. **Upload the Local Video File**:
   - Attach the local video file using the **`"Select files"`** button (or file input) with `filePath` set to the absolute path of the local video file.
   - Wait for the upload modal (`ytcp-uploads-dialog`) to transition to the **Details** view.

---

## Step 2: Fill Title, Description & Audience (`Details` Tab)

1. **Title (`<= 100` characters)**:
   - Locate the Title textbox in the snapshot (`textbox "Add a title that describes your video (type @ to mention a channel)"`).
   - Use `fill` with the clean Title string.
2. **Description**:
   - Locate the Description textbox (`textbox "Tell viewers about your video (type @ to mention a channel)"`).
   - Use `fill` with the Description string.
3. **Audience (Required by YouTube Studio to Save)**:
   - Locate the radio button **`"No, it's not made for kids"`** (`radio "No, it's not made for kids"`).
   - If it is not already checked, call `click` on its `uid`.
   - Do **not** click `"Show more"` or configure optional tabs unless explicitly requested.

---

## Step 3: Set Visibility to `Unlisted` & Save (`Visibility` Tab)

1. **Open the `Visibility` Step**:
   - In the top stepper of the upload modal, click **`"Visibility"`** (`button "Visibility"`), OR click **`"Next"`** (`button "Next"`) 3 times until the **Visibility** view appears.
2. **Select `Unlisted`**:
   - Call `take_snapshot` and locate the **`"Unlisted"`** radio button (`radio "Unlisted"`).
   - Call `click` on the **`"Unlisted"`** radio button.
   - Call `take_snapshot` to confirm `radio "Unlisted"` shows `checked`.
3. **Copy Video URL & Click `Save`**:
   - Read the `https://youtu.be/<VIDEO_ID>` link from the right-hand video preview panel in the snapshot.
   - Click the **`"Save"`** button (`button "Save"` / `#done-button`).
   - Wait 2–3 seconds and take a snapshot to confirm the upload is saved/complete, then return the Unlisted link to the user.
