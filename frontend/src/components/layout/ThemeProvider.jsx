/**
 * Server Component — no "use client" needed.
 *
 * Injects an inline blocking script into <head> that adds the theme class
 * to <html> synchronously, before the first paint. This eliminates the
 * flash of fallback colors that a useEffect approach would cause.
 *
 * Note: React shows a dev-only warning about <script> tags during client-side
 * navigation. This is harmless — the theme class persists on <html> from the
 * initial SSR render and doesn't need to re-execute on soft nav.
 */
export default function ThemeProvider({ theme }) {
  return (
    <script
      dangerouslySetInnerHTML={{
        __html: `document.documentElement.classList.add(${JSON.stringify(theme)})`,
      }}
    />
  );
}
