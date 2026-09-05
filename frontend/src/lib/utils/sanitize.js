/**
 * Sanitiza strings para prevenir inyecciones XSS.
 * @param {string|any} str
 * @returns {string}
 */
export function sanitizeHTML(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
