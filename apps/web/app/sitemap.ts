import type { MetadataRoute } from "next";

const BASE = "https://spyfyprod.vercel.app";

export default function sitemap(): MetadataRoute.Sitemap {
  const routes = [
    "",
    "/app",
    "/app/feed",
    "/app/analytics",
    "/app/library",
    "/app/alerts",
    "/app/settings",
    "/app/compare",
    "/app/offer/ofr_123",
    "/app/offer/ofr_204",
    "/app/offer/ofr_318",
    "/app/offer/ofr_441",
    "/app/offer/ofr_512",
    "/app/offer/ofr_607",
  ];

  return routes.map((r) => ({
    url: BASE + r,
    lastModified: new Date(),
    changeFrequency: "weekly" as const,
    priority: r === "" ? 1 : 0.7,
  }));
}
