let emptyVideo = document.getElementById('video_empty')
emptyVideo.loop = true

let cookingModeContainer = document.getElementById('cooking_mode_container')
let cookingModeTitle = document.getElementById('cooking_mode_title')
let cookingModeSubtitle = document.getElementById('cooking_mode_subtitle')
let stepsTable = document.getElementById('steps_table')
let defaultBottomMargin = '100px'
stepsTable.style.marginBottom = defaultBottomMargin


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
    stepsTable.style.marginBottom = `150px`
    cookingModeTitle.innerText = 'Cooking Mode'
    cookingModeSubtitle.innerText = 'Your screen will stay awake while you cook 👨‍🍳🤌'

    cookingModeContainer.removeEventListener('click', enterCookingModeHandler)
    cookingModeContainer.addEventListener('click', exitCookingModeHandler)
}

async function exitCookingMode() {
    await tooltipResetAnimation()
    emptyVideo.pause()
    stepsTable.style.marginBottom = defaultBottomMargin
    cookingModeTitle.innerText = 'Enable Cooking Mode'
    cookingModeSubtitle.innerText = ''

    cookingModeContainer.removeEventListener('click', exitCookingModeHandler)
    cookingModeContainer.addEventListener('click', enterCookingModeHandler)
}

function highlightOnHover() {
    cookingModeContainer.style.background = '#86f9c1'
    cookingModeContainer.style.color = '#161616'
    
}
function unHighlightOnExit() {
    cookingModeContainer.style.background = '#3cc382'
    cookingModeContainer.style.color = 'white'
}


const enterCookingModeHandler = () => enterCookingMode()
const exitCookingModeHandler = () => exitCookingMode()

cookingModeContainer.addEventListener('mouseenter', highlightOnHover)
cookingModeContainer.addEventListener('mouseleave', unHighlightOnExit)
cookingModeContainer.addEventListener('click', enterCookingModeHandler)