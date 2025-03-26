let currentUrl = window.location.href
let currentUrlDomain = currentUrl.split("/food/")[0]
let foodDataDict = getFoodData(document)

let highlightedStatsRow
let highlightedMergeRow
let mergeMode = false
let editMode = false
let originalFoodValue = null
let originalCategoryValue = null

let foodCategoryTable = document.getElementById('foods_categories_table')
let foodStatsHeader = document.getElementById('food_stats_header')
let foodStatsBody = document.getElementById('food_stats_body')

let foodNameSearch = document.getElementById('food_name_search_input')
let foodCategorySearch = document.getElementById('food_category_search_input')
let noCategorySearch = document.getElementById('no_category_search_input')

let deleteButton = document.getElementById('delete_food_button')
let mergeButton = document.getElementById('merge_food_button')
let cancelMergeButton = document.getElementById('cancel_merge_food_button')
let editButton = document.getElementById('edit_food_button')
let cancelEditButton = document.getElementById('cancel_edit_food_button')

let foodStatsMergeHeader = document.getElementById('food_stats_merge_header')
let foodStatsMergeBody = document.getElementById('food_stats_merge_body')
let badMergeTooltip = document.getElementById('cant_self_merge_tooltip')
let duplicateNameTooltip = document.getElementById('duplicate_name_tooltip')

let defaultMergeHeaderText = 'Select a food to merge with'
let defaultMergeButtonText = 'Merge with another'

let foodStatsTemplate = `<h4>Used in these recipes:</h4>
<ul>
{recipeList}
</ul>`
let emptyFoodStatsTemplate = '<h4 style="margin: 0;">Not used in any recipes</h4>'

function getFoodData(document) {
    // foodDataRaw is declared in manage_food.html, passed from views.py
    let foodData = JSON.parse(document.querySelector('#foodDataRaw').textContent)
    let returnDict = {}
    foodData.forEach((food, index) => {
        returnDict[food.name] = {
            'category': food.category,
            'recipes': food.recipes,
            'rowIndex': index + 1,   // The headers are row 0 in the table, so starting the index at 1
        }
    })
    return returnDict
}

function autoTextareaHeight(event) {
    element = event.target
    element.style.height = "5px";
    element.style.height = (element.scrollHeight+3)+"px";
}

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

function enterMergeMode() {
    mergeMode = true
    foodStatsMergeHeader.innerText = defaultMergeHeaderText
    cancelMergeButton.style.display = ''
    mergeButton = document.getElementById('merge_food_button')
    mergeButton.removeEventListener('click', enterMergeMode)
    editButton.style.display = 'none'
}

function enterEditMode() {
    editMode = true
    mergeButton.style.display = 'none'
    cancelEditButton.style.display = ''

    foodNameSearch.setAttribute('disabled', true)
    foodCategorySearch.setAttribute('disabled', true)

    let nameInput = highlightedStatsRow.querySelector('.food_name')
    nameInput.classList.remove('locked')
    nameInput.classList.add('unlocked')
    nameInput.removeAttribute('readonly')

    let categoryLabel = highlightedStatsRow.querySelector('.food_category_label')
    let categorySelect = highlightedStatsRow.querySelector('.food_category')
    categoryLabel.style.display = 'none'
    categorySelect.style.display = ''

    originalFoodValue = nameInput.value
    originalCategoryValue = categoryLabel.innerText

    editButton.removeEventListener('click', enterEditMode)
    editButton.addEventListener('click', submitEditsHandler)
    editButton.innerText = 'Save edits'
}

function resetEditMode(cancelEdits) {
    editMode = false
    mergeButton.style.display = ''
    editButton.style.display = ''
    cancelEditButton.style.display = 'none'

    foodNameSearch.removeAttribute('disabled')
    foodCategorySearch.removeAttribute('disabled')

    let nameInput = highlightedStatsRow.querySelector('.food_name')
    if (nameInput.classList.contains('unlocked')) {
        nameInput.classList.remove('unlocked')
        nameInput.classList.add('locked')
        nameInput.setAttribute('readonly', true)
    }

    let categoryLabel = highlightedStatsRow.querySelector('.food_category_label')
    let categorySelect = highlightedStatsRow.querySelector('.food_category')
    categoryLabel.style.display = ''
    categorySelect.style.display = 'none'

    editButton.removeEventListener('click', submitEditsHandler)
    editButton.addEventListener('click', enterEditMode)
    editButton.innerText = 'Edit row'

    if (cancelEdits) {
        highlightedStatsRow.querySelector('.food_name').value = originalFoodValue
        highlightedStatsRow.querySelector('.food_name').innerHTML = originalFoodValue
        originalFoodValue = null

        // no need to change any values for the Category since categoryLabel still holds the original value
        originalCategoryValue = null
    } else {
        originalFoodValue = null
        originalCategoryValue = null
        categoryLabel.innerText = categorySelect.value
    }
}

async function submitEdits() {
    let nameInput = highlightedStatsRow.querySelector('.food_name')
    let categorySelect = highlightedStatsRow.querySelector('.food_category')
    editButton.innerText = 'Saving edits...'
    editButton.setAttribute('disabled', true)
    let apiSuccess = await fetch(`${currentUrlDomain}/edit_food/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            original_food_name: originalFoodValue,
            new_food_name: nameInput.value,
            category_name: categorySelect.value,
        })
    })
    .then(function(response) {
        if ( response.status == 406 ) {
            // Reset edit button, display tooltip, then quit the function without resetting inputs or edit mode
            editButton.innerText = 'Save edits'
            editButton.removeAttribute('disabled')
            
            duplicateNameTooltip.style.left = `${highlightedStatsRow.offsetLeft}px`;
            duplicateNameTooltip.style.top = `${highlightedStatsRow.offsetTop + 330}px`;
            duplicateNameTooltip.innerText = duplicateNameTooltip.innerText.replace('{food}', nameInput.value)

            showAndHideTooltip(duplicateNameTooltip, 5000)
            return false
        } else if ( response.status == 200 ) {
            return true
        } else {
            return false
        }
    })
    
    if ( apiSuccess ) {
        // Doing this so I can use await, which must be at top-level (rather than
        // putting it under the .then function above)
        await reloadFoodCategoryTable()
        editButton.removeAttribute('disabled')
        resetEditMode(false, '')
        
        // Reloading the table un-highlights the row, so we re-highlight it by
        // faking a click event.
        let newHighlightedRowIndex = foodDataDict[nameInput.value]['rowIndex']
        let newHighlightedRow = foodCategoryTable.rows[newHighlightedRowIndex]
        let fakeEvent = {'target': newHighlightedRow}
        highlightStatsRow(fakeEvent)
    }
}

const submitEditsHandler = () => submitEdits()

function highlightStatsRow(event){
    targetElement = event.target
    let inputNodeNames = ['TEXTAREA', 'SELECT', 'SPAN']
    if (inputNodeNames.includes(targetElement.nodeName) && targetElement.classList.contains('unlocked')) {
        // Totally skip this function - do not change the highlights and stats if clicking an unlocked input 
        return
    } else if (editMode) {
        // Also skip this function while in edit mode
        return
    } else if (targetElement.nodeName == "TD") {
        // Target the parent row so we can standardize the code below
        targetElement = targetElement.parentNode
    } else if (inputNodeNames.includes(targetElement.nodeName)) {
        targetElement = targetElement.parentNode.parentNode
    }

    if (highlightedStatsRow == targetElement) {
        // If clicking the already-highlighted row, un-highlight it and remove stats
        highlightedStatsRow.classList.remove('highlight_stats')
        highlightedStatsRow = null
        foodStatsHeader.innerText = 'Select a food'
        foodStatsBody.innerHTML = ''
        mergeButton.style.display = 'none'
        editButton.style.display = 'none'
        deleteButton.style.display = 'none'
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
        if ( recipes.length > 0 ) {
            let recipeHTML = recipes.map(rec => `<li><a href="${currentUrlDomain}/recipe/${rec.clean_key}">${rec.title}</a></li>`)
            foodStatsBody.innerHTML = foodStatsTemplate.replace('{recipeList}',recipeHTML)
            deleteButton.style.display = 'none'
        } else {
            deleteButton.style.display = ''
            foodStatsBody.innerHTML = emptyFoodStatsTemplate
        }
        foodStatsHeader.innerText = `${category}: ${food}`
        mergeButton.style.display = ''
        mergeButton.addEventListener('click', enterMergeMode)
        editButton.style.display = ''
    }
}

async function reloadFoodCategoryTable(params) {
    if ( params == undefined ) {
        params = ''
    } else {
        params = `?${params}`
    }
    let response = await fetch(`/food${params}`, {
        method: "GET",
    })
    .then(function(response) {
        // The response is a Response instance.
        return response.text();
    })
    
    // Render the response text as an html element, then extract the new search result div from its innards
    let responseHtml = document.createElement('html')
    responseHtml.innerHTML = response
    foodDataDict = getFoodData(responseHtml)
    let responseFoodCategoryTable = responseHtml.querySelector('#foods_categories_table')

    // Frankenstein it right into our existing page
    foodCategoryTable.innerHTML = responseFoodCategoryTable.innerHTML

    assignRowListeners()
}


async function mergeFoods(event) {
    event.preventDefault()
    firstFood = highlightedStatsRow.getAttribute('data-food')
    secondFood = highlightedMergeRow.getAttribute('data-food')
    let confirmText = `Are you sure you want to merge "${firstFood}" with "${secondFood}"? All recipes using "${firstFood}" will be updated to instead use "${secondFood}", and "${firstFood}" will disappear from the database.`
    let confirmMerge = confirm(confirmText)
    if (confirmMerge) {
        let apiSuccess = await fetch(`${currentUrlDomain}/merge_foods/`, {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                food_to_merge: firstFood,
                food_to_keep: secondFood,
            })
        })
        .then(function(response) {
            if (! response.status == 200) {
                console.log("d'oh!")
                return false
            } else {
                return true
            }
        })
        if ( apiSuccess ) {
            // Doing this so I can use await, which must be at top-level (rather than
            // putting it under the .then function above)
            await reloadFoodCategoryTable()
            resetMergeMode(false, '')
            
            // The merge row should now be highlighted, but using the highlightedMergeRow 
            // variable won't work since that is from before reloadFoodCategoryTable. 
            // Instead we'll find it by index.
            let newHighlightedRowIndex = foodDataDict[secondFood]['rowIndex']
            let newHighlightedRow = foodCategoryTable.rows[newHighlightedRowIndex]
            let fakeEvent = {'target': newHighlightedRow}
            highlightStatsRow(fakeEvent)
        }
    }
}

const mergeFoodsHandler = (event) => mergeFoods(event)

function resetMergeMode(stillInMergeMode, headerText) {
    mergeMode = stillInMergeMode
    if (!stillInMergeMode) {
        // Remove cancel button and show edit button again
        cancelMergeButton.style.display = 'none'
        if (highlightedStatsRow) {
            editButton.style.display = ''
        }
    }
    foodStatsMergeHeader.innerText = ''
    if (highlightedMergeRow) {
        highlightedMergeRow.classList.remove('highlight_merge')
        highlightedMergeRow = null
    }
    foodStatsMergeHeader.innerText = headerText
    foodStatsMergeBody.innerHTML = ''
    mergeButton.classList.remove('merge_selected')
    mergeButton.innerText = defaultMergeButtonText
    mergeButton.removeEventListener('click', mergeFoodsHandler)
    mergeButton.addEventListener('click', enterMergeMode)
}

async function deleteFood() {
    let foodName = highlightedStatsRow.getAttribute('data-food')
    let confirmText = `Are you sure you want to delete "${foodName}"? No recipes are using it so no recipes will be impacted.`
    let confirmDelete = confirm(confirmText)
    if (confirmDelete) {
        deleteButton.innerText = 'Deleting...'
        deleteButton.setAttribute('disabled', true)
        let apiSuccess = await fetch(`${currentUrlDomain}/delete_food/`, {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                food_name: foodName,
            })
        })
        .then(function(response) {
            if (! response.status == 200) {
                console.log("d'oh!")
                return false
            } else {
                return true
            }
        })

        if ( apiSuccess ) {
            await reloadFoodCategoryTable()

            deleteButton.innerText = 'Delete food'
            deleteButton.removeAttribute('disabled')
            // This is my cheater way of resetting the highlighting variables and stats table.
            let fakeEvent = {'target': highlightedStatsRow}  // this row doesn't exist in the table anymore, but I still have it in this variable!
            highlightStatsRow(fakeEvent)
        }
    }
}

function highlightMergeRow(event) {
    targetElement = event.target
    if (targetElement.nodeName == "TD") {
        // Target the parent row so we can standardize the code below
        targetElement = targetElement.parentNode
    } else if (targetElement.nodeName == "TEXTAREA") {
        targetElement = targetElement.parentNode.parentNode
    }
    if (highlightedMergeRow == targetElement) {
        // If clicking the already-highlighted row, un-highlight it and remove stats
        resetMergeMode(true, defaultMergeHeaderText)
    } else if (highlightedStatsRow == targetElement) {
        // Clicked the stats row, which is highlighted blue. You can't merge into yourself!
        // showAndHideTooltip is defined in tooltip.js

        badMergeTooltip.style.left = `${targetElement.offsetLeft}px`;
        badMergeTooltip.style.top = `${targetElement.offsetTop + 330}px`;
        showAndHideTooltip(badMergeTooltip)
    } else {
        if (highlightedMergeRow) {
            // Un-highlight the different row
            highlightedMergeRow.classList.remove('highlight_merge')
        }
        // Modify merge button to indicate we're ready to merge
        mergeButton.classList.add('merge_selected')
        mergeButton.innerText = 'Merge foods'
        mergeButton.addEventListener('click', mergeFoodsHandler)
        
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

async function searchFilter() {
    // An async 'form submission' rather than an actual form submission that loads
    // a new page. Retrieves results from the /search URL (this page's URL) with a
    // GET, then extracts HTML from the result and patches it onto the current page's
    // HTML, rather than actually moving to a new URL. It's pretty brute force but
    // hey, what are side projects for?

    let foodNameSearchValue = foodNameSearch.value
    let foodCategorySearchValue = foodCategorySearch.value
    let noCategorySearchValue = noCategorySearch.checked

    let params = {
        name: foodNameSearchValue,
        category: foodCategorySearchValue,
        no_category: noCategorySearchValue,
    }

    // Format params as URL query string
    let param_string = Object.entries(params)
        .map(([k, v]) => (`${k}=${v}`))
        .join('&')

    console.log(`Performing GET with params: ${param_string}`)

    await reloadFoodCategoryTable(param_string)
    
    // If in merge mode, preserve the original highlighted row even if it's
    // not in the search results - in other words, always show the stats and don't
    // set highlightedStatsRow back to null. If the row disappears from the search
    // results, its stats stay visible. When it appears back in the search results,
    // highlight it again.
    if ( mergeMode && highlightedStatsRow ) {
        let oldHighlightedFoodName = highlightedStatsRow.getAttribute('data-food')
        if ( oldHighlightedFoodName in foodDataDict ) {
            let newHighlightedRowIndex = foodDataDict[oldHighlightedFoodName]['rowIndex']
            let newHighlightedRow = foodCategoryTable.rows[newHighlightedRowIndex]
            let fakeEvent = {'target': newHighlightedRow}
            highlightStatsRow(fakeEvent)
        }
    }

    // If in merge mode and have selected a merge highlight row
    // Un-highlight the merge row if it's no longer in the search results
    if ( mergeMode && highlightedMergeRow ) {
        let oldHighlightedFoodName = highlightedMergeRow.getAttribute('data-food')
        if ( oldHighlightedFoodName in foodDataDict ) {
            let newHighlightedRowIndex = foodDataDict[oldHighlightedFoodName]['rowIndex']
            let newHighlightedRow = foodCategoryTable.rows[newHighlightedRowIndex]
            let fakeEvent = {'target': newHighlightedRow}
            highlightMergeRow(fakeEvent)
        } else {
            // Un-highlight by passing the existing row into the highlight function
            let fakeEvent = {'target': highlightedMergeRow}
            highlightMergeRow(fakeEvent)
        }
    }

    // If NOT in merge mode and just have a highlighted stats row
    // Un-highlight the stats row if it's no longer in the search results
    if ( ! mergeMode && highlightedStatsRow ) {
        let oldHighlightedFoodName = highlightedStatsRow.getAttribute('data-food')
        if ( oldHighlightedFoodName in foodDataDict ) {
            let newHighlightedRowIndex = foodDataDict[oldHighlightedFoodName]['rowIndex']
            let newHighlightedRow = foodCategoryTable.rows[newHighlightedRowIndex]
            let fakeEvent = {'target': newHighlightedRow}
            highlightStatsRow(fakeEvent)
        } else {
            // Un-highlight by passing the existing row into the highlight function
            let fakeEvent = {'target': highlightedStatsRow}
            highlightStatsRow(fakeEvent)
        }
    }
    
}


function assignRowListeners() {
    let rows = document.querySelectorAll('.manage_food_row')
    rows.forEach(row => {
        row.addEventListener('click', function(event) {handleFoodRowClick(event)})
    })

    let inputs = document.querySelectorAll('.food_name')
    inputs.forEach(textarea => {
        let fakeEvent = {'target': textarea}
        autoTextareaHeight(fakeEvent)
        textarea.addEventListener('change', function(event) {autoTextareaHeight(event)})
    })

    
}

assignRowListeners()
$(document).ready(showHideTabs)
editButton.addEventListener('click', enterEditMode)

foodNameSearch.addEventListener("input", searchFilter)
foodCategorySearch.addEventListener("input", searchFilter)
noCategorySearch.addEventListener("input", searchFilter)