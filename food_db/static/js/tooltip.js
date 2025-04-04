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