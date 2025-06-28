let emptyVideo = document.getElementById('video_empty')
emptyVideo.loop = true

let cookingModeContainer = document.getElementById('cooking_mode_container')
let cookingModeTitle = document.getElementById('cooking_mode_title')
let cookingModeSubtitle = document.getElementById('cooking_mode_subtitle')
let stepsTables = document.querySelectorAll('.steps_table')
let bottomStepsTable = stepsTables[stepsTables.length - 1]
let defaultBottomMargin = '100px'
bottomStepsTable.style.marginBottom = defaultBottomMargin


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
    bottomStepsTable.style.marginBottom = `150px`
    cookingModeTitle.innerText = 'Cooking Mode'
    cookingModeSubtitle.innerText = 'Your screen will stay awake while you cook 👨‍🍳🤌'

    cookingModeContainer.removeEventListener('click', enterCookingModeHandler)
    cookingModeContainer.addEventListener('click', exitCookingModeHandler)
}

async function exitCookingMode() {
    await tooltipResetAnimation()
    emptyVideo.pause()
    bottomStepsTable.style.marginBottom = defaultBottomMargin
    cookingModeTitle.innerText = 'Enable Cooking Mode'
    cookingModeSubtitle.innerText = ''

    cookingModeContainer.removeEventListener('click', exitCookingModeHandler)
    cookingModeContainer.addEventListener('click', enterCookingModeHandler)
}

const enterCookingModeHandler = () => enterCookingMode()
const exitCookingModeHandler = () => exitCookingMode()

cookingModeContainer.addEventListener('click', enterCookingModeHandler)