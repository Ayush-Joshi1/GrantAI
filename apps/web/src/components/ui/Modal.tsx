import * as React from "react";
import { createPortal } from "react-dom";
import { cn } from "@/utils/cn";

export type ModalProps = {
  open: boolean;
  title: string;
  description?: string;
  onClose: () => void;
  children: React.ReactNode;
  footer?: React.ReactNode;
};

export function Modal({ open, title, description, onClose, children, footer }: ModalProps) {
  React.useEffect(() => {
    if (!open) return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return createPortal(
    <div className="fixed inset-0 z-50">
      <div
        className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      <div className="relative mx-auto flex h-full max-w-xl items-center px-4">
        <div
          role="dialog"
          aria-modal="true"
          aria-label={title}
          className={cn(
            "w-full rounded-[24px] border border-slate-200/80 bg-white/95 shadow-[0_22px_80px_rgba(15,23,42,0.16)] backdrop-blur-sm dark:border-[#4b5563] dark:bg-[#2f3645]"
          )}
        >
          <div className="px-6 pt-6">
            <h2 className="text-lg font-semibold tracking-tight text-slate-900 dark:text-[#f9fafb]">{title}</h2>
            {description ? <p className="mt-1 text-sm text-slate-600 dark:text-[#c7ced8]">{description}</p> : null}
          </div>
          <div className="px-6 py-5">{children}</div>
          {footer ? (
            <div className="flex items-center justify-end gap-2 border-t border-slate-200/80 px-6 py-4 dark:border-[#4b5563]">
              {footer}
            </div>
          ) : null}
        </div>
      </div>
    </div>,
    document.body
  );
}

