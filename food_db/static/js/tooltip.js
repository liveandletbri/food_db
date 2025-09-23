function hideToolTip(tooltip) {
    tooltip.classList.remove('visible')
}

function showToolTip(tooltip) {
    tooltip.classList.add('visible')
}

function showAndHideTooltip(tooltip, duration) {
    if ( duration == undefined ) {
        duration = 3000
    }
    tooltip.scrollIntoView({behavior: 'smooth', block: 'center'})
    setTimeout(showToolTip, 300, tooltip)
    setTimeout(hideToolTip, duration, tooltip)
}

// Ingredient link tooltip functionality
document.addEventListener('DOMContentLoaded', function() {
    // Find all ingredient links
    let ingredientLinks = document.querySelectorAll('.ingredient-link');
    
    ingredientLinks.forEach(function(link) {
        let tooltip = null;
        
        // Create tooltip element
        function createTooltip() {
            let tooltipElement = document.createElement('div');
            tooltipElement.className = 'ingredient-tooltip';
            tooltipElement.textContent = link.getAttribute('data-tooltip');
            document.body.appendChild(tooltipElement);
            return tooltipElement;
        }
        
        // Show tooltip on mouseenter
        link.addEventListener('mouseenter', function(e) {
            if (!tooltip) {
                tooltip = createTooltip();
            }
            
            // Position tooltip
            let rect = link.getBoundingClientRect();
            let tooltipRect = tooltip.getBoundingClientRect();
            
            let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
            let top = rect.top - tooltipRect.height - 10;
            
            // Adjust if tooltip would go off screen
            if (left < 10) left = 10;
            if (left + tooltipRect.width > window.innerWidth - 10) {
                left = window.innerWidth - tooltipRect.width - 10;
            }
            if (top < 10) {
                top = rect.bottom + 10;
                // Change arrow direction
                tooltip.style.setProperty('--arrow-direction', 'up');
            }
            
            tooltip.style.left = left + 'px';
            tooltip.style.top = top + 'px';
            
            showToolTip(tooltip);
        });
        
        // Hide tooltip on mouseleave
        link.addEventListener('mouseleave', function() {
            if (tooltip) {
                hideToolTip(tooltip);
            }
        });
    });
});