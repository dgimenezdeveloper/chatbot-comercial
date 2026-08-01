import FacebookIcon from "@/components/icons/facebook";
import TwitterIcon from "@/components/icons/twitter";
import LinkedinIcon from "@/components/icons/linkedin";

const SOCIAL_LINKS = [
  { href: "#", label: "Facebook", icon: FacebookIcon },
  { href: "#", label: "Twitter", icon: TwitterIcon },
  { href: "#", label: "LinkedIn", icon: LinkedinIcon },
];

const LEGAL_LINKS = [
  { href: "#", label: "Información legal" },
  { href: "#", label: "Política de privacidad" },
];

export default function Footer() {
  return (
    <footer className="w-full bg-footer text-footer-foreground py-10 h-58 px-6">
      <div className="mx-auto max-w-4xl flex flex-col items-center gap-4">
        {/* Divider with social icons */}
        <div className="flex w-full items-center gap-30">
          <span className="h-0.5 flex-1 bg-white" />
          <nav aria-label="Redes sociales" className="flex items-center gap-5">
            {SOCIAL_LINKS.map(({ href, label, icon: Icon }) => (
              <a
                key={label}
                href={href}
                aria-label={label}
                className="w-5 h-5 text-white/90 hover:text-white transition-colors"
              >
                <Icon className="w-full h-full" />
              </a>
            ))}
          </nav>
          <span className="h-0.5 flex-1 bg-white" />
        </div>

        {/* Brand */}
        <p className="text-lg font-bold tracking-wide uppercase">
          PYMIO
        </p>

        {/* Legal links */}
        <nav aria-label="Enlaces legales" className="flex items-center gap-3 text-sm text-white/80">
          {LEGAL_LINKS.map(({ href, label }, i) => (
            <span key={label} className="flex items-center gap-3">
              {i > 0 && (
                <span className="h-4 w-px bg-white/50" aria-hidden="true" />
              )}
              <a href={href} className="hover:text-white transition-colors">
                {label}
              </a>
            </span>
          ))}
        </nav>
      </div>
    </footer>
  );
}
