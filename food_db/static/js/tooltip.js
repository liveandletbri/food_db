function hideToolTip(tooltip) {
    tooltip.className = "form_validate_tooltip"
}

function showToolTip(tooltip) {
    tooltip.className = "form_validate_tooltip visible"
}

function showAndHideTooltip(tooltip, duration) {
    if ( duration == undefined ) {
        duration = 3000
    }
    tooltip.scrollIntoView({behavior: 'smooth', block: 'center'})
    setTimeout(showToolTip, 300, tooltip)
    setTimeout(hideToolTip, duration, tooltip)
}