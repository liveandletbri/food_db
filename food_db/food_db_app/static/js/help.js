document.addEventListener('DOMContentLoaded', function() {
    let tutorialLinks = document.querySelectorAll('.tutorial_step_link')
    tutorialLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault()
            let stepId = this.getAttribute('data-step-id')
            if (typeof startTutorial === 'function') {
                startTutorial(stepId)
            }
        })
    })
})

