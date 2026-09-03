/**
 * stub_data.js — Mock Sample Data matching the locked JSON schema in TECH_STACK.md
 * Used by Anurodh's renderer for offline / stubbed testing prior to live API connection.
 */

window.STUB_MENTOR_DATA = {
  "problem_summary": "You are building a Campus Food Wastage Prevention System aimed at predicting daily meal demand in college canteens and enabling dynamic portion ordering for students.",
  "key_questions": [
    "How will canteen staff input daily menu items and available quantity?",
    "What incentive encourages students to order half-portions or pre-notify attendance?",
    "What is the simplest working prototype you can finish in the next 60 minutes?"
  ],
  "user_personas": [
    {
      "name": "Canteen Manager (Ramesh)",
      "need": "Accurate daily headcounts to avoid cooking surplus food.",
      "pain_point": "High unpredictable variance in student attendance on Fridays."
    },
    {
      "name": "Hostel Student (Priya)",
      "need": "Quick pre-ordering option for custom portion sizes.",
      "pain_point": "Forced to buy full meals when only wanting light snacks."
    }
  ],
  "design_thinking_guidance": "1. Empathize: Talk to canteen staff about peak waste hours. 2. Define: 'Students waste 30% of meals because portion sizes are fixed.' 3. Ideate: Simple QR-code pre-ordering vs. surplus discount alerts. 4. Prototype: Form with meal selection + dynamic count calculator. 5. Test: Simulate 10 student orders with dummy data.",
  "feature_suggestions": [
    {
      "feature": "Student Pre-Ordering Input Form",
      "why": "Collects advance headcounts before food prep starts.",
      "effort": "low"
    },
    {
      "feature": "Real-time Canteen Demand Dashboard",
      "why": "Displays aggregated meal counts to kitchen staff.",
      "effort": "medium"
    },
    {
      "feature": "Surplus Meal Alert Notification System",
      "why": "Alerts students when extra meals are available at discount near closing.",
      "effort": "high"
    }
  ],
  "tech_stack_options": [
    "Frontend: Vanilla HTML/CSS + JavaScript (Glassmorphism UI)",
    "Backend: Python Flask REST API (`POST /api/mentor`)",
    "Data: In-memory JavaScript objects / JSON files (Skip DB for speed)"
  ],
  "prototype_priorities": [
    "P0 (Must Have): Single form for meal pre-order and manager summary view",
    "P1 (Should Have): Visual chart/cards showing saved meals count",
    "P2 (Nice to Have): Gamified green points for students"
  ],
  "validation_checkpoints": [
    "Can a student complete a pre-order in under 15 seconds?",
    "Does the manager view update accurately when a new order comes in?"
  ],
  "demo_prep_tips": [
    "Prepare 2 pre-filled test cases — never type live under time pressure",
    "Highlight the Decision block during the pitch: 'We built P0 first to prove feasibility'",
    "Emphasize the 70% Knowledge Base + 30% LLM architecture to the jury"
  ],
  "decision": "Build the P0 pre-order form and manager summary dashboard first.",
  "reason": "A complete end-to-end user flow (Student order → Manager view) proves feasibility and scores higher than multiple half-finished features.",
  "next_action": "Lock the JSON request/response contract with your team, build the student input form, and wire it directly to the backend renderer."
};
