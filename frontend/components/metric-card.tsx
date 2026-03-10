type MetricCardProps = {
  label: string;
  value: string;
  detail: string;
  trend?: "up" | "down" | "neutral";
};

export function MetricCard({ label, value, detail, trend = "neutral" }: MetricCardProps) {
  const trendColors = {
    up: "text-[var(--success)]",
    down: "text-[var(--accent)]",
    neutral: "text-[var(--primary-light)]",
  };

  return (
    <div className="card-dark p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold text-white">
        {value}
      </p>
      <p className={`mt-2 text-sm ${trendColors[trend]}`}>{detail}</p>
    </div>
  );
}
