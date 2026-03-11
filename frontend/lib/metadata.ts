import type { Metadata } from "next";

import { absoluteUrl, siteConfig } from "@/lib/site-config";

type MetadataOptions = {
  title?: string;
  description?: string;
  path?: string;
  ogImage?: string;
};

export function createMetadata({
  title,
  description = siteConfig.description,
  path = "/",
  ogImage = "/opengraph-image",
}: MetadataOptions = {}): Metadata {
  const fullTitle = title ? `${title} | ${siteConfig.name}` : siteConfig.name;
  const canonical = absoluteUrl(path);
  const imageUrl = absoluteUrl(ogImage);

  return {
    title,
    description,
    alternates: {
      canonical,
    },
    openGraph: {
      title: fullTitle,
      description,
      type: "website",
      url: canonical,
      siteName: siteConfig.name,
      locale: "en_US",
      images: [
        {
          url: imageUrl,
          width: 1200,
          height: 630,
          alt: fullTitle,
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title: fullTitle,
      description,
      images: [imageUrl],
    },
  };
}
