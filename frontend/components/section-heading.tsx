type SectionHeadingProps = {
  eyebrow: string;
  title: string;
  body: string;
  light?: boolean;
  align?: "left" | "center";
};

export function SectionHeading({
  eyebrow,
  title,
  body,
  light = false,
  align = "left",
}: SectionHeadingProps) {
  return (
    <div className={`max-w-2xl ${align === "center" ? "mx-auto text-center" : ""}`}>
      <p
        className={`mb-3 text-sm font-semibold uppercase tracking-wider ${
          light ? "text-white/60" : "text-[var(--primary)]"
        }`}
      >
        {eyebrow}
      </p>
      <h2
        className={`font-[family:var(--font-display)] text-3xl font-semibold tracking-tight sm:text-4xl ${
          light ? "text-white" : "text-[var(--foreground)]"
        }`}
      >
        {title}
      </h2>
      <p className={`mt-4 text-lg leading-relaxed ${light ? "text-slate-300" : "text-[var(--foreground-muted)]"}`}>
        {body}
      </p>
    </div>
  );
}
