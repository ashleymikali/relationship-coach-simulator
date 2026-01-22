# Relationship Coach Simulator

An agentic narrative simulation driven by autonomous outcome modeling

⸻

# Overview

Relationship Coach Simulator is a narrative simulation game in which the player takes the role of a relationship therapist managing a small caseload of recurring clients. During therapy sessions, the player provides guidance and advice through dialogue choices. An LLM-based agent autonomously determines what happens between sessions: how clients interpret the advice, whether they act on it, and how their relationships evolve over time.

The central focus of the project is agentic outcome simulation. The agent does not select dialogue options or roleplay the player. Instead, it owns causality, memory, and long-term consequences. Clients persist across sessions, remember prior advice, and change their behavior based on accumulated history rather than isolated interactions.

This project is explicitly a simulation, not a real counseling tool, and includes clear disclaimers.

⸻

# Core Concept

You run a small relationship coaching practice with 3–4 recurring clients. Each client presents an ongoing relationship dilemma, often inspired by real-world scenarios sourced from Reddit relationship advice communities.

## During sessions
	•	The player listens, asks questions, and offers guidance.
	•	The agent does not intervene during dialogue or steer player choices.

## After sessions
	•	The agent independently evaluates the advice as a whole.
	•	It simulates what actions the client takes (or avoids) between sessions.
	•	Outcomes may be delayed, partial, or unexpected.

## Over time
	•	Clients remember what you said and how it worked out.
	•	Trust in you evolves based on repeated outcomes.
	•	Patterns emerge in your advice style and its effectiveness.
	•	Some clients improve, others stagnate, and some disengage entirely.

The game explores the tension between giving advice and being responsible for its consequences.

⸻

# What Makes This Agentic

Although the player provides advice, the system is agentic because the LLM agent controls everything outside the player’s direct input.

The agent:
	•	Maintains persistent state across multiple clients
	•	Interprets advice rather than executing it literally
	•	Simulates behavior over time, not single turns
	•	Decides when consequences surface
	•	Manages long-term trajectories (improvement, stagnation, disengagement)
	•	Reasons across accumulated history rather than isolated sessions

This is not a branching narrative or a scripted decision tree. The agent functions as a practice simulator, continuously updating a living world model based on player input and prior outcomes.

⸻

# Core Gameplay Loop
	1.	Client Session
    A client arrives (returning or new) and discusses their situation. The player engages through dialogue and offers guidance.
	2.	Advice Synthesis
    The session concludes with a clear therapeutic direction, expressed through the player’s advice.
	3.	Agent Processing
    The agent evaluates the advice holistically, considering:
	  •	 coherence and intent
	  •	client personality and context
	  •	prior advice and outcomes
	  •	current trust level
	4.	Between-Session Simulation
    The agent simulates what happens next:
	  •	which advice is followed or ignored
	  •	how relationships change
	  •	whether new issues emerge
	5.	Persistent Consequences
    The results carry forward into future sessions, shaping trust, behavior, and long-term outcomes.

⸻

# Trust as a Core State Variable

Trust is a first-class, persistent variable tracked for each client.
	•	Trust reflects how much the client believes in and follows the player’s advice.
	•	High trust increases the likelihood that advice is attempted consistently.
	•	Low trust causes clients to partially apply, distort, or ignore advice—even if it is sound.
	•	Trust changes slowly and compounds over time.

Importantly:
	•	Good advice can fail if trust is low.
	•	Poor advice can sometimes succeed if trust is high.
	•	Trust mediates outcomes rather than guaranteeing them.

This allows realistic dynamics where repeated missteps matter more than single mistakes.

⸻

# Agent Responsibilities

## 1. Client State Management

For each client, the agent maintains persistent structured state:
	•	Relationship context and history
	•	Advice received across sessions
	•	Trust level and qualitative notes
	•	Responsiveness to different advice styles
	•	Unresolved issues and recurring themes

This state persists across sessions and application restarts.

⸻

## 2. Outcome Simulation (Primary Agent Function)

After each session, the agent:
	•	Interprets the player’s advice holistically
	•	Evaluates it against the client’s personality, trust level, and past history
	•	Simulates client behavior probabilistically
	•	Determines delayed, partial, or compounding outcomes

Outcomes are not guaranteed to align with player intent, and consequences may surface several sessions later.

⸻

## 3. Memory & Continuity

The agent:
	•	Stores session histories and summaries
	•	Retrieves relevant past moments when needed
	•	References prior advice naturally in later sessions
	•	Surfaces unresolved conflicts instead of resetting scenarios

Clients do not “forget” unless the agent deliberately compresses memory.

⸻

## 4. Relationship Trajectories

The agent autonomously decides:
	•	How trust evolves
	•	Whether a client continues therapy
	•	When a client disengages or terminates
	•	Whether successful clients refer others

These decisions are based on accumulated outcomes, not scripted thresholds.

⸻

# MCP Tools (Agent-Invoked)

The agent chooses when to invoke tools; there is no fixed pipeline.
	1.	Scenario Intake Tool
	•	Provides anonymized relationship dilemmas
	•	Structured by conflict type and emotional volatility
	•	Used primarily for new client intake
	•	Cached locally (no live dependency required)
	2.	Client Database Manager
	•	Persistent storage for client profiles, trust, advice history, and summaries
	•	Supports agent queries about past effectiveness and unresolved issues
	3.	Session Memory System
	•	Stores dialogue and summaries
	•	Supports keyword or lightweight semantic search
	•	Enables accurate callbacks to prior advice
	4.	Outcome Simulator
	•	Agent-owned interface for simulating consequences
	•	Considers advice quality, trust, personality, and history
	•	Produces delayed or compounding outcomes

⸻

# Scope Constraints (Explicit)

To fit a 6-day development window:
	•	3–4 clients maximum
	•	Text-only UI
	•	Cached scenarios only
	•	Simple numeric trust metric with qualitative notes
	•	No content-heavy subplots

This is a systems demonstration, not a content-heavy game.

⸻

# Development Timeline (6 Days)

Day 1: Project scaffolding, UI shell, agent prompt design, client model
Day 2: Dialogue flow, state persistence, session logging
Day 3: Outcome simulation logic, trust updates, multi-client handling
Day 4: Memory retrieval, continuity testing, bug fixing
Day 5: UI refinement, agent decision visibility, failure testing
Day 6: Documentation, final testing, proposal polish

⸻

# Success Criteria

The system is considered successful if:
	•	Clients reference specific past advice correctly
	•	Trust evolves believably over time
	•	Poor advice produces lasting consequences
	•	Identical advice yields different outcomes based on history
	•	State persists across restarts
	•	Multiple clients are managed without state bleed

⸻

# Summary

Relationship Coach Simulator is an agentic narrative simulation centered on autonomy, memory, and long-term consequence. By separating player advice from agent-owned outcomes, the project demonstrates how small decisions compound over time in a persistent, human-like system.

The scope is intentionally constrained to ensure completion within six days while still clearly exhibiting agentic behavior.
