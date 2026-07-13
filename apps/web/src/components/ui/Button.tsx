import * as React from "react";
import { cn } from "@/utils/cn";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md" | "lg";

export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  size?: Size;
  isLoading?: boolean;
};

const base =
  "inline-flex items-center justify-center gap-2 rounded-2xl font-semibold transition-all duration-200 " +
  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#5BA8A0]/60 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-slate-950 " +
  "disabled:opacity-50 disabled:pointer-events-none";

const variants: Record<Variant, string> = {
  primary:
    "bg-[var(--btn-primary-bg)] text-[var(--btn-primary-text)] shadow-[0_10px_30px_rgba(0,0,0,0.08)] " +
    "hover:-translate-y-0.5 hover:opacity-90 active:translate-y-0",
  secondary:
    "bg-[var(--btn-secondary-bg)] text-[var(--btn-secondary-text)] ring-1 ring-[var(--btn-secondary-border)] hover:bg-[var(--btn-secondary-hover)] shadow-sm active:translate-y-0 hover:-translate-y-0.5",
  ghost:
    "bg-transparent text-[var(--text-secondary)] hover:bg-[var(--hover)] ring-1 ring-transparent hover:ring-[var(--border)]",
  danger:
    "bg-rose-500 text-white shadow-[0_10px_30px_rgba(244,63,94,0.2)] hover:-translate-y-0.5 hover:bg-rose-600"
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-3 text-sm",
  md: "h-11 px-4 text-sm",
  lg: "h-12 px-5 text-base"
};

function Spinner() {
  return (
    <span
      aria-hidden="true"
      className="inline-block size-4 animate-spin rounded-full border-2 border-white/30 border-t-white"
    />
  );
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(base, variants[variant], sizes[size], className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? <Spinner /> : null}
        <span>{children}</span>
      </button>
    );
  }
);
Button.displayName = "Button";

