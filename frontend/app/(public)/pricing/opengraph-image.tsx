import { createOgImage } from "@/lib/opengraph";

export const dynamic = "force-static";
export const alt = "Scivly pricing";
export const size = {
  width: 1200,
  height: 630,
};
export const contentType = "image/png";

export default function PricingOpenGraphImage() {
  return createOgImage({
    eyebrow: "Pricing",
    title: "Plans for solo researchers, teams, and enterprise operators.",
    body: "Scivly pricing is structured around validation, shared delivery, and governance-ready paper workflows.",
    accent: "#f97316",
  });
}
