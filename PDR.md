# Pixel Tasker Agent PRD – Prototype (Version 1.0)

**Date:** July 13, 2025
**Author:** Mark Ofir

---

## 1. **Product Overview**

**Product Name:** Pixel Tasker Agent
**Version:** 1.0 (Prototype)

**Description:**
Pixel Tasker Agent is an AI‑powered assistant designed for the Google Pixel 8 Pro (Android 14+), enabling users to create, configure, and test Tasker automations via natural-language instructions. It leverages the Google Agent Development Kit (ADK), Gemini visual recognition, scrcpy for screen mirroring, and ADB/uiautomator2 for device control—all orchestrated from a Linux host (e.g., Linux Mint).

**Target Users:**

* Android enthusiasts and power users
* Developers and hobbyists experienced with ADB/Python
* Individuals interested in device automation and conversational interfaces

## 📌 Pixel Tasker Agent PRD – Prototype Version 1.0

**Platforms:**

* **Host:** Linux (tested on Mint)
* **Device:** Pixel 8 Pro with Android 14+
* **Backend Services:** Gemini API for visual analysis

---

### 2. **Goals & Non-Goals**

#### **Primary Goals**

* Enable users to describe Tasker automations in plain language (e.g., “turn off Wi‑Fi at low battery”).
* Utilize real-time screen capture and computer vision to identify UI elements in Tasker.
* Plan interaction flows cooperatively via chat, then execute them (taps, text entry).
* Test created automations through Tasker intents and verify outcomes.
* Provide screen mirroring so users can monitor agent actions visually.

#### **Non-Goals (Prototype Constraints)**

* Voice input/output (limited to text; voice may be added later).
* Compatibility across other devices or platforms beyond Pixel 8 Pro.
* Production-grade deployment (e.g., full security, polish, scalability).

---

### 3. **Key Features & Requirements**

| Feature                         | Description                                                            | Priority |
| ------------------------------- | ---------------------------------------------------------------------- | -------- |
| **Natural-Language Task Input** | Accepts free-form text and converts to Tasker task logic.              | High     |
| **Visual UI Recognition**       | Detects on-screen elements in Tasker via Gemini API (e.g. “Add Task”). | High     |
| **Interactive Planning**        | Conversational step-by-step plan review before execution.              | Medium   |
| **Automated UI Navigation**     | Simulates clicks, text input, navigation flows.                        | High     |
| **Task Testing & Verification** | Fires intents to exercise created Tasker logic and checks outcomes.    | High     |
| **Screen Mirroring**            | Displays real-time device screen via scrcpy for user visibility.       | Medium   |

---

### 4. **Architecture**

#### **Host-Side Components (Linux)**

* **Controller Service**: Python script using ADB + uiautomator2.
* **Vision Module**: Wraps Gemini for UI component recognition.
* **Planner Module**: Converts NL instructions into actionable UI flow.
* **Communication Interface**: Chat UI for user-agent interaction.
* **Screen Mirroring**: Integrates scrcpy to stream device UI.

#### **Device-Side Components (Pixel 8 Pro)**

* **Tasker App**: Manages routine automations.
* **UI Response Mechanism**: Tasker screens navigated via automated UI events.
* **Task Execution**: Tasker tasks triggered via intents for testing.

---

### 5. **User Flow**

1. **Initiation**
   User launches the controller on Linux; scrcpy opens for screen mirroring.

2. **Instruction Input**
   User types a command: e.g. “Set Wi‑Fi off when battery <20%”.

3. **Planning**
   Agent responds with a draft plan: “Open Tasker → Add new profile → Battery level …”.
   Users refine or approve this plan via chat.

4. **Execution**
   After confirmation, the agent navigates the Tasker UI to implement the task.

5. **Testing**
   Agent sends a test intent (e.g., battery=15%), verifies the response (Wi-Fi toggles correctly).

6. **Feedback & Iteration**
   Agent provides success/failure feedback; user can refine or repeat.

---

### 6. **Technical Requirements**

#### **System Requirements**

* **Host:** Linux Mint (or compatible)
* **Device:** Pixel 8 Pro running Android 14+
* **Software Dependencies:**

  * Python ≥ 3.10
  * ADB & uiautomator2
  * scrcpy
  * Google ADK + Gemini API credentials
  * Tasker (installed and set up on device)

#### **Security & Privacy**

* Operates locally; only minimal visual/UI data transmitted to Gemini.
* ADB control limited to device – no unnecessary permissions requested.

---

### 7. **Success Criteria**

* **Usability:** ≥70% tasks defined and implemented correctly on first try.
* **Reliability:** UI flows succeed in ≥90% of execution attempts.
* **Testing Accuracy:** Agent verifies task outcomes with ≥95% correctness.

---

### 8. **Risks & Mitigations**

1. **UI Variation:** Tasker UI might change across versions → mitigate with updated vision training.
2. **Recognition Failures:** Mitigate via visual confidence thresholds or fallback to manual selection.
3. **Automation Errors:** Provide rollback or manual guidance if tasks fail.
4. **API Latency:** Optimize batching, caching, or parallel API calls.

---

### 9. **Milestones & Roadmap**

1. **MVP Delivery (v1.0):** Basic NL → Tasker task creation with simple battery/Wi‑Fi tasks.
2. **Interactive Revisions:** Allow users to edit detected steps before execution.
3. **Extended Testing:** Add deeper test cases (connectivity, app launching).
4. **Voice Prototype:** Explore speech input/output (optional).
5. **Device Expansion:** Support for broader Android devices (future versions).

---

### 10. **Appendices**

#### A. Example Conversation

**User:** “Create a Tasker task to turn off Wi‑Fi when battery < 20%.”
**Agent:**

> “Plan: 1) Open Tasker; 2) Profiles → + → State → Battery Level (<20%); 3) New task named ‘LowBatteryWiFiOff’; 4) Add ‘Wi‑Fi → Set Off’; 5) Save. Approve?”
> **User:** “Yes.”
> *(Agent executes plan, tests with synthetic battery intent — result: Wi‑Fi toggles off — success reported.)*

#### B. System Diagram

#*(Insert diagrams visually mapping interactions between Host Controller, Gemini API, scrcpy, Tasker, and Pixel device.)*

---

### 🧠 Next Steps

* Draft UI wireframes for the chat + mirroring interface.
* Define Gemini vision models for common Tasker UI elements.
* Develop core modules: Planner, Vision, Executor.
* Set up CI tests against Tasker on emulators or real devices.
* Begin user trials with target audience.