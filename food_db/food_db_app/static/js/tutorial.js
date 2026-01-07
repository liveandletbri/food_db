// Tutorial system for interactive walkthrough of Food DB features

let currentTutorialStep = null
let tutorialTooltipElement = null
let tutorialExitButton = null

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

function scrollToElement(selector) {
    let targetElement = document.querySelector(selector)
    if (targetElement) {
        targetElement.scrollIntoView({behavior: 'smooth', block: 'center'})
        return targetElement
    }
    return null
}

function createTutorialTooltip(content, isLastStep) {
    // Remove existing tooltip if present
    if (tutorialTooltipElement) {
        tutorialTooltipElement.remove()
    }
    
    let tooltip = document.createElement('div')
    tooltip.classList.add('tutorial_tooltip')
    tooltip.classList.add('tooltip')
    
    let contentDiv = document.createElement('div')
    contentDiv.innerHTML = content
    tooltip.appendChild(contentDiv)
    
    let buttonDiv = document.createElement('div')
    buttonDiv.style.marginTop = '10px'
    buttonDiv.style.textAlign = 'center'
    
    let nextButton = document.createElement('button')
    nextButton.textContent = isLastStep ? 'Finish' : 'Next'
    nextButton.style.padding = '2px 8px'
    nextButton.style.marginTop = '10px'
    nextButton.style.cursor = 'pointer'
    nextButton.addEventListener('click', function() {
        if (isLastStep) {
            exitTutorial()
        } else {
            nextTutorialStep()
        }
    })
    
    buttonDiv.appendChild(nextButton)
    tooltip.appendChild(buttonDiv)
    
    document.body.appendChild(tooltip)
    tutorialTooltipElement = tooltip
    
    return tooltip
}

function showTutorialTooltip(stepData, targetElement) {
    // Check if this is the last step (determined on server side)
    let isLastStep = stepData.is_last_step || false
    
    let tooltip = createTutorialTooltip(stepData.tooltip_content, isLastStep)
    positionTooltip(tooltip, targetElement)
    
    // Show tooltip with animation using function from tooltip.js
    setTimeout(function() {
        showToolTip(tooltip)
    }, 100)
}

async function startTutorial(stepId) {
    let response = await fetch('/start_tutorial/', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            step_id: stepId
        })
    })
    .then(function(response) {
        return response.json()
    })
    
    if (response.success && response.step_data) {
        // Navigate to the step's page
        window.location.href = response.step_data.url
    }
}

async function nextTutorialStep() {
    let response = await fetch('/next_tutorial_step/', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    })
    .then(function(response) {
        return response.json()
    })
    
    if (response.success && response.step_data) {
        // Check if next step is on the same page
        let currentUrl = window.location.pathname
        let nextStepUrl = response.step_data.url
        
        // Extract pathname from nextStepUrl if it's a full URL
        if (nextStepUrl.startsWith('http')) {
            let urlObj = new URL(nextStepUrl)
            nextStepUrl = urlObj.pathname
        }
        
        if (currentUrl === nextStepUrl) {
            // Same page - just show the next step without reloading
            showTutorialStep(response.step_data)
        } else {
            // Different page - navigate to the next step's page
            window.location.href = response.step_data.url
        }
    } else if (response.success && !response.step_data) {
        // No more steps, exit tutorial
        exitTutorial()
    }
}

async function exitTutorial() {
    await fetch('/exit_tutorial/', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
    })
    
    // Hide tooltip using function from tooltip.js
    if (tutorialTooltipElement) {
        hideToolTip(tutorialTooltipElement)
        setTimeout(function() {
            if (tutorialTooltipElement) {
                tutorialTooltipElement.remove()
                tutorialTooltipElement = null
            }
        }, 800)
    }
    
    // Hide exit button using function from tooltip.js
    if (tutorialExitButton) {
        hideToolTip(tutorialExitButton)
    }
    
    // Clear tutorial state
    currentTutorialStep = null
    
    // Reload page to clear tutorial state
    window.location.reload()
}

function createTutorialExitButton() {
    if (tutorialExitButton) {
        return tutorialExitButton
    }
    
    let button = document.createElement('div')
    button.id = 'tutorial_exit_button'
    button.classList.add('tutorial_exit_button')
    button.classList.add('tooltip')
    
    let titleSpan = document.createElement('span')
    titleSpan.textContent = 'Exit Tutorial'
    titleSpan.style.fontSize = '20px'
    titleSpan.style.fontWeight = '900'
    button.appendChild(titleSpan)
    
    button.style.cursor = 'pointer'
    button.addEventListener('click', exitTutorial)
    
    document.body.appendChild(button)
    tutorialExitButton = button
    
    return button
}

function showTutorialExitButton() {
    let button = createTutorialExitButton()
    setTimeout(function() {
        showToolTip(button)
    }, 100)
}

function initTutorial(stepId) {
    // Start tutorial from a specific step (or first step if stepId is null/undefined)
    startTutorial(stepId || null)
}

function showTutorialStep(stepData) {
    currentTutorialStep = stepData
    
    // Show exit button
    showTutorialExitButton()
    
    // Scroll to target element
    let targetElement = scrollToElement(stepData.scroll_target)
    
    // Show tooltip after scrolling animation
    setTimeout(function() {
        showTutorialTooltip(stepData, targetElement)
    }, 500)
}

function handleTutorialOnPageLoad() {
    // Check if tutorial state is available from page context
    let tutorialStateElement = document.getElementById('tutorialStateData')
    let tutorialStepElement = document.getElementById('tutorialCurrentStepData')
    
    if (!tutorialStateElement || !tutorialStepElement) {
        return
    }
    
    let tutorialState = JSON.parse(tutorialStateElement.textContent)
    let currentStepData = JSON.parse(tutorialStepElement.textContent)
    
    if (tutorialState.tutorial_active && currentStepData) {
        // Check if we're on the correct page
        let currentUrl = window.location.pathname
        let stepUrl = currentStepData.url
        
        // Extract pathname from stepUrl if it's a full URL
        if (stepUrl.startsWith('http')) {
            let urlObj = new URL(stepUrl)
            stepUrl = urlObj.pathname
        }
        
        if (currentUrl === stepUrl) {
            // We're on the right page, show the step
            showTutorialStep(currentStepData)
        } else {
            // Navigate to the correct page (shouldn't happen often, but handle it)
            window.location.href = currentStepData.url
        }
    }
}

// Initialize tutorial on page load
document.addEventListener('DOMContentLoaded', function() {
    handleTutorialOnPageLoad()
})

