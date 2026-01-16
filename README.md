# Relationship Coach Simulator

A narrative simulation game where you play as a relationship therapist managing recurring clients while navigating your own dating life. An AI agent orchestrates client outcomes, tracks therapeutic relationships, and manages the consequences of your advice.

## Core Concept

You run a small relationship coaching practice with 3-5 recurring clients who come to you with real relationship dilemmas sourced from Reddit’s relationship advice communities. As their therapist, you provide guidance through dialogue choices, and the AI agent simulates outcomes based on the quality and nature of your advice. Clients remember everything you’ve told them, return with follow-up issues, and their trust in you evolves based on whether your guidance helps or harms them.

The game explores the tension between giving advice and living it - as a stretch goal, you’ll also navigate your own dating life with 1-2 potential partners, creating opportunities for hypocrisy, growth, and thematic resonance between your professional and personal worlds.

## Agent Architecture

The LLM agent acts as the game master, managing multiple interconnected systems:

- **Client State Management**: Tracks each client’s relationship history, past advice received, outcomes from following your guidance, trust levels, and therapeutic progress
- **Outcome Simulation**: After each session, determines what happened when clients applied your advice - did their relationship improve, deteriorate, or remain unchanged?
- **Memory & Continuity**: Maintains detailed session notes for each client, ensures they reference past conversations naturally, and creates realistic follow-up scenarios based on previous outcomes
- **Relationship Dynamics**: Manages how clients’ trust in you evolves - successful advice builds rapport, harmful advice damages the therapeutic relationship, and clients may eventually terminate therapy or refer others based on their experience

The agent doesn’t just respond to your choices - it actively simulates a living practice where clients have ongoing lives between sessions.

## Game Flow

### Session Structure

1. **Client Check-in**: A client arrives for their appointment (new client or returning)
1. **Problem Presentation**: For new issues, the agent presents a scenario sourced from Reddit; for follow-ups, the agent reports outcomes from previous advice
1. **Therapeutic Dialogue**: You engage through dialogue choices, ask questions, offer guidance
1. **Advice Synthesis**: The session ends with your core recommendation
1. **Agent Processing**: Between sessions, the agent simulates outcomes and prepares the next encounter

### Progression

- Start with 2-3 clients, unlock more as your reputation grows
- Clients can terminate therapy if repeatedly dissatisfied
- Successful outcomes lead to referrals (new clients)
- Build specialization based on which relationship issues you handle well
- Track overall success rate and therapeutic approach (empathetic vs. direct, traditional vs. unconventional)

### Personal Life (Stretch Goal)

- Occasional dating scenarios with 1-2 potential partners between client sessions
- Your romantic choices can contradict your professional advice, affecting your confidence and energy
- Dates might ask about your work, creating moments where you reflect on your own advice
- Lighter interaction system than client sessions - more focused on flavor and thematic contrast

## Features

### Core Features

- **3-5 distinct recurring clients** with persistent memory across multiple sessions
- **Reddit-sourced relationship dilemmas** provide authentic, varied initial scenarios
- **Dynamic outcome simulation** where the agent determines consequences of your advice
- **Evolving therapeutic relationships** - clients grow to trust you more or less based on your guidance
- **Session history system** - detailed notes on every interaction, accessible during future sessions
- **Multiple therapeutic approaches** - the game recognizes and tracks whether you lean empathetic, solution-focused, confrontational, etc.

### Stretch Features

- **Personal dating subplot** with 1-2 romantic interests
- **Cross-contamination** between professional advice and personal choices
- **Reputation system** affecting which clients seek you out
- **Ethical dilemmas** when clients’ situations challenge your values
- **Client termination scenarios** when relationships break down beyond repair

## Technical Stack

### Platform

- **macOS desktop application** built with Electron or Swift/SwiftUI (TBD based on development progress)
- Native macOS look and feel with menu bar, notifications for “appointments”

### UI Design

- **Session view**: Clean therapy office aesthetic - client profile on left, dialogue in center, session notes on right
- **Client roster**: Overview of all clients, their current status, upcoming appointments
- **History browser**: Searchable archive of past sessions
- Text-based interface (no character portraits to avoid AI-generated art concerns)

### Backend & Agent

- **LLM Integration**: Claude API for agent decision-making and dialogue generation
- **State Management**: Local persistence for all client data, session history, and game progress

### MCP Tools

1. **Reddit Content Fetcher**

- Scrapes r/relationship_advice, r/relationships, r/AmITheAsshole for initial client scenarios
- Filters for appropriate content (avoid extreme abuse, violence)
- Tags posts by relationship type (romantic, family, friendship) and severity
- Caches posts locally to avoid repeated API calls

1. **Client Database Manager**

- Stores comprehensive client profiles: demographics, relationship history, personality traits
- Tracks therapeutic relationship metrics: trust level, session count, satisfaction
- Maintains advice history: what guidance was given, what outcomes occurred
- Records client preferences and sensitivities learned over time
- Supports queries like “get_client_history()” and “update_trust_level()”

1. **Session Memory System**

- Searchable archive of all dialogue from every session
- Vector database (ChromaDB or similar) for semantic search of past conversations
- Enables queries like “what did Sarah say about communication in our third session?”
- Allows agent to reference specific past moments naturally
- Tags sessions by themes, emotions, breakthrough moments

1. **Outcome Simulator (Agent-Driven)**

- Not a traditional API but a structured MCP tool interface for the agent
- Agent evaluates advice quality against relationship science principles
- Simulates realistic outcomes with appropriate randomness (good advice can still fail, bad advice might accidentally work)
- Generates follow-up scenarios based on outcomes
- Determines if clients return, terminate therapy, or refer others

### Additional Tools (Potential)

1. **Calendar/Scheduling System** - Manages appointment timing, sends notifications
1. **Sentiment Analyzer** - Tracks emotional tone of sessions, client distress levels

## Development Approach

Given the ambitious scope, development will leverage AI coding assistants (GitHub Copilot, Claude Code, or Cursor) to accelerate implementation, particularly for:

- UI scaffolding and macOS-specific features
- MCP tool integration and API handling
- State management and data persistence
- Reddit API integration and content filtering

### Phased Development

**Phase 1: Core Therapy Simulator (MVP)**

- Basic UI with session view and client roster
- Reddit API integration for initial scenarios
- 2-3 clients with simple state tracking
- Agent generates basic outcomes
- Session memory stored in simple JSON

**Phase 2: Enhanced Memory & Continuity**

- Implement vector database for semantic session search
- Add comprehensive client database
- Agent references past sessions naturally in dialogue
- Trust/satisfaction metrics affect client behavior

**Phase 3: Depth & Variety**

- Expand to 5 clients
- More sophisticated outcome simulation
- Client termination and referral mechanics
- Multiple therapeutic approaches recognized

**Phase 4: Stretch Goals (Time Permitting)**

- Personal dating subplot (1-2 characters)
- Cross-contamination between professional and personal
- Polish and additional content

## Success Metrics

The project successfully demonstrates agentic AI capabilities if:

- Clients feel like they have genuine memory and continuity across sessions
- Outcomes feel causally related to advice quality (not random)
- The therapeutic relationships evolve in believable ways
- Players face meaningful choices where different approaches yield different results
- The memory system enables natural callbacks to past conversations

## Why This Project Works

**Demonstrates Agentic Capabilities:**

- Agent makes autonomous decisions (outcome simulation) rather than just responding
- Complex state management across multiple relationship threads
- Sophisticated memory requirements (semantic search, context-aware responses)
- Emergent narrative from agent decisions combined with player choices

**Technically Ambitious:**

- Integration with external API (Reddit)
- Multiple MCP tools with distinct purposes
- Persistent state and long-term memory
- Native desktop application

**Thematically Cohesive:**

- The “relationship coach” framing naturally justifies the agent architecture
- Memory is central to the experience (therapists must remember clients)
- Explores interesting questions about advice, expertise, and personal vs. professional life

-----

## Repository Structure (Planned)

```
/src
  /ui          # macOS desktop app interface
  /agent       # LLM agent logic and prompt templates
  /mcp_tools   # Individual MCP tool implementations
  /data        # Client database, session archives
/tests         # Unit tests for tools and agent logic
/docs          # Additional documentation
README.md      # This file
```

## Getting Started (Post-Development)

Instructions for running the application will be added as development progresses.​​​​​​​​​​​​​​​​
