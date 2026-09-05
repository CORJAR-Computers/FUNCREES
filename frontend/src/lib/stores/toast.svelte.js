/**
 * @typedef {Object} ToastItem
 * @property {string} id
 * @property {string} message
 * @property {'success'|'error'|'warning'|'info'} type
 */

class ToastStore {
  /** @type {ToastItem[]} */
  toasts = $state([]);

  /**
   * @param {string} message
   * @param {'success'|'error'|'warning'|'info'} [type='success']
   * @param {number} [duration=4000]
   */
  show(message, type = 'success', duration = 4000) {
    if (this.toasts.some(t => t.message === message)) return;

    const id = Date.now() + Math.random().toString(36).substring(2, 7);
    /** @type {ToastItem} */
    const item = { id, message, type };
    this.toasts.push(item);

    setTimeout(() => {
      this.remove(id);
    }, duration);
  }

  /**
   * @param {string} id
   */
  remove(id) {
    this.toasts = this.toasts.filter(t => t.id !== id);
  }
}

export const toast = new ToastStore();
