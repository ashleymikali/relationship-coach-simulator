"use client";

import { useEffect, useMemo, useState } from "react";
import { useSSEStream } from "./useSSEStream";

type Status = "Ready" | "Streaming…" | "Done" | "Error";

type User = {
    user_id: string;
    display_name: string;
    bio: string;
    traits: string[];
    boundaries: string[];
};

type DateExchangeResponse = {
    scene: string;
    transcript: Array<{ speaker: string; name: string; text: string }>;
    evaluator_notes: string[];
};

export default function Home() {
    const [userInput, setUserInput] = useState("");
    const { transcript, status, startStream, clearTranscript, addMessage } = useSSEStream();

    const [users, setUsers] = useState<User[]>([]);
    const [intakeUserId, setIntakeUserId] = useState("");
    const [userAId, setUserAId] = useState("");
    const [userBId, setUserBId] = useState("");

    const [intakeLoading, setIntakeLoading] = useState(false);
    const [dateLoading, setDateLoading] = useState(false);
    const [reportLoading, setReportLoading] = useState(false);

    // Live intake state
    const [liveIntakeUserId, setLiveIntakeUserId] = useState("");
    const [liveSessionId, setLiveSessionId] = useState<string | null>(null);
    const [currentQuestion, setCurrentQuestion] = useState("");
    const [currentAnswer, setCurrentAnswer] = useState("");
    const [questionIndex, setQuestionIndex] = useState(0);
    const [liveIntakeLoading, setLiveIntakeLoading] = useState(false);

    const apiUrl = useMemo(() => "http://localhost:8000/api/chat/stream", []);
    const isStreaming = status === "Streaming…";

    const statusDotClass =
        status === "Ready"
            ? "text-green-400"
            : status === "Streaming…"
                ? "text-yellow-400"
                : status === "Done"
                    ? "text-green-400"
                    : "text-red-400";

    // Fetch demo users on mount
    useEffect(() => {
        fetch("http://localhost:8000/api/users")
            .then((res) => res.json())
            .then((data) => {
                setUsers(data.users || []);
                if (data.users && data.users.length > 0) {
                    setIntakeUserId(data.users[0].user_id);
                    setLiveIntakeUserId(data.users[0].user_id);
                    setUserAId(data.users[0].user_id);
                    if (data.users.length > 1) setUserBId(data.users[1].user_id);
                }
            })
            .catch((err) => console.error("Failed to fetch users:", err));
    }, []);

    function formatDateExchange(userA: string, userB: string, payload: DateExchangeResponse) {
        const t = payload.transcript
            .map((x, i) => `${i + 1}. ${x.name}: ${x.text}`)
            .join("\n\n");

        const notes = (payload.evaluator_notes || [])
            .map((n, i) => `${i + 1}. ${n}`)
            .join("\n");

        return `DATE EXCHANGE: ${userA} × ${userB}

SCENE:
${payload.scene}

TRANSCRIPT:
${t}

EVALUATOR NOTES:
${notes}`;
    }

    async function handleStart() {
        const text =
            userInput.trim() ||
            "Explain what this agentic matchmaking demo does, in 5-8 sentences.";
        await startStream(text, apiUrl);
    }

    async function handleStartLiveIntake() {
        if (!liveIntakeUserId) return;

        setLiveIntakeLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/intake/live/start/${liveIntakeUserId}`, {
                method: "POST",
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();
            setLiveSessionId(data.session_id);
            setCurrentQuestion(data.question);
            setQuestionIndex(data.step_index);
            setCurrentAnswer("");
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : "Unknown error";
            addMessage("error", `Failed to start live intake: ${errorMsg}`);
        } finally {
            setLiveIntakeLoading(false);
        }
    }

    async function handleSubmitLiveAnswer() {
        if (!liveSessionId || !currentAnswer.trim()) return;

        setLiveIntakeLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/intake/live/answer/${liveSessionId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ answer_text: currentAnswer }),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();

            if (data.is_complete && data.final_summary) {
                // Format and display final summary
                const summary = data.final_summary;
                const formattedText = `LIVE INTAKE SUMMARY for ${liveIntakeUserId}:

PREFERENCES:
${(summary.preferences || []).map((p: string, i: number) => `${i + 1}. ${p}`).join("\n")}

DEALBREAKERS:
${(summary.dealbreakers || []).map((d: string, i: number) => `${i + 1}. ${d}`).join("\n")}

DATING THESIS:
${summary.dating_thesis || ""}`;

                addMessage("system", formattedText);

                // Reset live intake state
                setLiveSessionId(null);
                setCurrentQuestion("");
                setCurrentAnswer("");
                setQuestionIndex(0);
            } else {
                // Next question
                setCurrentQuestion(data.question || "");
                setQuestionIndex(data.step_index);
                setCurrentAnswer("");
            }
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : "Unknown error";
            addMessage("error", `Failed to submit answer: ${errorMsg}`);
        } finally {
            setLiveIntakeLoading(false);
        }
    }

    async function handleRunIntake() {
        if (!intakeUserId) return;

        setIntakeLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/intake/${intakeUserId}`, {
                method: "POST",
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();
            const summary = data.summary;

            const formattedText = `INTAKE SUMMARY for ${intakeUserId}:

PREFERENCES:
${(summary.preferences || []).map((p: string, i: number) => `${i + 1}. ${p}`).join("\n")}

DEALBREAKERS:
${(summary.dealbreakers || []).map((d: string, i: number) => `${i + 1}. ${d}`).join("\n")}

DATING THESIS:
${summary.dating_thesis || ""}`;

            addMessage("system", formattedText);
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : "Unknown error";
            addMessage("error", `Intake failed: ${errorMsg}`);
        } finally {
            setIntakeLoading(false);
        }
    }

    async function handleRunDateExchange() {
        if (!userAId || !userBId) return;

        setDateLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/date/exchange/${userAId}/${userBId}`, {
                method: "POST",
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = (await res.json()) as DateExchangeResponse;
            addMessage("system", formatDateExchange(userAId, userBId, data));
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : "Unknown error";
            addMessage("error", `Date exchange failed: ${errorMsg}`);
        } finally {
            setDateLoading(false);
        }
    }

    async function handleGenerateReport() {
        if (!userAId || !userBId) return;

        setReportLoading(true);
        try {
            const res = await fetch(`http://localhost:8000/api/report/${userAId}/${userBId}`, {
                method: "POST",
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();
            const report = data.report;

            addMessage("system", `MATCH REPORT: ${userAId} × ${userBId}\n\n${report}`);
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : "Unknown error";
            addMessage("error", `Report generation failed: ${errorMsg}`);
        } finally {
            setReportLoading(false);
        }
    }

    return (
        <div className="flex h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            {/* Left Panel - Controls */}
            <div className="w-96 border-r border-purple-500/30 bg-slate-900/50 backdrop-blur-sm p-6 flex flex-col overflow-y-auto">
                <div className="mb-6">
                    <h1 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400 mb-2">
                        Hang the DJ
                    </h1>
                    <p className="text-sm text-slate-400">Agentic Matchmaking Demo</p>
                </div>

                <div className="flex-1 flex flex-col gap-4">
                    {/* Live Intake Interview */}
                    <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <h3 className="text-sm font-semibold text-slate-300 mb-3">Live Intake Interview</h3>

                        {!liveSessionId ? (
                            <>
                                <label className="block text-xs text-slate-400 mb-1">Select User</label>
                                <select
                                    value={liveIntakeUserId}
                                    onChange={(e) => setLiveIntakeUserId(e.target.value)}
                                    disabled={liveIntakeLoading}
                                    className="w-full px-3 py-2 mb-3 bg-slate-800/50 border border-purple-500/30 rounded text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 disabled:opacity-50"
                                >
                                    {users.map((u) => (
                                        <option key={u.user_id} value={u.user_id}>
                                            {u.user_id} - {u.display_name}
                                        </option>
                                    ))}
                                </select>

                                <button
                                    onClick={handleStartLiveIntake}
                                    disabled={liveIntakeLoading || !liveIntakeUserId}
                                    className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {liveIntakeLoading ? "Starting..." : "Start Live Intake"}
                                </button>
                            </>
                        ) : (
                            <>
                                <div className="mb-3">
                                    <div className="text-xs text-slate-400 mb-2">
                                        Question {questionIndex + 1} / 5
                                    </div>
                                    <div className="p-3 bg-slate-900/50 border border-purple-500/30 rounded text-sm text-slate-200">
                                        {currentQuestion}
                                    </div>
                                </div>

                                <label className="block text-xs text-slate-400 mb-1">Your Answer</label>
                                <textarea
                                    value={currentAnswer}
                                    onChange={(e) => setCurrentAnswer(e.target.value)}
                                    disabled={liveIntakeLoading}
                                    rows={3}
                                    className="w-full px-3 py-2 mb-3 bg-slate-800/50 border border-purple-500/30 rounded text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 disabled:opacity-50 resize-none"
                                    placeholder="Type your answer here..."
                                />

                                <button
                                    onClick={handleSubmitLiveAnswer}
                                    disabled={liveIntakeLoading || !currentAnswer.trim()}
                                    className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {liveIntakeLoading ? "Submitting..." : "Submit Answer"}
                                </button>
                            </>
                        )}
                    </div>

                    {/* Intake Controls */}
                    <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <h3 className="text-sm font-semibold text-slate-300 mb-3">1. Run Intake</h3>

                        <label className="block text-xs text-slate-400 mb-1">Intake User</label>
                        <select
                            value={intakeUserId}
                            onChange={(e) => setIntakeUserId(e.target.value)}
                            disabled={intakeLoading}
                            className="w-full px-3 py-2 mb-3 bg-slate-800/50 border border-purple-500/30 rounded text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 disabled:opacity-50"
                        >
                            {users.map((u) => (
                                <option key={u.user_id} value={u.user_id}>
                                    {u.user_id} - {u.display_name}
                                </option>
                            ))}
                        </select>

                        <button
                            onClick={handleRunIntake}
                            disabled={intakeLoading || !intakeUserId}
                            className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {intakeLoading ? "Running..." : "Run Intake"}
                        </button>
                    </div>

                    {/* Pair Selection (shared) */}
                    <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <h3 className="text-sm font-semibold text-slate-300 mb-3">2. Choose Pair</h3>

                        <label className="block text-xs text-slate-400 mb-1">User A</label>
                        <select
                            value={userAId}
                            onChange={(e) => setUserAId(e.target.value)}
                            disabled={dateLoading || reportLoading}
                            className="w-full px-3 py-2 mb-2 bg-slate-800/50 border border-purple-500/30 rounded text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 disabled:opacity-50"
                        >
                            {users.map((u) => (
                                <option key={u.user_id} value={u.user_id}>
                                    {u.user_id} - {u.display_name}
                                </option>
                            ))}
                        </select>

                        <label className="block text-xs text-slate-400 mb-1">User B</label>
                        <select
                            value={userBId}
                            onChange={(e) => setUserBId(e.target.value)}
                            disabled={dateLoading || reportLoading}
                            className="w-full px-3 py-2 mb-3 bg-slate-800/50 border border-purple-500/30 rounded text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 disabled:opacity-50"
                        >
                            {users.map((u) => (
                                <option key={u.user_id} value={u.user_id}>
                                    {u.user_id} - {u.display_name}
                                </option>
                            ))}
                        </select>

                        <div className="flex gap-2">
                            <button
                                onClick={handleRunDateExchange}
                                disabled={dateLoading || !userAId || !userBId}
                                className="flex-1 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {dateLoading ? "Simulating..." : "Run Date Exchange"}
                            </button>

                            <button
                                onClick={handleGenerateReport}
                                disabled={reportLoading || !userAId || !userBId}
                                className="flex-1 px-4 py-2 bg-pink-600 hover:bg-pink-500 text-white text-sm font-medium rounded transition disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {reportLoading ? "Generating..." : "Match Report"}
                            </button>
                        </div>
                    </div>

                    {/* SSE Stream Controls */}
                    <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <h3 className="text-sm font-semibold text-slate-300 mb-3">3. Agent #3 Stream</h3>

                        <label className="block text-xs text-slate-400 mb-1">Prompt</label>
                        <textarea
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            placeholder="Type a prompt for Agent #3..."
                            className="w-full h-20 px-3 py-2 mb-3 bg-slate-800/50 border border-purple-500/30 rounded text-slate-200 text-sm placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50 resize-none"
                            disabled={isStreaming}
                        />

                        <div className="flex gap-2">
                            <button
                                onClick={handleStart}
                                disabled={isStreaming}
                                className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white text-sm font-medium rounded transition shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {isStreaming ? "Streaming…" : "Start Stream"}
                            </button>

                            <button
                                onClick={clearTranscript}
                                disabled={isStreaming || transcript.length === 0}
                                className="px-4 py-2 rounded border border-slate-700/70 bg-slate-900/30 text-slate-200 text-sm hover:bg-slate-900/50 transition disabled:opacity-50 disabled:cursor-not-allowed"
                                title="Clear transcript"
                            >
                                Clear
                            </button>
                        </div>
                    </div>

                    {/* Status */}
                    <div className="p-3 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <div className="space-y-1 text-xs text-slate-400">
                            <div className="flex items-center justify-between">
                                <span>Status:</span>
                                <span className={statusDotClass}>● {status as Status}</span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span>Users:</span>
                                <span className="text-slate-500">{users.length}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Center Panel - Transcript */}
            <div className="flex-1 flex flex-col bg-slate-900/30 backdrop-blur-sm">
                <div className="border-b border-purple-500/30 px-6 py-4">
                    <h2 className="text-lg font-semibold text-slate-200">Live Transcript</h2>
                    <p className="text-sm text-slate-500">Agent outputs and system messages</p>
                </div>

                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {transcript.length === 0 ? (
                        <div className="flex items-center justify-center h-full">
                            <p className="text-slate-500 text-center">
                                No messages yet.
                                <br />
                                <span className="text-sm">Run intake, simulate a date, generate report, or stream.</span>
                            </p>
                        </div>
                    ) : (
                        transcript.map((msg, idx) => (
                            <div
                                key={idx}
                                className={`p-4 rounded-lg border ${msg.speaker === "user"
                                    ? "bg-blue-900/20 border-blue-500/30"
                                    : msg.speaker === "agent#3"
                                        ? "bg-purple-900/20 border-purple-500/30"
                                        : msg.speaker === "error"
                                            ? "bg-red-900/20 border-red-500/30"
                                            : "bg-slate-800/30 border-slate-700/50"
                                    }`}
                            >
                                <div className="flex items-center gap-2 mb-2">
                                    <span
                                        className={`text-xs font-semibold uppercase tracking-wide ${msg.speaker === "user"
                                            ? "text-blue-400"
                                            : msg.speaker === "agent#3"
                                                ? "text-purple-400"
                                                : msg.speaker === "error"
                                                    ? "text-red-400"
                                                    : "text-slate-400"
                                            }`}
                                    >
                                        {msg.speaker}
                                    </span>
                                    <span className="text-xs text-slate-500">
                                        {new Date(msg.timestamp).toLocaleTimeString()}
                                    </span>
                                </div>
                                <p className="text-slate-200 leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Right Panel - State / Explanation */}
            <div className="w-96 border-l border-purple-500/30 bg-slate-900/50 backdrop-blur-sm p-6 flex flex-col">
                <div className="mb-6">
                    <h2 className="text-lg font-semibold text-slate-200 mb-1">Agent State</h2>
                    <p className="text-sm text-slate-500">Architecture overview</p>
                </div>

                <div className="flex-1 space-y-4">
                    <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <h3 className="text-sm font-semibold text-purple-400 mb-3">Active Agents</h3>
                        <div className="space-y-2 text-sm">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                                <span className="text-slate-300">Matchmaker A</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                                <span className="text-slate-300">Matchmaker B</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                                <span className="text-slate-300">Agent #3 (Neutral Evaluator)</span>
                            </div>
                        </div>
                    </div>

                    <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <h3 className="text-sm font-semibold text-purple-400 mb-3">Demo Users</h3>
                        <div className="space-y-2 text-xs text-slate-400">
                            {users.map((u) => (
                                <div key={u.user_id} className="pb-2 border-b border-slate-700/30 last:border-0">
                                    <div className="font-semibold text-slate-300">{u.display_name}</div>
                                    <div className="text-slate-500 mt-1">{u.user_id}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="p-4 bg-slate-800/30 rounded-lg border border-slate-700/50">
                        <h3 className="text-sm font-semibold text-purple-400 mb-3">Workflow</h3>
                        <div className="text-xs text-slate-400 space-y-1">
                            <div>1. Run intake (profile-based or live)</div>
                            <div>2. Run date exchange (6 turns)</div>
                            <div>3. Generate match report (cites a quote)</div>
                            <div>4. Ask Agent #3 questions (stream)</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
