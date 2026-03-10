export function LogoMark({ className = "" }: { className?: string }) {
  return (
    <div className={`relative h-8 w-8 shrink-0 ${className}`}>
      {/* Outer ring */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-[var(--primary)] to-[var(--primary-dark)]" />
      {/* Inner white circle */}
      <div className="absolute inset-[2px] rounded-[10px] bg-white" />
      {/* Center dot */}
      <div className="absolute left-1/2 top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-[var(--primary)]" />
      {/* Pulse ring */}
      <div className="absolute inset-0 rounded-xl ring-2 ring-[var(--primary)]/20" />
    </div>
  );
}
