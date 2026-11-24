/* Unity AI Architect - small progressive-enhancement helpers (no inline scripts, CSP friendly). */
document.addEventListener('DOMContentLoaded', () => {
    initDescriptionCounter();
    initAnalyzeForm();
    initScriptViewer();
    initConfirmForms();
});

/** Live character counter for the game description. */
function initDescriptionCounter() {
    const textarea = document.getElementById('description');
    const counter = document.getElementById('descCount');
    if (!textarea || !counter) return;

    const update = () => {
        const length = textarea.value.length;
        counter.textContent = `${length} / 2000`;
        counter.classList.toggle('warning', length > 1800);
    };
    textarea.addEventListener('input', update);
    update();
}

/** Bootstrap validation + loading overlay for the analyze form. */
function initAnalyzeForm() {
    const form = document.getElementById('analyzeForm');
    const overlay = document.getElementById('loadingOverlay');
    if (!form) return;

    const messages = [
        'Analyzing mechanics and genre complexity...',
        'Scanning for optimal Unity assets...',
        'Designing code architecture and managers...',
        'Generating starter C# templates...',
        'Compiling development roadmap phases...',
    ];

    form.addEventListener('submit', (event) => {
        form.classList.add('was-validated');
        if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
            return;
        }
        if (!overlay) return;

        overlay.style.display = 'flex';
        const status = document.getElementById('statusMessage');
        let index = 0;
        setInterval(() => {
            index = (index + 1) % messages.length;
            if (status) status.textContent = messages[index];
        }, 2500);
    });
}

/** Script tabs, copy and download buttons on the results page. */
function initScriptViewer() {
    const tabs = document.querySelectorAll('[data-script-target]');
    tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.script-code-block').forEach((b) => b.classList.add('d-none'));
            tabs.forEach((t) => t.classList.remove('active'));
            const block = document.getElementById(tab.dataset.scriptTarget);
            if (block) block.classList.remove('d-none');
            tab.classList.add('active');
        });
    });

    document.querySelectorAll('[data-copy-target]').forEach((button) => {
        button.addEventListener('click', () => copyCode(button));
    });
    document.querySelectorAll('[data-download-target]').forEach((button) => {
        button.addEventListener('click', () => downloadCode(button));
    });
}

function codeFor(button, attr) {
    const pre = document.getElementById(button.dataset[attr]);
    return pre ? pre.textContent : '';
}

function flashButton(button, label) {
    const original = button.innerHTML;
    button.textContent = label;
    setTimeout(() => { button.innerHTML = original; }, 1800);
}

async function copyCode(button) {
    const text = codeFor(button, 'copyTarget');
    try {
        await navigator.clipboard.writeText(text);
        flashButton(button, 'Copied!');
    } catch (err) {
        // Fallback for non-secure contexts or denied clipboard permission.
        const area = document.createElement('textarea');
        area.value = text;
        document.body.appendChild(area);
        area.select();
        const ok = document.execCommand('copy');
        area.remove();
        flashButton(button, ok ? 'Copied!' : 'Copy failed');
    }
}

function downloadCode(button) {
    const blob = new Blob([codeFor(button, 'downloadTarget')], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = button.dataset.filename || 'script.cs';
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(link.href);
}

/** Ask for confirmation before submitting forms marked with data-confirm. */
function initConfirmForms() {
    document.querySelectorAll('form[data-confirm]').forEach((form) => {
        form.addEventListener('submit', (event) => {
            if (!window.confirm(form.dataset.confirm)) event.preventDefault();
        });
    });
}
