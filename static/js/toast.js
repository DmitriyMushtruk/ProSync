document.addEventListener('DOMContentLoaded', function () {
    let toastElements = document.querySelectorAll('.toast');
    let toastList = [...toastElements].map(function (toastElement) {
        return new bootstrap.Toast(toastElement, {
            autohide: true,
            delay: 3000
        });
    });

    toastList.forEach(function (toast) {
        toast.show();
    });

    toastElements.forEach(function (toastElement) {
        toastElement.addEventListener('hidden.bs.toast', function () {
            toastElement.style.opacity = '0';
        });
    });
});