import * as React from "react";
import { Send, Sparkles } from "lucide-react";
import toast from "react-hot-toast";

import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { cn } from "@/utils/cn";
import { grantApi } from "@/services/grantApi";

type Msg = { role: "user" | "assistant"; content: string; time: string; error?: boolean };

const seed: Msg[] = [
  {
    role: "assistant",
    content:
      "Tell me about your startup (sector, incorporation date, location, revenue stage). I’ll shortlist grants and explain eligibility in plain language.",
    time: "Now"
  }
];

export function ChatPage() {
  const [messages, setMessages] = React.useState<Msg[]>(seed);
  const [value, setValue] = React.useState("");
  const [isSending, setIsSending] = React.useState(false);
  const [sessionId, setSessionId] = React.useState<string | null>(null);
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null);
  const [retryMessage, setRetryMessage] = React.useState<string | null>(null);

  const sendMessage = React.useCallback(async (message: string) => {
    setErrorMessage(null);
    setRetryMessage(null);
    setMessages((prev) => [...prev, { role: "user", content: message, time: "Now" }]);
    setIsSending(true);

    try {
      const response = await grantApi.chatTurn({ session_id: sessionId, message });
      setSessionId(response.session_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.reply, time: "Now" }
      ]);
      toast.success("Message sent");
    } catch (error) {
      const detail = error instanceof Error ? error.message : "Unable to reach the chat service.";
      setErrorMessage(detail);
      setRetryMessage(message);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `I couldn't reach the chat service. ${detail}`,
          time: "Now",
          error: true
        }
      ]);
      toast.error(detail);
    } finally {
      setIsSending(false);
    }
  }, [sessionId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || isSending) return;

    setValue("");
    await sendMessage(trimmed);
  };

  return (
    <div className="grid gap-4 lg:grid-cols-[1fr_340px]">
      <Card className="flex min-h-[72vh] flex-col overflow-hidden">
        <div className="flex items-center justify-between border-b border-slate-200/80 px-5 py-4 dark:border-slate-800">
          <div>
            <div className="text-sm font-semibold tracking-tight text-slate-900 dark:text-slate-50">Grant Agent Chat</div>
            <div className="mt-1 text-xs text-slate-600 dark:text-slate-400">
              Connected to the live backend chat endpoint.
            </div>
          </div>
          <div className="rounded-full bg-[var(--accent)]/15 px-3 py-1 text-xs font-semibold text-[var(--text-primary)] ring-1 ring-[var(--accent)]/30">
            Grounded mode
          </div>
        </div>

        <div className="flex-1 space-y-3 overflow-auto px-5 py-4">
          {messages.map((m, i) => (
            <Message key={`${m.role}-${i}`} msg={m} />
          ))}
          {isSending ? (
            <div className="flex justify-start">
              <div className="max-w-[78%] rounded-[20px] bg-slate-50 px-4 py-3 text-sm leading-relaxed text-slate-700 shadow-sm ring-1 ring-slate-200 dark:bg-slate-800/80 dark:text-slate-100 dark:ring-slate-700">
                Thinking…
              </div>
            </div>
          ) : null}
        </div>

        <div className="border-t border-slate-200/80 p-4 dark:border-slate-800">
          <form className="flex items-center gap-2" onSubmit={handleSubmit}>
            <div className="flex flex-1 items-center gap-2 rounded-[20px] border border-[var(--border)] bg-[var(--input-bg)] px-3 py-2 shadow-sm focus-within:ring-2 focus-within:ring-[var(--accent)]/40">
              <Sparkles className="size-4 text-[var(--text-muted)]" />
              <input
                className={cn(
                  "h-9 w-full bg-transparent text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:outline-none",
                  "focus:outline-none"
                )}
                placeholder="Ask about grants, eligibility, documents, proposal sections…"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                disabled={isSending}
              />
            </div>
            <Button type="submit" className="shrink-0" isLoading={isSending} disabled={isSending}>
              Send <Send className="size-4" />
            </Button>
          </form>
          {errorMessage ? (
            <div className="mt-3 rounded-[20px] border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700 dark:border-rose-900/40 dark:bg-rose-950/20 dark:text-rose-200">
              <div>{errorMessage}</div>
              {retryMessage ? (
                <button
                  className="mt-2 text-xs font-semibold text-rose-700 underline underline-offset-2 dark:text-rose-200"
                  onClick={() => {
                    void sendMessage(retryMessage);
                  }}
                  type="button"
                >
                  Retry last message
                </button>
              ) : null}
            </div>
          ) : null}
          <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
            Tip: Ask “What grants fit an AI healthcare startup in Bengaluru incorporated in 2024?”
          </div>
        </div>
      </Card>

      <div className="space-y-4">
        <Card className="p-5">
          <div className="text-sm font-semibold tracking-tight text-slate-900 dark:text-slate-50">Suggested prompts</div>
          <div className="mt-3 space-y-2">
            <PromptChip text="Check eligibility for MSME innovation grants." />
            <PromptChip text="List documents needed for DST seed support." />
            <PromptChip text="Draft a problem statement aligned to the grant." />
          </div>
        </Card>

        <Card className="p-5">
          <div className="text-sm font-semibold tracking-tight text-slate-900 dark:text-slate-50">Citations (preview)</div>
          <div className="mt-2 text-xs text-slate-600 dark:text-slate-400">
            Sources will appear here when the backend returns them.
          </div>
          <div className="mt-4 space-y-2">
            <Citation title="Startup India Scheme Guidelines" meta="PDF · Ministry source · Page 6" />
            <Citation title="DST Seed Support Terms" meta="Web · Official portal · Clause 4.2" />
          </div>
        </Card>
      </div>
    </div>
  );
}

function Message({ msg }: { msg: Msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[78%] rounded-[20px] px-4 py-3 text-sm leading-relaxed shadow-sm",
          isUser
            ? "bg-[var(--btn-primary-bg)] text-[var(--btn-primary-text)] rounded-br-sm"
            : msg.error
              ? "bg-rose-50 text-rose-700 ring-1 ring-rose-200 dark:bg-rose-950/20 dark:text-rose-200 dark:ring-rose-900/40"
              : "bg-[var(--surface-section)] text-[var(--text-secondary)] ring-1 ring-[var(--border)] rounded-bl-sm"
        )}
      >
        <div className="whitespace-pre-wrap">{msg.content}</div>
        <div className="mt-2 text-[11px] text-[var(--text-muted)] opacity-80">{msg.time}</div>
      </div>
    </div>
  );
}

function PromptChip({ text }: { text: string }) {
  return (
    <button type="button" className="w-full rounded-[16px] bg-[var(--surface-section)] px-3 py-2 text-left text-xs text-[var(--text-secondary)] ring-1 ring-[var(--border)] transition hover:bg-[var(--hover)]">
      {text}
    </button>
  );
}

function Citation({ title, meta }: { title: string; meta: string }) {
  return (
    <div className="rounded-[16px] bg-[var(--surface-section)] p-3 ring-1 ring-[var(--border)]">
      <div className="text-xs font-semibold text-[var(--text-primary)]">{title}</div>
      <div className="mt-1 text-[11px] text-[var(--text-muted)]">{meta}</div>
    </div>
  );
}

