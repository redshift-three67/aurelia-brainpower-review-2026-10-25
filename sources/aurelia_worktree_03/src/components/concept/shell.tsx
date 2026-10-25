import { useState } from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import * as Dialog from "@radix-ui/react-dialog";
import { Menu, X } from "lucide-react";
import { NAV } from "@/lib/concept/nav";
import { UserButton, SignedIn, SignedOut } from "@/lib/auth/gates";
import { cn } from "@/lib/utils";

function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <Link to="/" className="flex items-center gap-3 text-fg no-underline">
      <span
        className="grid size-9 place-items-center rounded-md bg-primary"
        aria-hidden
      >
        <svg viewBox="0 0 32 32" className="size-5 text-primary-fg">
          <circle cx="16" cy="16" r="8" fill="none" stroke="currentColor" strokeWidth="2" />
          <circle cx="16" cy="16" r="3" fill="currentColor" />
        </svg>
      </span>
      <span className="leading-tight">
        <span className="block font-display text-lg font-medium tracking-tight">AURELIA</span>
        {compact ? null : (
          <span className="block text-xs text-muted">Phase 1 · Gehäuse</span>
        )}
      </span>
    </Link>
  );
}

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <ul className="flex flex-col gap-0.5">
      {NAV.map((item) => {
        const active = pathname === item.href;
        return (
          <li key={item.href}>
            <Link
              to={item.href}
              onClick={onNavigate}
              aria-current={active ? "page" : undefined}
              className={cn(
                "flex items-baseline gap-3 rounded-lg px-3 py-2.5 no-underline transition-colors duration-150",
                active
                  ? "bg-primary text-primary-fg"
                  : "text-fg hover:bg-surface",
              )}
            >
              <span
                className={cn(
                  "w-6 shrink-0 font-mono text-xs tabular-nums",
                  active ? "text-primary-fg/70" : "text-subtle",
                )}
              >
                {item.chapter}
              </span>
              <span className="text-sm font-medium">{item.label}</span>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}

export function ConceptShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-dvh bg-bg">
      <a
        href="#inhalt"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-fg"
      >
        Zum Inhalt springen
      </a>

      <div className="mx-auto flex min-h-dvh max-w-7xl">
        <aside className="sticky top-0 hidden h-dvh w-64 shrink-0 flex-col border-r border-border bg-elevated/80 px-4 py-6 lg:flex">
          <BrandMark />
          <nav className="mt-8 flex-1 overflow-y-auto pr-1" aria-label="Kapitel">
            <NavLinks />
          </nav>
          <p className="px-3 pt-6 text-xs leading-relaxed text-subtle">
            Phase 1 · X akzeptiert · Kein Video · Qualität vor Menge.
          </p>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-20 flex items-center justify-between gap-3 border-b border-border bg-bg/90 px-4 py-3 backdrop-blur-sm lg:hidden">
            <BrandMark compact />
            <Dialog.Root open={open} onOpenChange={setOpen}>
              <Dialog.Trigger asChild>
                <button
                  type="button"
                  className="inline-flex size-11 items-center justify-center rounded-lg border border-border bg-elevated text-fg"
                  aria-label="Kapitel öffnen"
                >
                  <Menu className="size-5" />
                </button>
              </Dialog.Trigger>
              <Dialog.Portal>
                <Dialog.Overlay className="fixed inset-0 z-40 bg-fg/30" />
                <Dialog.Content className="fixed inset-y-0 left-0 z-50 flex w-[min(20rem,92vw)] flex-col bg-elevated p-4 shadow-soft">
                  <div className="flex items-center justify-between gap-3">
                    <Dialog.Title className="font-display text-lg">Kapitel</Dialog.Title>
                    <Dialog.Close asChild>
                      <button
                        type="button"
                        className="inline-flex size-11 items-center justify-center rounded-lg border border-border text-fg"
                        aria-label="Menü schließen"
                      >
                        <X className="size-5" />
                      </button>
                    </Dialog.Close>
                  </div>
                  <nav className="mt-4 overflow-y-auto" aria-label="Kapitel">
                    <NavLinks onNavigate={() => setOpen(false)} />
                  </nav>
                </Dialog.Content>
              </Dialog.Portal>
            </Dialog.Root>
          </header>

          <main id="inhalt" className="flex-1 px-4 py-10 sm:px-8 sm:py-14 lg:px-12">
            <div
              role="status"
              className="mb-8 box-border w-full min-w-0 max-w-full break-words rounded-lg border border-border bg-elevated px-4 py-3 text-sm whitespace-normal text-fg shadow-soft"
            >
              <p className="font-medium">Phase-1-Schale vorhanden · Produktarbeit pausiert bis G0-SRV-12</p>
              <p className="mt-1 text-muted">Nur synthetische Daten · keine Server-, CUDA-, USB- oder Art.-9-Aktivierung</p>
            </div>
            {children}
          </main>

          <footer className="border-t border-border px-4 py-6 text-sm text-muted sm:px-8 lg:px-12">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p>
                AURELIA v1.0 Gehäuse · 24. August 2026 · Kein Medizinprodukt · Keine
                Diagnose- oder Heilversprechen.
              </p>
              <div className="flex min-h-11 items-center gap-3">
                <SignedOut>
                  <Link to="/login" className="text-sm text-fg underline decoration-from-font">
                    Anmelden
                  </Link>
                </SignedOut>
                <SignedIn>
                  <UserButton />
                </SignedIn>
              </div>
            </div>
          </footer>
        </div>
      </div>
    </div>
  );
}
