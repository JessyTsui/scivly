import { createOgImage } from "@/lib/opengraph";

export const dynamic = "force-static";
export const alt = "Scivly landing page";
export const size = {
  width: 1200,
  height: 630,
};
export const contentType = "image/png";

export default function OpenGraphImage() {
  return createOgImage({
    eyebrow: "Research intelligence",
    title: "Scivly",
    body: "Monitor papers, translate signal, and keep every answer tied to source evidence.",
    accent: "#0ea5e9",
  });
}
