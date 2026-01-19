let ingredientLinks = document.querySelectorAll('.ingredient_link');

function isAndroidChrome() {
    let userAgent = navigator.userAgent.toLowerCase();
    let isMobile = /chrome/.test(userAgent) && /android/.test(userAgent) && /mobile/.test(userAgent);
    return (( isMobile ) ? 'mobile' : 'computer')
}

function isiPhoneSafari() {
    let userAgent = navigator.userAgent.toLowerCase();
    let isMobile = /iphone/.test(userAgent) && /safari/.test(userAgent) && !/chrome/.test(userAgent) && !/crios/.test(userAgent);
    return (( isMobile ) ? 'mobile' : 'computer')
}

function isMobile() {
    return (( isAndroidChrome() == 'mobile' || isiPhoneSafari() == 'mobile' ) ? 'mobile' : 'computer')
}

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

function positionTooltip(tooltip, targetElement, centerOnMobile, verticalOffset) {
    if (targetElement) {
        let rect = targetElement.getBoundingClientRect()
        let isMobileDevice = isMobile() == 'mobile'
        
        // Get button positions to avoid overlap (buttons are fixed at bottom: 30px, or 125px on recipe detail page)
        let cookingModeButton = document.querySelector('.cooking_mode_tooltip.visible')
        let exitButton = document.querySelector('.tutorial_exit_button.visible')
        let buttonBottom = 0
        let buttonHeight = 0
        let buttonTopInViewport = 0
        
        if (cookingModeButton || exitButton) {
            let activeButton = cookingModeButton || exitButton
            let buttonRect = activeButton.getBoundingClientRect()
            buttonBottom = buttonRect.bottom
            buttonHeight = buttonRect.height
            buttonTopInViewport = buttonRect.top
        }
        let buttonPadding = 20
        
        // Position tooltip above or below the target element
        let spaceAbove = rect.top
        let spaceBelow = window.innerHeight - rect.bottom
        
        tooltip.style.position = 'absolute'
        
        // On desktop, ensure tooltip maintains its width (400px max from CSS)
        let tooltipWidth = 400
        if (isMobileDevice) {
            tooltipWidth = window.innerWidth * 0.9
        }
        
        // Handle horizontal positioning
        if (centerOnMobile && isMobileDevice) {
            // Mobile: center tooltip and scroll viewport to accommodate it
            // The tooltip will be centered at 50% of viewport
            // We want to scroll so that when centered, it points to the target
            
            // Target's center in current viewport coordinates
            let targetCenterX = rect.left + rect.width / 2
            let viewportCenterX = window.innerWidth / 2
            
            // How much we need to scroll to align target center with viewport center
            let scrollNeeded = targetCenterX - viewportCenterX
            
            // Get scroll limits
            let currentScrollX = window.scrollX
            let maxScrollX = Math.max(0, document.documentElement.scrollWidth - window.innerWidth)
            
            // Calculate new scroll position (scroll as far as possible toward centering)
            let newScrollX = Math.max(0, Math.min(maxScrollX, currentScrollX + scrollNeeded))
            
            // Apply scroll
            if (Math.abs(newScrollX - currentScrollX) > 1) {
                window.scrollTo({
                    left: newScrollX,
                    behavior: 'smooth'
                })
            }
            
            // Position tooltip centered in viewport
            tooltip.style.left = '50%'
            tooltip.style.transform = 'translateX(-50%)'
            
            // After scroll completes, check if tooltip extends beyond screen
            // With 90% width it should fit, but handle edge case
            setTimeout(function() {
                let tooltipRectAfter = tooltip.getBoundingClientRect()
                let tooltipLeft = tooltipRectAfter.left
                let tooltipRight = tooltipRectAfter.right
                let needsAdjustment = false
                let adjustedLeft = null
                
                if (tooltipLeft < 0) {
                    // Tooltip extends left - position against left edge
                    let tooltipHalfWidth = tooltipRectAfter.width / 2
                    adjustedLeft = window.scrollX + tooltipHalfWidth
                    needsAdjustment = true
                    // Also scroll to far left if possible
                    window.scrollTo({
                        left: 0,
                        behavior: 'smooth'
                    })
                } else if (tooltipRight > window.innerWidth) {
                    // Tooltip extends right - position against right edge
                    let tooltipHalfWidth = tooltipRectAfter.width / 2
                    adjustedLeft = window.scrollX + window.innerWidth - tooltipHalfWidth
                    needsAdjustment = true
                    // Also scroll to far right if possible
                    let finalMaxScroll = Math.max(0, document.documentElement.scrollWidth - window.innerWidth)
                    window.scrollTo({
                        left: finalMaxScroll,
                        behavior: 'smooth'
                    })
                }
                
                if (needsAdjustment && adjustedLeft !== null) {
                    tooltip.style.left = `${adjustedLeft}px`
                    tooltip.style.transform = 'translateX(-50%)'
                }
            }, 100)
        } else {
            // Desktop: maintain width, clamp to screen edges
            let leftPos = rect.left + window.scrollX
            let rightPos = leftPos + tooltipWidth
            let screenLeft = window.scrollX
            let screenRight = window.scrollX + window.innerWidth
            
            // Clamp to screen edges while maintaining width
            if (rightPos > screenRight) {
                leftPos = screenRight - tooltipWidth
            }
            if (leftPos < screenLeft) {
                leftPos = screenLeft
            }
            
            tooltip.style.left = `${leftPos}px`
            tooltip.style.transform = ''
        }
        
        // Wait for tooltip to be positioned horizontally before measuring
        // We need to force a reflow to get accurate measurements
        void tooltip.offsetHeight
        
        let tooltipRect = tooltip.getBoundingClientRect()
        
        // Determine vertical position - above or below
        let positionBelow = spaceBelow > tooltipRect.height + 20 || spaceBelow > spaceAbove
        let tooltipTop
        
        if (positionBelow) {
            tooltipTop = rect.bottom + window.scrollY + (verticalOffset || 10)
        } else {
            tooltipTop = rect.top + window.scrollY - tooltipRect.height - (verticalOffset || 10)
        }
        
        // Check for overlap with buttons (buttons are fixed at bottom of viewport)
        if (buttonHeight > 0) {
            // Convert tooltip position to viewport coordinates for comparison with fixed button
            let tooltipTopInViewport = tooltipTop - window.scrollY
            let tooltipBottomInViewport = tooltipTopInViewport + tooltipRect.height
            let tooltipBottomInDoc = tooltipTop + tooltipRect.height
            
            // Button is fixed, so buttonTopInViewport and buttonBottom are already in viewport coords
            // Check if tooltip overlaps button area
            if (tooltipBottomInViewport > buttonTopInViewport - buttonPadding) {
                // Tooltip would overlap - try to move it above
                let alternativeTop = rect.top + window.scrollY - tooltipRect.height - (verticalOffset || 10)
                let alternativeBottomInDoc = alternativeTop + tooltipRect.height
                let alternativeTopInViewport = alternativeTop - window.scrollY
                let alternativeBottomInViewport = alternativeTopInViewport + tooltipRect.height
                
                // Check if there's enough space above and it doesn't overlap button
                if (alternativeTop >= window.scrollY && alternativeBottomInViewport <= buttonTopInViewport - buttonPadding) {
                    tooltipTop = alternativeTop
                } else {
                    // Not enough space above, position it just above the button area
                    tooltipTop = (buttonTopInViewport - buttonPadding - tooltipRect.height) + window.scrollY
                    // But ensure it doesn't go too high (at least 10px from top of viewport)
                    let minTooltipTop = window.scrollY + 10
                    if (tooltipTop < minTooltipTop) {
                        tooltipTop = minTooltipTop
                    }
                }
            }
        }
        
        tooltip.style.top = `${tooltipTop}px`
    } else {
        // Center on screen if element not found
        tooltip.style.position = 'fixed'
        tooltip.style.top = '50%'
        tooltip.style.left = '50%'
        tooltip.style.transform = 'translate(-50%, -50%)'
    }
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
