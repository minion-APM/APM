(() => {
    const modal = document.getElementById('confirmation-modal');
    const title = document.getElementById('confirmation-modal-title');
    const message = document.getElementById('confirmation-modal-message');
    const cancel = document.getElementById('confirmation-modal-cancel');
    const confirm = document.getElementById('confirmation-modal-confirm');
    let pendingAction = null;
    let previousFocus = null;

    const close = () => {
        if (!modal || confirm.disabled) return;
        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');
        pendingAction = null;
        previousFocus?.focus();
    };

    window.openConfirmation = ({ title: modalTitle = 'Tem certeza?', message: modalMessage, cancelText = 'Cancelar', confirmText = 'Confirmar', loadingText = 'Processando...', cancelStyle = 'secondary', danger = false, onConfirm }) => {
        if (!modal) return;
        previousFocus = document.activeElement;
        title.textContent = modalTitle;
        message.textContent = modalMessage;
        cancel.textContent = cancelText;
        confirm.textContent = confirmText;
        cancel.classList.toggle('confirmation-modal__button--primary', cancelStyle === 'primary');
        confirm.classList.toggle('confirmation-modal__button--danger', danger);
        pendingAction = onConfirm;
        modal.hidden = false;
        modal.setAttribute('aria-hidden', 'false');
        confirm.disabled = false;
        cancel.disabled = false;
        confirm.dataset.loadingText = loadingText;
        requestAnimationFrame(() => confirm.focus());
    };

    window.showToast = (text, type = 'success') => {
        const container = document.getElementById('toast-container');
        if (!container) return;
        const toast = document.createElement('div');
        toast.className = `toast toast--${type}`;
        toast.textContent = `${type === 'success' ? '✓' : '✕'} ${text}`;
        container.appendChild(toast);
        window.setTimeout(() => toast.remove(), 3500);
    };

    cancel?.addEventListener('click', close);
    confirm?.addEventListener('click', async () => {
        if (!pendingAction || confirm.disabled) return;
        const label = confirm.textContent;
        confirm.disabled = true;
        cancel.disabled = true;
        confirm.textContent = `⏳ ${confirm.dataset.loadingText || 'Processando...'}`;
        try {
            await pendingAction();
            modal.hidden = true;
            modal.setAttribute('aria-hidden', 'true');
            pendingAction = null;
        } catch (error) {
            window.showToast('Não foi possível realizar a operação.', 'error');
            confirm.disabled = false;
            cancel.disabled = false;
            confirm.textContent = label;
        }
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && modal && !modal.hidden) close();
    });
    document.querySelectorAll('[data-confirm-form]').forEach(form => {
        form.addEventListener('submit', event => {
            if (form.dataset.confirmed === 'true') {
                delete form.dataset.confirmed;
                return;
            }
            event.preventDefault();
            const button = form.querySelector('button[type="submit"]');
            window.openConfirmation({
                title: form.dataset.confirmTitle,
                message: form.dataset.confirmMessage,
                confirmText: form.dataset.confirmLabel,
                loadingText: form.dataset.confirmLoading || 'Processando...',
                onConfirm: () => {
                    form.dataset.confirmed = 'true';
                    if (button) button.disabled = true;
                    form.requestSubmit(button || undefined);
                }
            });
        });
    });
})();
