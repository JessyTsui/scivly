import { ImageResponse } from "next/og";

type OgImageOptions = {
  eyebrow: string;
  title: string;
  body: string;
  accent: string;
};

export function createOgImage({ eyebrow, title, body, accent }: OgImageOptions) {
  return new ImageResponse(
    (
      <div
        style={{
          display: "flex",
          height: "100%",
          width: "100%",
          background:
            "radial-gradient(circle at top left, rgba(56,189,248,0.18), transparent 30%), linear-gradient(135deg, #f0f9ff 0%, #ffffff 48%, #e0f2fe 100%)",
          color: "#082f49",
          fontFamily: "Georgia, serif",
          padding: "64px",
          position: "relative",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 36,
            right: 36,
            display: "flex",
            height: 180,
            width: 180,
            borderRadius: 9999,
            border: "1px solid rgba(8,47,73,0.12)",
            background: "rgba(255,255,255,0.78)",
            boxShadow: "0 28px 80px -42px rgba(8,47,73,0.45)",
          }}
        />

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
            width: "100%",
            borderRadius: 36,
            border: "1px solid rgba(8,47,73,0.08)",
            background: "rgba(255,255,255,0.84)",
            boxShadow: "0 32px 96px -50px rgba(8,47,73,0.5)",
            padding: "40px 44px",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
              }}
            >
              <div
                style={{
                  height: 26,
                  width: 26,
                  borderRadius: 9999,
                  background: accent,
                  boxShadow: `0 0 0 8px ${accent}24`,
                }}
              />
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: 4,
                }}
              >
                <div
                  style={{
                    fontSize: 20,
                    letterSpacing: "0.2em",
                    textTransform: "uppercase",
                    color: accent,
                    fontFamily: "ui-sans-serif, system-ui, sans-serif",
                    fontWeight: 700,
                  }}
                >
                  {eyebrow}
                </div>
                <div
                  style={{
                    fontSize: 24,
                    fontFamily: "ui-sans-serif, system-ui, sans-serif",
                    fontWeight: 700,
                  }}
                >
                  Scivly
                </div>
              </div>
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                borderRadius: 9999,
                padding: "12px 18px",
                background: "rgba(8,47,73,0.06)",
                fontFamily: "ui-sans-serif, system-ui, sans-serif",
                fontSize: 18,
                color: "#0c4a6e",
              }}
            >
              Public Surface
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: 860 }}>
            <div
              style={{
                fontSize: 78,
                lineHeight: 0.92,
                letterSpacing: "-0.06em",
                fontWeight: 700,
              }}
            >
              {title}
            </div>
            <div
              style={{
                fontSize: 28,
                lineHeight: 1.35,
                color: "#0c4a6e",
                fontFamily: "ui-sans-serif, system-ui, sans-serif",
              }}
            >
              {body}
            </div>
          </div>

          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              paddingTop: 18,
              borderTop: "1px solid rgba(8,47,73,0.08)",
              fontFamily: "ui-sans-serif, system-ui, sans-serif",
              fontSize: 18,
              color: "#0c4a6e",
            }}
          >
            <div>Monitor papers. Translate signal. Keep the evidence trail.</div>
            <div style={{ color: accent, fontWeight: 700 }}>scivly.dev</div>
          </div>
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    },
  );
}
