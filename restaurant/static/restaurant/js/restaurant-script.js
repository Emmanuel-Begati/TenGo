document.addEventListener('DOMContentLoaded', function() {
    // Get canvas element safely with null check
    const canvas = document.getElementById('chartCanvas');
    
    if (canvas) {
        const ctx = canvas.getContext('2d');
        // Continue with chart code only if canvas exists
        // Your existing chart code...
    }

    // Safely handle other DOM elements
    function safelyGetElement(id) {
        const element = document.getElementById(id);
        return element;
    }

    // Apply this pattern to other DOM manipulations
    const loaderElement = document.querySelector('.loader-line');
    if (loaderElement) {
        loaderElement.style.display = 'none';
    }
    
    // Your other code...
});