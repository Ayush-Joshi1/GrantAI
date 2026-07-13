import { cn } from "@/utils/cn";

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl bg-slate-200/80 ring-1 ring-slate-200 dark:bg-[#46506a] dark:ring-[#4b5563]",
        className
      )}
    >
      <div className="pointer-events-none absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-white/60 to-transparent dark:via-white/10" />
      <div className="opacity-0">.</div>
    </div>
  );
}

