import { createOgImage } from "@/lib/opengraph";

export const dynamic = "force-static";
export const alt = "About Scivly";
export const size = {
  width: 1200,
  height: 630,
};
export const contentType = "image/png";

export default function AboutOpenGraphImage() {
  return createOgImage({
    eyebrow: "About",
    title: "A multi-surface platform for paper intelligence.",
    body: "Scivly is built around public, workspace, operator, and developer surfaces that share one architectural language.",
    accent: "#0284c7",
  });
}
