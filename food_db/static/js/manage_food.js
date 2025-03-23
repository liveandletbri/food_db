let currentUrl = window.location.href
let currentUrlDomain = currentUrl.split("/food/")[0]
const foodData = JSON.parse(document.getElementById('foodDataRaw').textContent);  // foodDataRaw is declared in manage_food.html, passed from views.py
let foodDataDict = {}
foodData.forEach(food => {
    foodDataDict[food.name] = {
        'category': food.category,
        'recipes': food.recipes,
    }
})
let highlightedStatsRow
let highlightedMergeRow
let mergeMode = false
let foodStatsHeader = document.getElementById('food_stats_header')
let foodStatsBody = document.getElementById('food_stats_body')
let foodStatsButtons = document.getElementById('food_stats_buttons')

let foodStatsMergeHeader = document.getElementById('food_stats_merge_header')
let foodStatsMergeBody = document.getElementById('food_stats_merge_body')

let foodStatsTemplate = `<h4>Used in these recipes:</h4>
<ul>
{recipeList}
</ul>`

let defaultMergeHeaderText = 'Select a food to merge with'
let defaultMergeButtonText = 'Merge with another'
let foodStatsMergeButton = `<button id="merge_food_button" class="food_stats_button" type="button" 
onclick="enterMergeMode()">${defaultMergeButtonText}</button><br><br>`

let badMergeTooltip = document.getElementById('cant_self_merge_tooltip')

function showHideTabs(){   
    $('#tabs li a:not(:first)').addClass('inactive');
    $('.tab_container').hide();
    $('.tab_container:first').show();
        
    $('#tabs li a').click(function() {
        var thisTabId = $(this).attr('id');
        if($(this).hasClass('inactive')){ //this is the start of our condition 
            $('#tabs li a').addClass('inactive');           
            $(this).removeClass('inactive');
            
            $('.tab_container').hide();
            $('#'+ thisTabId + '_content').fadeIn('slow');
        }
    });
}

function highlightStatsRow(event){
    targetElement = event.target
    if (targetElement.nodeName == "TD") {
        // Target the parent row so we can standardize the code below
        targetElement = targetElement.parentNode;   
    }
    if (highlightedStatsRow == targetElement) {
        // If clicking the already-highlighted row, un-highlight it and remove stats
        highlightedStatsRow.classList.remove('highlight_stats')
        highlightedStatsRow = null
        foodStatsHeader.innerText = 'Select a food'
        foodStatsBody.innerHTML = ''
        foodStatsButtons.innerHTML = ''
        resetMergeMode(false, '')
    } else {
        if (highlightedStatsRow) {
            // Un-highlight the different row
            highlightedStatsRow.classList.remove('highlight_stats')
        }
        // Highlight and set stats for this row
        targetElement.classList.add('highlight_stats')
        highlightedStatsRow = targetElement
        let food = targetElement.getAttribute('data-food')
        let category = targetElement.getAttribute('data-category')
        let recipes = Array.from(foodDataDict[food]['recipes'])
        let recipeHTML = recipes.map(rec => `<li><a href="${currentUrlDomain}/recipe/${rec.clean_key}">${rec.title}</a></li>`)
        foodStatsHeader.innerText = `${category}: ${food}`
        foodStatsBody.innerHTML = foodStatsTemplate.replace('{food}',food).replace('{category}',category).replace('{recipeList}',recipeHTML)
        foodStatsButtons.innerHTML = foodStatsMergeButton
    }
}

function enterMergeMode() {
    mergeMode = true
    foodStatsMergeHeader.innerText = defaultMergeHeaderText
}

function resetMergeMode(stillInMergeMode, headerText) {
    mergeMode = stillInMergeMode
    foodStatsMergeHeader.innerText = ''
    if (highlightedMergeRow) {
        highlightedMergeRow.classList.remove('highlight_merge')
        highlightedMergeRow = null
    }
    foodStatsMergeHeader.innerText = headerText
    foodStatsMergeBody.innerHTML = ''
    mergeButton.classList.remove('merge_selected')
    mergeButton.innerText = defaultMergeButtonText
}

function highlightMergeRow(event) {
    targetElement = event.target
    mergeButton = document.getElementById('merge_food_button')
    if (targetElement.nodeName == "TD") {
        // Target the parent row so we can standardize the code below
        targetElement = targetElement.parentNode;   
    }
    if (highlightedMergeRow == targetElement) {
        // If clicking the already-highlighted row, un-highlight it and remove stats
        resetMergeMode(true, defaultMergeHeaderText)
    } else if (highlightedStatsRow == targetElement) {
        // Clicked the stats row, which is highlighted blue. You can't merge into yourself!
        // showAndHideTooltip is defined in tooltip.js

        // badMergeTooltip.offsetTop = targetElement.offsetTop
        // badMergeTooltip.offsetLeft = targetElement.offsetLeft

        let targetRect = targetElement.getBoundingClientRect();

        console.log(targetRect.top)
        badMergeTooltip.style.left = `${targetRect.left}px`;
        badMergeTooltip.style.top = `${targetRect.top+80}px`;
        showAndHideTooltip(badMergeTooltip)
    } else {
        if (highlightedMergeRow) {
            // Un-highlight the different row
            highlightedMergeRow.classList.remove('highlight_merge')
        }
        // Modify merge button to indicate we're ready to merge
        mergeButton.classList.add('merge_selected')
        mergeButton.innerText = 'Merge foods'
        
        // Highlight and set stats for this row
        targetElement.classList.add('highlight_merge')
        highlightedMergeRow = targetElement
        let food = targetElement.getAttribute('data-food')
        let category = targetElement.getAttribute('data-category')
        let recipes = Array.from(foodDataDict[food]['recipes'])
        let recipeHTML = recipes.map(rec => `<li><a href="${currentUrlDomain}/recipe/${rec.clean_key}">${rec.title}</a></li>`)
        foodStatsMergeHeader.innerText = `${category}: ${food}`
        foodStatsMergeBody.innerHTML = foodStatsTemplate.replace('{food}',food).replace('{category}',category).replace('{recipeList}',recipeHTML)
    }
}

function handleFoodRowClick(event) {
    event.preventDefault()
    if (mergeMode == true) {
        highlightMergeRow(event)
    } else {
        highlightStatsRow(event)
    }
}

let rows = document.querySelectorAll('.manage_food_row')
rows.forEach(row => {
    row.addEventListener('click', function(event) {handleFoodRowClick(event)})
})

$(document).ready(showHideTabs)
