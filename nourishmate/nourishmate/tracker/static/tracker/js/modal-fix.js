/**
 * This file makes sure that when a Bootstrap modal is hidden,
 * the currently focused element is blurred.
 */

document.addEventListener("DOMContentLoaded", function () {
    document.addEventListener('hide.bs.modal', function (event) {
    if (document.activeElement) {
        document.activeElement.blur();
    }
    });
});
