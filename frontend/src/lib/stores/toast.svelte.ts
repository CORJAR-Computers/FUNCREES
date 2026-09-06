/**
 * Store de notificaciones toast (Svelte 5 runes).
 */
export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastItem {
	id: string;
	message: string;
	type: ToastType;
}

class ToastStore {
	toasts = $state<ToastItem[]>([]);

	show(message: string, type: ToastType = 'success', duration: number = 4000): void {
		if (this.toasts.some((t) => t.message === message)) return;

		const id = Date.now() + Math.random().toString(36).substring(2, 7);
		const item: ToastItem = { id, message, type };
		this.toasts.push(item);

		setTimeout(() => {
			this.remove(id);
		}, duration);
	}

	remove(id: string): void {
		this.toasts = this.toasts.filter((t) => t.id !== id);
	}
}

export const toast = new ToastStore();
