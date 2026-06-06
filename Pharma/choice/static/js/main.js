/**
 * PharmaChoice — main.js
 * Handles: auto-dismiss alerts, order total update,
 *          form validation, qty clamping, confirm dialogs,
 *          and disabled payment option clicks.
 */

/* ── AUTO-DISMISS FLASH ALERTS ── */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.alert').forEach(function (el) {
        setTimeout(function () {
            el.style.transition = 'opacity .5s';
            el.style.opacity = '0';
            setTimeout(function () { el.remove(); }, 500);
        }, 4000);
    });
});

/* ── ORDER TOTAL UPDATER ──
   unitPrice must be set as a global var in the place_order template */
function updateTotal(qty) {
    var price = parseFloat(window.unitPrice) || 0;
    var n = Math.max(1, parseInt(qty, 10) || 1);
    var el = document.getElementById('total');
    if (el) el.textContent = '₹' + (price * n).toFixed(2);
}

/* ── QTY INPUT — clamp to min/max ── */
document.addEventListener('DOMContentLoaded', function () {
    var qtyInput = document.getElementById('qtyInput');
    if (!qtyInput) return;

    qtyInput.addEventListener('change', function () {
        var max = parseInt(this.max, 10);
        var min = parseInt(this.min, 10) || 1;
        var val = parseInt(this.value, 10);
        if (isNaN(val) || val < min) val = min;
        if (max && val > max)        val = max;
        this.value = val;
        updateTotal(val);
    });
    updateTotal(qtyInput.value); // set initial total on page load
});

/* ── FORM VALIDATION ── */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            var ok = true;
            form.querySelectorAll('[required]').forEach(function (f) {
                if (!f.value.trim()) {
                    f.classList.add('input-error');
                    ok = false;
                } else {
                    f.classList.remove('input-error');
                }
            });
            if (!ok) e.preventDefault();
        });
    });

    /* email format */
    document.querySelectorAll('input[type="email"]').forEach(function (f) {
        f.addEventListener('blur', function () {
            var ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.value);
            this.classList.toggle('input-error', this.value && !ok);
        });
    });

    /* phone — 10-digit India */
    document.querySelectorAll('input[name="phone"]').forEach(function (f) {
        f.addEventListener('blur', function () {
            var ok = /^[6-9]\d{9}$/.test(this.value.replace(/\s/g, ''));
            this.classList.toggle('input-error', this.value && !ok);
        });
    });
});

/* ── CONFIRM DIALOGS — add data-confirm="..." to any <a> ── */
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('a[data-confirm]').forEach(function (link) {
        link.addEventListener('click', function (e) {
            if (!confirm(this.getAttribute('data-confirm'))) e.preventDefault();
        });
    });
});

/* ── DISABLED PAYMENT OPTIONS — show warning in banner ── */
document.addEventListener('DOMContentLoaded', function () {
    var banner = document.getElementById('codBanner');
    if (!banner) return;

    var defaultHTML = banner.innerHTML;
    var resetTimer;

    document.querySelectorAll('.disabled-option label').forEach(function (lbl) {
        lbl.addEventListener('click', function (e) {
            e.preventDefault();

            /* flash banner to warn user */
            banner.style.background  = 'var(--warn-l)';
            banner.style.borderColor = 'rgba(245,166,35,.5)';
            banner.style.color       = '#8a6200';
            banner.innerHTML =
                '<span style="font-size:16px;">⚠️</span>' +
                '<span>This payment method is <strong>not available yet</strong>. ' +
                'Please use <strong>Cash on Delivery</strong>.</span>';

            clearTimeout(resetTimer);
            resetTimer = setTimeout(function () {
                banner.style.background  = '';
                banner.style.borderColor = '';
                banner.style.color       = '';
                banner.innerHTML = defaultHTML;
            }, 3000);
        });
    });
});
