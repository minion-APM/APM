(() => {
    const modal = document.getElementById('confirmation-modal');
    const title = document.getElementById('confirmation-modal-title');
    const message = document.getElementById('confirmation-modal-message');
    const cancel = document.getElementById('confirmation-modal-cancel');
    const confirm = document.getElementById('confirmation-modal-confirm');
    let pendingAction = null;
    let pendingCancelAction = null;
    let previousFocus = null;

    const close = () => {
        if (!modal || confirm.disabled) return;
        modal.hidden = true;
        modal.setAttribute('aria-hidden', 'true');
        pendingAction = null;
        const onCancel = pendingCancelAction;
        pendingCancelAction = null;
        onCancel?.();
        previousFocus?.focus();
    };

    window.openConfirmation = ({ title: modalTitle = 'Tem certeza?', message: modalMessage, cancelText = 'Cancelar', confirmText = 'Confirmar', loadingText = 'Processando...', cancelStyle = 'secondary', danger = false, onConfirm, onCancel }) => {
        if (!modal) return;
        previousFocus = document.activeElement;
        title.textContent = modalTitle;
        message.textContent = modalMessage;
        cancel.textContent = cancelText;
        confirm.textContent = confirmText;
        cancel.classList.toggle('confirmation-modal__button--primary', cancelStyle === 'primary');
        confirm.classList.toggle('confirmation-modal__button--danger', danger);
        pendingAction = onConfirm;
        pendingCancelAction = onCancel;
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
            pendingCancelAction = null;
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
            const dialog = form.querySelector('dialog');
            const reopenDialogOnCancel = Boolean(dialog?.open);
            if (reopenDialogOnCancel) dialog.close();
            window.openConfirmation({
                title: form.dataset.confirmTitle,
                message: form.dataset.confirmMessage,
                confirmText: form.dataset.confirmLabel,
                loadingText: form.dataset.confirmLoading || 'Processando...',
                onCancel: () => { if (reopenDialogOnCancel) dialog.showModal(); },
                onConfirm: () => {
                    form.dataset.confirmed = 'true';
                    form.requestSubmit(button || undefined);
                }
            });
        });
    });
    document.querySelectorAll('[data-confirm-link]').forEach(link => {
        link.addEventListener('click', event => {
            event.preventDefault();
            const destino = link.href;
            window.openConfirmation({
                title: link.dataset.confirmTitle,
                message: link.dataset.confirmMessage,
                confirmText: link.dataset.confirmLabel || 'Confirmar',
                onConfirm: () => { window.location.href = destino; }
            });
        });
    });
})();
