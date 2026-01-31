import { useState, useCallback } from "react";

type TranscriptMsg = {
    speaker: string;
    text: string;
    timestamp: number;
};

type Status = "Ready" | "Streaming…" | "Done" | "Error";

type ParsedEvent = {
    event: string;
    data: any;
};

export function useSSEStream() {
    const [transcript, setTranscript] = useState<TranscriptMsg[]>([]);
    const [status, setStatus] = useState<Status>("Ready");

    const clearTranscript = useCallback(() => {
        setTranscript([]);
        setStatus("Ready");
    }, []);

    const addMessage = useCallback((speaker: string, text: string) => {
        setTranscript((prev) => [...prev, { speaker, text, timestamp: Date.now() }]);
    }, []);

    const startStream = useCallback(
        async (userText: string, apiUrl: string) => {
            setStatus("Streaming…");

            // Delta merge accumulator
            let currentDeltaSpeaker: string | null = null;
            let currentDeltaText = "";

            const flushDelta = () => {
                if (currentDeltaSpeaker && currentDeltaText.length > 0) {
                    setTranscript((prev) => [
                        ...prev,
                        {
                            speaker: currentDeltaSpeaker,
                            text: currentDeltaText,
                            timestamp: Date.now(),
                        },
                    ]);
                }
                currentDeltaSpeaker = null;
                currentDeltaText = "";
            };

            const onDelta = (speaker: string, text: string) => {
                if (speaker === currentDeltaSpeaker) {
                    currentDeltaText += text;
                } else {
                    flushDelta();
                    currentDeltaSpeaker = speaker;
                    currentDeltaText = text;
                }
            };

            const onTranscript = (speaker: string, text: string) => {
                flushDelta();
                setTranscript((prev) => [...prev, { speaker, text, timestamp: Date.now() }]);
            };

            try {
                const response = await fetch(apiUrl, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "text/event-stream",
                    },
                    body: JSON.stringify({ user_text: userText }),
                });

                if (!response.ok) throw new Error(`HTTP ${response.status}`);

                const reader = response.body?.getReader();
                if (!reader) throw new Error("No response body reader available");

                const decoder = new TextDecoder("utf-8");
                let buffer = "";

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });

                    // Normalize CRLF -> LF so splitting works reliably in browsers
                    buffer = buffer.replace(/\r\n/g, "\n");

                    // SSE events end with a blank line
                    let sepIndex: number;
                    while ((sepIndex = buffer.indexOf("\n\n")) !== -1) {
                        const frame = buffer.slice(0, sepIndex);
                        buffer = buffer.slice(sepIndex + 2);

                        const evt = parseSSEFrame(frame);
                        if (!evt) continue;

                        const { event, data } = evt;

                        if (event === "meta") continue;

                        if (event === "transcript") {
                            onTranscript(data.speaker ?? "unknown", data.text ?? "");
                            continue;
                        }

                        if (event === "delta") {
                            onDelta(data.speaker ?? "agent#3", data.text ?? "");
                            continue;
                        }

                        if (event === "done") {
                            flushDelta();
                            setStatus("Done");
                            try {
                                await reader.cancel();
                            } catch { }
                            return;
                        }

                        if (event === "error") {
                            flushDelta();
                            onTranscript("error", data.error ?? "Unknown error");
                            setStatus("Error");
                            try {
                                await reader.cancel();
                            } catch { }
                            return;
                        }
                    }
                }

                // Stream ended without explicit done
                flushDelta();
                setStatus("Done");
            } catch (err) {
                setStatus("Error");
                onTranscript("system", `Error: ${err instanceof Error ? err.message : "Unknown error"}`);
            }
        },
        []
    );

    return { transcript, status, startStream, clearTranscript, addMessage };
}

function parseSSEFrame(frame: string): ParsedEvent | null {
    // Supports:
    // event: delta
    // data: {...}
    // data: {...}   (multi-line data; SSE spec allows this)
    let event = "message";
    const dataLines: string[] = [];

    const lines = frame.split("\n").map((l) => l.replace(/\r/g, ""));

    for (const line of lines) {
        if (line.startsWith("event:")) {
            event = line.slice("event:".length).trim();
            continue;
        }
        if (line.startsWith("data:")) {
            dataLines.push(line.slice("data:".length).trim());
            continue;
        }
    }

    if (dataLines.length === 0) return null;

    const dataStr = dataLines.join("\n");
    try {
        const data = JSON.parse(dataStr);
        return { event, data };
    } catch {
        // If your server ever sends plain text data, you can fall back here:
        // return { event, data: { text: dataStr } };
        return null;
    }
}