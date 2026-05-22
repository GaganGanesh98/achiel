import type { MetadataRoute } from "next";

const BASE = "http://localhost:3000";

export default function sitemap(): MetadataRoute.Sitemap {
  const paths = [
    "/",
    "/dashboard",
    "/universities",
    "/current-affairs",
    "/privacy",
    "/terms",
    "/community-guidelines",
    "/impressum",
    "/login",
    "/register",
  ];

  return paths.map((path) => ({
    url: `${BASE}${path}`,
    lastModified: new Date("2026-05-22"),
  }));
}
