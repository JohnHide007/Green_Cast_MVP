"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const links = [
  { href: "/funds",     label: "Portfolio" },
  { href: "/screening", label: "Pre-DD Screening" },
  { href: "/roi",       label: "ROI Calculator" },
];

/** Inline leaf SVG mark — two organic curves suggesting a plant shoot */
function LeafMark({ className }: { className?: string }) {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      {/* Main leaf body */}
      <path
        d="M12 21C12 21 5 16.5 5 10C5 6.13 8.13 3 12 3C15.87 3 19 6.13 19 10C19 16.5 12 21 12 21Z"
        fill="currentColor"
        fillOpacity="0.15"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {/* Midrib */}
      <path
        d="M12 21L12 10"
        stroke="currentColor"
        strokeWidth="1.2"
        strokeLinecap="round"
      />
      {/* Left vein */}
      <path
        d="M12 14C10 13 8 11.5 8 9"
        stroke="currentColor"
        strokeWidth="0.9"
        strokeLinecap="round"
        opacity="0.7"
      />
      {/* Right vein */}
      <path
        d="M12 12C14 11 16 9.5 16 7.5"
        stroke="currentColor"
        strokeWidth="0.9"
        strokeLinecap="round"
        opacity="0.7"
      />
    </svg>
  );
}

export function Nav() {
  const pathname = usePathname();
  return (
    <header className="sticky top-0 z-50 border-b border-gc-border bg-gc-surface/95 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-screen-xl items-center justify-between px-6">
        {/* Wordmark */}
        <Link href="/" className="flex items-center gap-2 group">
          <LeafMark className="text-gc-green transition-transform group-hover:scale-110" />
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold tracking-tight text-gc-text">
              Green<span className="text-gc-green">Cast</span>
            </span>
            <span className="hidden text-xs font-medium text-gc-muted sm:inline leading-none">
              Risk Intelligence
            </span>
          </div>
        </Link>

        {/* Nav links */}
        <nav className="flex items-center gap-1">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={cn(
                "rounded px-3 py-1.5 text-sm font-medium transition-colors",
                pathname.startsWith(l.href)
                  ? "bg-gc-green/10 text-gc-green"
                  : "text-gc-text hover:bg-gc-border/50",
              )}
            >
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
