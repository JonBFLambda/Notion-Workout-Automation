# Notion Workout Automation

Automation of predefined workout routines in Notion using Pipedream and HTTP Shortcuts, enabling one-click logging of workouts directly from mobile.

---

## 1. Overview
This project integrates **Notion**, **Pipedream**, and **HTTP Shortcuts** to create a simple workflow for logging workout routines.  
Instead of manually adding each training session, the user can trigger a shortcut on their phone and automatically insert the workout data into their Notion database.

---

## 2. Motivation
The initial idea came from a limitation in Notion’s mobile app: while it is possible to duplicate templates on desktop, this option was missing in the mobile interface.  
Since my training log was becoming central to my workflow, I wanted a way to **automate and simplify routine insertion directly from my phone**.  
Although the project might appear simple, it focuses on **ergonomics and comfort**, solving a very specific real-world problem.

---

## 3. Features
- One-click mobile logging of workout routines via HTTP Shortcuts.  
- Serverless automation using Pipedream for handling requests and updating Notion.  
- Dynamic workout tracking: global routine count and per-type routine count (e.g. PUSH, PULL, LEGS).  
- Automatic persistence of static fields (e.g. “stands”), keeping training details consistent across sessions.  
- Error handling and logging included for debugging and reliability.  

---

## 4. Challenges & Solutions
This project involved several iterations and problem-solving steps:

1. **Local scripts vs. serverless approach**  
   - At first, I built Python scripts in Visual Studio to connect with the Notion API.  
   - These worked well, but required my PC to be active every time I wanted to log a workout.  
   - This didn’t match my vision of a **mobile-first, always-available solution**, so I shifted to Pipedream for a serverless trigger.  

2. **Notion API connection issues**  
   - Unlike the local scripts, the first Pipedream attempts had trouble authenticating and handling the Notion API properly.  
   - Several logic adjustments were required until the connection stabilized.  

3. **Custom numbering system**  
   - I wanted two separate counters:  
     - A **global order** for all workouts.  
     - A **per-type order** (e.g., PUSH #1, PUSH #2) displayed in the title.  
   - Achieving this required changes in the logic, ensuring both counters stayed consistent across multiple insertions.  

4. **Concurrency issue**  
   - When two requests were sent almost simultaneously, the counters sometimes overlapped.  
   - Although not critical for my daily use, it was an interesting challenge to detect and think about.  

---

## 5. Tech Stack
- **Notion API** – database integration and record creation.  
- **Pipedream** – serverless function execution and workflow automation.  
- **HTTP Shortcuts** – mobile interface to trigger requests with a single tap.  

---

## 6. How It Works
1. Create a database in Notion with the required properties (title, type, order, stands, etc.).  
2. Deploy the automation script on Pipedream.  
3. Configure HTTP Shortcuts to send POST requests to Pipedream with the workout type.  
4. Each request automatically inserts a new workout into Notion, updating both global and per-type counters.  

---

## 7. Learning Goals
This project was designed as a **learning exercise** to explore:  
- Connecting APIs (Notion, Pipedream, mobile triggers).  
- Automating repetitive workflows.  
- Debugging API validation errors and handling data consistency.  
- Building a personal productivity tool while improving programming skills.  

---

## 8. Future Improvements
- Develop a **custom mobile app** for workout tracking.  
- Add **data visualization** of training progress directly in Notion.  
- Extend automation to support **different templates** (strength, hypertrophy, mobility, etc.).  

---

## 9. About This Project
This is my **first automation project** published on GitHub.  

It reflects the beginning of my learning journey in programming, workflow automation, and API integration.  
The focus is not only on the final result, but also on the **process of problem-solving and iteration**.  
