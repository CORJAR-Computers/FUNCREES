/**
 * Convierte un string de monto en formato colombiano a número.
 * Maneja formatos: "10.000", "10000", "10.000,00", "$10.000"
 * @param {string|number|null|undefined|any} val
 * @returns {number}
 */
export function parseCOP(val) {
  if (typeof val !== 'string' && typeof val !== 'number') return 0;
  let s = String(val).replace(/[^\d,\.]/g, '');
  if (s.includes(',') && /,\d{1,2}$/.test(s)) {
    s = s.replace(/\./g, '').replace(',', '.');
  } else {
    s = s.replace(/\./g, '');
  }
  const num = parseFloat(s);
  return isNaN(num) ? 0 : num;
}

/**
 * Formatea un número al estándar colombiano (con puntos de miles y coma decimal).
 * @param {number|string|null|undefined|any} val
 * @returns {string}
 */
export function formatMoneyNumber(val) {
  const num = typeof val === 'number' ? val : parseFloat(String(val));
  if (isNaN(num)) return '0';
  const parts = String(num).split('.');
  const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  if (parts.length > 1 && parts[1]) {
    return `${integerPart},${parts[1].substring(0, 2)}`;
  }
  return integerPart;
}
