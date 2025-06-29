let emptyVideo = document.getElementById('video_empty')
emptyVideo.loop = true

let recipeHasChildren = JSON.parse(recipeHasChildrenRaw.textContent)

let cookingModeContainer = document.getElementById('cooking_mode_container')
let cookingModeTitle = document.getElementById('cooking_mode_title')
let cookingModeSubtitle = document.getElementById('cooking_mode_subtitle')
let defaultBottomMargin = '100px'
adjustBottomMargin(defaultBottomMargin)


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

async function enterCookingMode() {
    await tooltipResetAnimation()
    emptyVideo.play()
    adjustBottomMargin('150px')
    cookingModeTitle.innerText = 'Cooking Mode'
    cookingModeSubtitle.innerText = 'Your screen will stay awake while you cook 👨‍🍳🤌'

    cookingModeContainer.removeEventListener('click', enterCookingModeHandler)
    cookingModeContainer.addEventListener('click', exitCookingModeHandler)
}

async function exitCookingMode() {
    await tooltipResetAnimation()
    emptyVideo.pause()
    adjustBottomMargin(defaultBottomMargin)
    cookingModeTitle.innerText = 'Enable Cooking Mode'
    cookingModeSubtitle.innerText = ''

    cookingModeContainer.removeEventListener('click', exitCookingModeHandler)
    cookingModeContainer.addEventListener('click', enterCookingModeHandler)
}

const enterCookingModeHandler = () => enterCookingMode()
const exitCookingModeHandler = () => exitCookingMode()

cookingModeContainer.addEventListener('click', enterCookingModeHandler)