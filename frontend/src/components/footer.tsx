import Link from "next/link";

const LEGAL_LINKS: { href: string; label: string; external?: boolean }[] = [
  { href: "/privacy", label: "Privacy" },
  { href: "/terms", label: "Terms" },
  { href: "/community-guidelines", label: "Community Guidelines" },
  { href: "/impressum", label: "Impressum" },
  { href: "mailto:gaganganesh098@gmail.com", label: "Contact", external: true },
];

export function Footer() {
  return (
    <footer className="mt-auto border-t bg-background">
      <div className="mx-auto max-w-5xl px-4 py-8 text-center space-y-3">
        <nav className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-sm">
          {LEGAL_LINKS.map((link, i) => (
            <span key={link.href} className="inline-flex items-center gap-3">
              {i > 0 && <span className="text-muted-foreground" aria-hidden>·</span>}
              {link.external ? (
                <a
                  href={link.href}
                  className="text-muted-foreground hover:text-foreground underline-offset-4 hover:underline"
                >
                  {link.label}
                </a>
              ) : (
                <Link
                  href={link.href}
                  className="text-muted-foreground hover:text-foreground underline-offset-4 hover:underline"
                >
                  {link.label}
                </Link>
              )}
            </span>
          ))}
        </nav>
        <p className="text-xs text-muted-foreground max-w-xl mx-auto">
          CampusVoice is an independent platform. We are not affiliated with or endorsed by
          any university.
        </p>
        <p className="text-xs text-muted-foreground">
          © 2026 {`Gagan Ganesh`}
        </p>
      </div>
    </footer>
  );
}
