let ingredientLinks = document.querySelectorAll('.ingredient_link');

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

ingredientLinks.forEach(function(link) {
    let tooltip = null;
    
    // Create tooltip element
    function createTooltip() {
        let tooltipElement = document.createElement('div');
        tooltipElement.classList.add('ingredient_link_tooltip');
        tooltipElement.classList.add('tooltip');

        // Each ingredient_link span has the tooltip content already embedded in data-tooltip
        tooltipElement.textContent = link.getAttribute('data-tooltip');
        document.body.appendChild(tooltipElement);
        return tooltipElement;
    }
    
    // Show tooltip when hovering over ingredient_link
    link.addEventListener('mouseenter', function(e) {
        if (!tooltip) {
            tooltip = createTooltip();
        }

        tooltip.style.left = `${link.offsetLeft - 5}px`;
        tooltip.style.top = `${link.offsetTop - 40}px`;
        
        showToolTip(tooltip);
    });
    
    // Hide tooltip on mouseleave
    link.addEventListener('mouseleave', function() {
        if (tooltip) {
            hideToolTip(tooltip);
        }
    });
});
