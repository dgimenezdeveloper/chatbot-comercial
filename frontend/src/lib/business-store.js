/**
 * localStorage helper for business data persistence.
 *
 * Used as the source of truth for onboarding status, business info,
 * and logo until the backend supports real persistence.
 *
 * Keys:
 *   pymio_onboarding_completed — "true" if onboarding was finished
 *   pymio_business_data        — JSON with business name, description, etc.
 *   pymio_business_logo        — base64 data URL of the uploaded logo
 *
 * @module lib/business-store
 */

const KEYS = {
  ONBOARDING: "pymio_onboarding_completed",
  BUSINESS: "pymio_business_data",
  LOGO: "pymio_business_logo",
};

// ─── Onboarding flag ─────────────────────────────────────────────────────────

/**
 * Whether the current user has completed onboarding.
 * @returns {boolean}
 */
export function isOnboardingCompleted() {
  if (typeof window === "undefined") return false;
  return localStorage.getItem(KEYS.ONBOARDING) === "true";
}

/**
 * Mark onboarding as completed.
 */
export function markOnboardingCompleted() {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEYS.ONBOARDING, "true");
}

/**
 * Reset onboarding status (useful for testing).
 */
export function resetOnboarding() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(KEYS.ONBOARDING);
}

// ─── Business data ───────────────────────────────────────────────────────────

/**
 * @typedef {Object} BusinessData
 * @property {string} name        — Nombre del negocio
 * @property {string} description — Descripción
 * @property {string} category    — Categoría (hair-salon, barbershop, etc.)
 * @property {string} address     — Dirección
 * @property {string} phone       — Teléfono de contacto
 * @property {string} email       — Email de contacto
 * @property {string} [website]   — Sitio web (opcional)
 * @property {Object} [social]    — { instagram, facebook, whatsapp }
 * @property {Object} [schedule]  — { days, open, close, lunchBreak }
 */

/**
 * Retrieves persisted business data.
 * @returns {BusinessData|null}
 */
export function getBusinessData() {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(KEYS.BUSINESS);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

/**
 * Persists business data to localStorage.
 * @param {BusinessData} data
 */
export function setBusinessData(data) {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEYS.BUSINESS, JSON.stringify(data));
}

/**
 * Returns the business name or a fallback.
 * @param {string} [fallback="Mi Negocio"]
 * @returns {string}
 */
export function getBusinessName(fallback = "Mi Negocio") {
  const data = getBusinessData();
  return data?.name || fallback;
}

// ─── Logo ────────────────────────────────────────────────────────────────────

/**
 * Retrieves the logo as a base64 data URL.
 * @returns {string|null}
 */
export function getBusinessLogo() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(KEYS.LOGO) || null;
}

/**
 * Persists the logo as a base64 data URL.
 * @param {string} dataUrl — base64 data URL (e.g. "data:image/png;base64,...")
 */
export function setBusinessLogo(dataUrl) {
  if (typeof window === "undefined") return;
  localStorage.setItem(KEYS.LOGO, dataUrl);
}

/**
 * Removes the stored logo.
 */
export function removeBusinessLogo() {
  if (typeof window === "undefined") return;
  localStorage.removeItem(KEYS.LOGO);
}

/**
 * Converts a File object to a base64 data URL and stores it.
 * @param {File} file
 * @returns {Promise<string>} The data URL
 */
export function saveLogoFromFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result;
      setBusinessLogo(dataUrl);
      resolve(dataUrl);
    };
    reader.onerror = () => reject(new Error("Error al leer el archivo"));
    reader.readAsDataURL(file);
  });
}
