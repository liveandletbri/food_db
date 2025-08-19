let emptyVideo = document.getElementById('video_empty')
emptyVideo.loop = true

let recipeHasChildren = JSON.parse(recipeHasChildrenRaw.textContent)

let cookingModeContainer = document.getElementById('cooking_mode_container')
let cookingModeTitle = document.getElementById('cooking_mode_title')
let cookingModeSubtitle = document.getElementById('cooking_mode_subtitle')
let defaultBottomMargin = '100px'
adjustBottomMargin(defaultBottomMargin)

// Add cooking mode class to body for CSS targeting
let body = document.body

function adjustBottomMargin(marginPx) {
    if (recipeHasChildren) {
        let collapsibleDetails = document.querySelectorAll('.child_recipe_details')
        let bottomCollapsibleDetail = collapsibleDetails[collapsibleDetails.length - 1]
        bottomCollapsibleDetail.style.marginBottom = marginPx
    } else {
        let stepsTables = document.querySelectorAll('.steps_table')
        let bottomStepsTable = stepsTables[stepsTables.length - 1]
        bottomStepsTable.style.marginBottom = marginPx
    }
}

function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function tooltipResetAnimation() {
    setTimeout(hideToolTip, 200, cookingModeContainer)
    setTimeout(showToolTip, 800, cookingModeContainer)
    await delay(800)
}

function resetAllCheckboxes() {
    // Uncheck all ingredient and step checkboxes
    const ingredientCheckboxes = document.querySelectorAll('.ingredient-checkbox')
    const stepCheckboxes = document.querySelectorAll('.step-checkbox')
    
    ingredientCheckboxes.forEach(checkbox => {
        checkbox.checked = false
        const ingredientCell = checkbox.closest('td')
        ingredientCell.classList.remove('checked-ingredient')
    })
    
    stepCheckboxes.forEach(checkbox => {
        checkbox.checked = false
        const stepCell = checkbox.closest('td')
        stepCell.classList.remove('checked-step')
    })
}

function setupCheckboxEventListeners() {
    // Add event listeners for ingredient checkboxes
    const ingredientCheckboxes = document.querySelectorAll('.ingredient-checkbox')
    ingredientCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const ingredientCell = this.closest('td')
            if (this.checked) {
                ingredientCell.classList.add('checked-ingredient')
            } else {
                ingredientCell.classList.remove('checked-ingredient')
            }
        })
    })
    
    // Add event listeners for step checkboxes
    const stepCheckboxes = document.querySelectorAll('.step-checkbox')
    stepCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const stepRow = this.closest('tr')
            if (this.checked) {
                stepRow.classList.add('checked-step')
            } else {
                stepRow.classList.remove('checked-step')
            }
        })
    })
    
    // Add click handlers for ingredient cells
    const ingredientCells = document.querySelectorAll('.recipe_detail_ingredient_food')
    ingredientCells.forEach(cell => {
        const ingredientRow = cell.closest('tr')
        ingredientRow.addEventListener('click', function(e) {
            // Don't trigger if clicking on the checkbox itself
            if (e.target.type === 'checkbox') return

            // Don't trigger if clicking on the ingredient category cell
            if (e.target.classList.contains('recipe_detail_ingredient_category_td')) return
            
            const checkbox = this.querySelector('.ingredient-checkbox')
            if (checkbox) {
                checkbox.checked = !checkbox.checked
                checkbox.dispatchEvent(new Event('change'))
            }
        })
    })
    
    // Add click handlers for step cells
    const stepCells = document.querySelectorAll('.step_description_text')
    stepCells.forEach(cell => {
        const stepRow = cell.closest('tr')
        stepRow.addEventListener('click', function(e) {
            // Don't trigger if clicking on the checkbox itself
            if (e.target.type === 'checkbox') return
            
            const checkbox = this.querySelector('.step-checkbox')
            if (checkbox) {
                checkbox.checked = !checkbox.checked
                checkbox.dispatchEvent(new Event('change'))
            }
        })
    })
}

async function enterCookingMode() {
    await tooltipResetAnimation()
    emptyVideo.play()
    adjustBottomMargin('150px')
    cookingModeTitle.innerText = 'Cooking Mode'
    cookingModeSubtitle.innerText = 'Your screen will stay awake while you cook 👨‍🍳🤌'
    
    // Add cooking mode class to body
    body.classList.add('cooking-mode-active')
    
    // Reset all checkboxes when entering cooking mode
    resetAllCheckboxes()
    
    // Setup checkbox event listeners
    setupCheckboxEventListeners()

    cookingModeContainer.removeEventListener('click', enterCookingModeHandler)
    cookingModeContainer.addEventListener('click', exitCookingModeHandler)
}

async function exitCookingMode() {
    await tooltipResetAnimation()
    emptyVideo.pause()
    adjustBottomMargin(defaultBottomMargin)
    cookingModeTitle.innerText = 'Enable Cooking Mode'
    cookingModeSubtitle.innerText = ''
    
    // Remove cooking mode class from body
    body.classList.remove('cooking-mode-active')
    
    // Reset all checkboxes when exiting cooking mode
    resetAllCheckboxes()

    cookingModeContainer.removeEventListener('click', exitCookingModeHandler)
    cookingModeContainer.addEventListener('click', enterCookingModeHandler)
}

const enterCookingModeHandler = () => enterCookingMode()
const exitCookingModeHandler = () => exitCookingMode()

cookingModeContainer.addEventListener('click', enterCookingModeHandler)