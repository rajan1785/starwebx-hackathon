function showToast(message, color = '#333', duration = 3000) {
    // 1. Get or create the container
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    // 2. Create the toast element
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerText = message;
    toast.style.backgroundColor = color;

    // 3. Add to screen
    container.appendChild(toast);

    // 4. Remove after duration
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.5s ease';
        setTimeout(() => toast.remove(), 500);
    }, duration);
}


function showModal(message, callback = null) {
    // 1. Get or create the modal container
    let modalContainer = document.getElementById('modal-container');
    if (!modalContainer) {
        modalContainer = document.createElement('div');
        modalContainer.id = 'modal-container';
        modalContainer.className = 'modal-container';
        document.body.appendChild(modalContainer);
    }
    // 2. Create the modal content
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    const parag = document.createElement('p');
    parag.innerText = message;
    modalContent.appendChild(parag);

    buttonContainer = document.createElement('div');
    buttonContainer.className = 'modal-button-container';
    modalContent.appendChild(buttonContainer);
    // 3. Add close button
    const closeButton = document.createElement('button');
    closeButton.className = 'modal-close-button';
    closeButton.innerText = 'Close';
    closeButton.onclick = () => {
        modalContainer.remove();
    }
    buttonContainer.appendChild(closeButton);
    // 4. Add Okay button
    const okayButton = document.createElement('button');
    okayButton.className = 'modal-okay-button';
    okayButton.innerText = 'Okay';
    okayButton.onclick = () => {
        modalContainer.remove();
        if (callback) callback();
    }
    buttonContainer.appendChild(okayButton);
    // 5. Add to screen
    modalContainer.appendChild(modalContent);
}