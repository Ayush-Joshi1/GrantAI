export function LandingBackground() {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 overflow-hidden bg-[var(--surface-secondary)]">
      <div className="absolute -top-[30%] left-1/2 h-[900px] w-[1200px] -translate-x-1/2 rounded-full bg-[radial-gradient(ellipse_at_center,rgba(247,198,74,0.15),transparent_65%)]" />
      <div className="absolute right-[-15%] top-[20%] h-[600px] w-[600px] rounded-full bg-[radial-gradient(circle,rgba(247,198,74,0.08),transparent_70%)]" />
      <div className="absolute bottom-[-10%] left-[-10%] h-[500px] w-[500px] rounded-full bg-[radial-gradient(circle,rgba(247,198,74,0.06),transparent_70%)]" />
      <div
        className="absolute inset-0 opacity-[0.2]"
        style={{
          backgroundImage:
            "linear-gradient(var(--border) 1px, transparent 1px), linear-gradient(90deg, var(--border) 1px, transparent 1px)",
          backgroundSize: "64px 64px"
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[var(--surface-secondary)]/50 to-[var(--surface-secondary)]" />
    </div>
  );
}
