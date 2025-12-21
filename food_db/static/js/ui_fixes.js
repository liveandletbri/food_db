// Disable scroll wheel from changing number input values
// Use event delegation to handle both existing and dynamically added inputs
document.addEventListener('wheel', function(e) {
    if (e.target && e.target.type === 'number' && document.activeElement === e.target) {
        e.preventDefault();
    }
}, { passive: false });


