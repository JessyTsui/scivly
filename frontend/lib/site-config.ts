export const siteConfig = {
  name: "Scivly",
  description:
    "Scivly is the paper intelligence layer for teams that monitor research, translate signal, and keep every answer tied to evidence.",
  githubUrl: "https://github.com/JessyTsui/scivly",
  signupPath: "/signup",
  url: resolveSiteUrl(),
};

function resolveSiteUrl() {
  const candidate = process.env.NEXT_PUBLIC_SITE_URL;

  if (candidate && URL.canParse(candidate)) {
    return candidate;
  }

  return "http://localhost:3100";
}

export function absoluteUrl(path = "/") {
  return new URL(path, siteConfig.url).toString();
}
