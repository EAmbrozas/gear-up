document.addEventListener('DOMContentLoaded', function () {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        new bootstrap.Toast(toast, {
            autohide: true,
            delay: 10000 // Auto hide after 10 seconds
        }).show();
    });

    toasts.forEach(toast => {
        toast.querySelector('.btn-close').addEventListener('click', function() {
            bootstrap.Toast.getInstance(toast).hide();
        });
    });
});
