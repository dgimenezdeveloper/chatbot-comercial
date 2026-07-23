/**
 * Server Component — no "use client" needed.
 *
 * Injects an inline blocking script into <head> that adds the theme class
 * to <html> synchronously, before the first paint. This eliminates the
 * flash of fallback colors that a useEffect approach would cause.
 *
 * JSON.stringify safely escapes the theme string in case the value
 * ever becomes dynamic.
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
