document.addEventListener('DOMContentLoaded', () => {
    // 1. Live Character Count for Game Description
    const descTextarea = document.getElementById('description');
    const descCount = document.getElementById('descCount');
    
    if (descTextarea && descCount) {
        descTextarea.addEventListener('input', () => {
            const length = descTextarea.value.length;
            descCount.textContent = `${length} / 2000`;
            if (length > 1800) {
                descCount.classList.add('warning');
            } else {
                descCount.classList.remove('warning');
            }
        });
    }

    // 2. Form Loading Spinner Activation
    const analyzeForm = document.getElementById('analyzeForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    if (analyzeForm && loadingOverlay) {
        analyzeForm.addEventListener('submit', (event) => {
            // Perform basic form validation check
            const title = document.getElementById('project_name').value.trim();
            const desc = descTextarea.value.trim();
            
            if (title && desc && desc.length >= 20) {
                loadingOverlay.style.display = 'flex';
                
                // Keep changing messages during load to make it feel responsive
                const statusMsg = document.getElementById('statusMessage');
                const messages = [
                    "Analyzing mechanics and genre complexity...",
                    "Querying AI Engine...",
                    "Scanning for optimal Unity assets...",
                    "Designing code architectures and managers...",
                    "Generating starter C# templates...",
                    "Compiling development roadmap phases..."
                ];
                let msgIndex = 0;
                
                setInterval(() => {
                    if (statusMsg) {
                        msgIndex = (msgIndex + 1) % messages.length;
                        statusMsg.textContent = messages[msgIndex];
                    }
                }, 2500);
            }
        });
    }
});

// 3. Clipboard Copy Helper with Visual Feedback
function copyScriptToClipboard(buttonId, preElementId) {
    const pre = document.getElementById(preElementId);
    const button = document.getElementById(buttonId);
    
    if (!pre || !button) return;
    
    // Extract text content of code block (removing HTML if highlighted)
    const textToCopy = pre.innerText;
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = button.innerHTML;
        button.innerHTML = '✔️ Copied!';
        button.classList.add('btn-success');
        button.style.borderColor = '#10b981';
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
            button.style.borderColor = '';
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        alert('Failed to copy to clipboard.');
    });
}

// 4. Script Selector Switcher
function showScript(filename) {
    // Hide all script pre-blocks
    const scriptBlocks = document.querySelectorAll('.script-code-block');
    scriptBlocks.forEach(block => {
        block.classList.add('d-none');
    });
    
    // Show active script block
    const activeBlock = document.getElementById(`script-${filename}`);
    if (activeBlock) {
        activeBlock.classList.remove('d-none');
    }
    
    // Update active tab styling
    const tabs = document.querySelectorAll('.script-tab');
    tabs.forEach(tab => {
        tab.classList.remove('active');
    });
    
    const activeTab = document.getElementById(`tab-${filename}`);
    if (activeTab) {
        activeTab.classList.add('active');
    }
}
