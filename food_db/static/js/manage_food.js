let currentUrl = window.location.href
let currentUrlDomain = currentUrl.split("/food/")[0]
let [foodDataDict, categoryDataDict] = getFoodData(document);

// Operational variables
let highlightedStatsRow
let highlightedMergeRow
let mergeMode = false
let editMode = false
let originalFoodValue = null
let originalCategoryValue = null

// Tab-dependent variables
let activeTab

// Food tab objects
let foodCategoryTable = document.getElementById('foods_categories_table')
let foodStatsHeader = document.getElementById('food_stats_header')
let foodStatsBody = document.getElementById('food_stats_body')
let foodResultCount = document.getElementById('food_result_count')

let foodNameSearch = document.getElementById('food_name_search_input')
let foodCategorySearch = document.getElementById('food_category_search_input')
let noCategorySearch = document.getElementById('no_category_search_input')
let noRecipeSearch = document.getElementById('no_recipe_search_input')

let foodDeleteButton = document.getElementById('delete_food_button')
let foodMergeButton = document.getElementById('merge_food_button')
let foodCancelMergeButton = document.getElementById('cancel_merge_food_button')
let foodEditButton = document.getElementById('edit_food_button')
let foodCancelEditButton = document.getElementById('cancel_edit_food_button')

let foodStatsMergeHeader = document.getElementById('food_stats_merge_header')
let foodStatsMergeBody = document.getElementById('food_stats_merge_body')
let foodBadMergeTooltip = document.getElementById('cant_self_merge_food_tooltip')
let foodDuplicateNameTooltip = document.getElementById('duplicate_food_name_tooltip')

// Category tab objects
let categoryTable = document.getElementById('categories_table')
let categoryStatsHeader = document.getElementById('category_stats_header')
let categoryStatsBody = document.getElementById('category_stats_body')
let categoryResultCount = document.getElementById('category_result_count')

let categoryNameSearch = document.getElementById('category_name_search_input')
let noFoodSearch = document.getElementById('no_food_search_input')

let categoryDeleteButton = document.getElementById('delete_category_button')
let categoryMergeButton = document.getElementById('merge_category_button')
let categoryCancelMergeButton = document.getElementById('cancel_merge_category_button')
let categoryEditButton = document.getElementById('edit_category_button')
let categoryCancelEditButton = document.getElementById('cancel_edit_category_button')

let categoryStatsMergeHeader = document.getElementById('category_stats_merge_header')
let categoryStatsMergeBody = document.getElementById('category_stats_merge_body')
let categoryBadMergeTooltip = document.getElementById('cant_self_merge_category_tooltip')
let categoryDuplicateNameTooltip = document.getElementById('duplicate_category_name_tooltip')

// Variables for filling out HTML
let defaultFoodMergeHeaderText = 'Select a food to merge with'
let defaultCategoryMergeHeaderText = 'Select a category to merge with'
let defaultMergeButtonText = 'Merge with another'

let foodStatsTemplate = `<h4>Used in these recipes:</h4>
<ul>
{statsList}
</ul>`
let emptyFoodStatsTemplate = '<h4 style="margin: 0;">Not used in any recipes</h4>'

let categoryStatsTemplate = `<h4>Assigned to these foods:</h4>
<ul>
{statsList}
</ul>`
let emptyCategoryStatsTemplate = '<h4 style="margin: 0;">Not assigned to any foods</h4>'

function getFoodData(document) {
    // foodDataRaw and categoryDataRaw are declared in manage_food.html, passed from views.py
    let foodData = JSON.parse(document.querySelector('#foodDataRaw').textContent)
    let categoryData = JSON.parse(document.querySelector('#categoryDataRaw').textContent)

    let returnFoodDict = {}
    let returnCategoryDict = {}

    foodData.forEach((food, index) => {
        returnFoodDict[food.name] = {
            'category': food.category,
            'recipes': food.recipes,
            'rowIndex': index + 1,   // The headers are row 0 in the table, so starting the index at 1
        }
    })

    categoryData.forEach((cat, index) => {
        returnCategoryDict[cat.name] = {
            'foods': cat.foods,
            'rowIndex': index + 1,   // The headers are row 0 in the table, so starting the index at 1
        }
    })
    return [returnFoodDict, returnCategoryDict]
}

function autoTextareaHeight(event) {
    element = event.target
    element.style.height = "5px";
    element.style.height = (element.scrollHeight+3)+"px";
}

function showHideTabs(){   
    // on page load, show first tab and hide the other
    $('#tabs li a:not(:first)').addClass('inactive');
    $('.tab_container').hide();
    $('.tab_container:first').show();
    activeTab = 'food'  // food tab is the first tab
    
    // actions when a tab is clicked
    $('#tabs li a').click(function() {
        var thisTabId = $(this).attr('id');

        // if the tab was inactive, make it active and hide the old tab
        if($(this).hasClass('inactive')){ 
            // first, clear search inputs and reset tables
            foodNameSearch.value = ''
            foodCategorySearch.value = ''
            categoryNameSearch.value = ''
            noCategorySearch.checked = false
            noRecipeSearch.checked = false
            noFoodSearch.checked = false
            searchFilter()  // this is the reason this is first - this async function is called without await


            // perform the tab swap
            $('#tabs li a').addClass('inactive');           
            $(this).removeClass('inactive');
            
            $('.tab_container').hide();
            $('#'+ thisTabId + '_content').fadeIn('slow');
            
            // reset highlighting and editing variables
            resetEditMode(true)
            resetMergeMode(false, '')
            hideAllButtons()
            if ( highlightedStatsRow ) {
                // un-highlight stats row
                unHighlightStatsRow()
            }
            if ( highlightedMergeRow ) {
                // un-highlight merge row
                resetMergeMode(true, defaultHeaderText)
            }
            // fix row heights
            autoHeightAllRows()

            // set the new "active tab" to be this tab
            activeTab = thisTabId.split('_')[0]  // set the value to be 'food' or 'category'
        }
    });
}

function hideAllButtons () {
    foodDeleteButton.style.display = 'none'
    foodMergeButton.style.display = 'none'
    foodCancelMergeButton.style.display = 'none'
    foodEditButton.style.display = 'none'
    foodCancelEditButton.style.display = 'none'

    categoryDeleteButton.style.display = 'none'
    categoryMergeButton.style.display = 'none'
    categoryCancelMergeButton.style.display = 'none'
    categoryEditButton.style.display = 'none'
    categoryCancelEditButton.style.display = 'none'
}

function enterMergeMode() {
    mergeMode = true
    let header
    let mergeButton
    let cancelButton
    if ( activeTab == 'food') {
        header = foodStatsMergeHeader
        mergeButton = foodMergeButton
        editButton = foodEditButton
        cancelButton = foodCancelMergeButton
    } else {
        header = categoryStatsMergeHeader
        mergeButton = categoryMergeButton
        editButton = categoryEditButton
        cancelButton = categoryCancelMergeButton
    }
    header.innerText = defaultFoodMergeHeaderText
    cancelButton.style.display = ''
    mergeButton = document.getElementById('merge_food_button')
    mergeButton.removeEventListener('click', enterMergeMode)
    editButton.style.display = 'none'
}

function enterEditMode() {
    editMode = true
    let header
    let mergeButton
    let editButton
    let cancelButton
    let cancelEditButton
    if ( activeTab == 'food') {
        header = foodStatsMergeHeader
        mergeButton = foodMergeButton
        editButton = foodEditButton
        cancelButton = foodCancelMergeButton
        cancelEditButton = foodCancelEditButton

        foodNameSearch.setAttribute('disabled', true)
        foodCategorySearch.setAttribute('disabled', true)
    } else {
        header = categoryStatsMergeHeader
        mergeButton = categoryMergeButton
        editButton = categoryEditButton
        cancelButton = categoryCancelMergeButton
        cancelEditButton = categoryCancelEditButton

        categoryNameSearch.setAttribute('disabled', true)
    }
    mergeButton.style.display = 'none'
    cancelEditButton.style.display = ''

    let nameInput = highlightedStatsRow.querySelector('.food_name')  // despite being called "food name", this is actually also used in the category tab
    nameInput.classList.remove('locked')
    nameInput.classList.add('unlocked')
    nameInput.removeAttribute('readonly')

    if ( activeTab == 'food' ) {
        let categoryLabel = highlightedStatsRow.querySelector('.food_category_label')
        let categorySelect = highlightedStatsRow.querySelector('.food_category')
        categoryLabel.style.display = 'none'
        categorySelect.style.display = ''
        originalFoodValue = nameInput.value
        originalCategoryValue = categoryLabel.innerText
    } else {
        originalCategoryValue = nameInput.value
    }

    editButton.removeEventListener('click', enterEditMode)
    editButton.addEventListener('click', submitEditsHandler)
    editButton.innerText = 'Save edits'
}

function resetEditMode(cancelEdits) {
    let wasInEditMode = editMode
    editMode = false

    let header
    let mergeButton
    let editButton
    let cancelButton
    let cancelEditButton
    if ( activeTab == 'food') {
        header = foodStatsMergeHeader
        mergeButton = foodMergeButton
        editButton = foodEditButton
        cancelButton = foodCancelMergeButton
        cancelEditButton = foodCancelEditButton

        foodNameSearch.removeAttribute('disabled')
        foodCategorySearch.removeAttribute('disabled')
    } else {
        header = categoryStatsMergeHeader
        mergeButton = categoryMergeButton
        editButton = categoryEditButton
        cancelButton = categoryCancelMergeButton
        cancelEditButton = categoryCancelEditButton

        categoryNameSearch.removeAttribute('disabled')
    }


    mergeButton.style.display = ''
    editButton.style.display = ''
    cancelEditButton.style.display = 'none'

    if ( wasInEditMode ) {
        let nameInput = highlightedStatsRow.querySelector('.food_name')  // Again, works on both tabs
        if (nameInput.classList.contains('unlocked')) {
            nameInput.classList.remove('unlocked')
            nameInput.classList.add('locked')
            nameInput.setAttribute('readonly', true)
        }

        let categoryLabel = highlightedStatsRow.querySelector('.food_category_label')
        let categorySelect = highlightedStatsRow.querySelector('.food_category')

        if ( activeTab == 'food' ) {
            categoryLabel.style.display = ''
            categorySelect.style.display = 'none'
        }

        editButton.removeEventListener('click', submitEditsHandler)
        editButton.addEventListener('click', enterEditMode)
        editButton.innerText = 'Edit row'

        if ( cancelEdits && activeTab == 'food' ) {
            highlightedStatsRow.querySelector('.food_name').value = originalFoodValue
            highlightedStatsRow.querySelector('.food_name').innerHTML = originalFoodValue
            // when on food tab, no need to reset any values for the Category since categoryLabel
            // still holds the original value
        } else if ( cancelEdits && activeTab == 'category' ) {
            highlightedStatsRow.querySelector('.food_name').value = originalCategoryValue
            highlightedStatsRow.querySelector('.food_name').innerHTML = originalCategoryValue
        } else if ( ! cancelEdits && activeTab == 'food' ) {
            // If saving edits, update categoryLabel when on food tab
            categoryLabel.innerText = categorySelect.value
        }
    }
    originalFoodValue = null
    originalCategoryValue = null
}

async function submitEdits() {
    let nameInput = highlightedStatsRow.querySelector('.food_name')
    let categorySelect
    let apiUrl
    let apiParams
    let editButton
    let tooltip
    let dataDict
    let table

    if ( activeTab == 'food' ) {
        categorySelect = highlightedStatsRow.querySelector('.food_category')
        apiUrl = 'edit_food'
        apiParams = {
            original_food_name: originalFoodValue,
            new_food_name: nameInput.value,
            category_name: categorySelect.value,
        }
        editButton = foodEditButton
        tooltip = foodDuplicateNameTooltip
        table = foodCategoryTable
    } else {
        apiUrl = 'edit_food_category'
        apiParams = {
            original_category_name: originalCategoryValue,
            new_category_name: nameInput.value,
        }
        editButton = categoryEditButton
        tooltip = categoryDuplicateNameTooltip
        table = categoryTable
    }

    editButton.innerText = 'Saving edits...'
    editButton.setAttribute('disabled', true)
    let apiSuccess = await fetch(`${currentUrlDomain}/${apiUrl}/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(apiParams)
    })
    .then(function(response) {
        if ( response.status == 406 ) {
            // Reset edit button, display tooltip, then quit the function without resetting inputs or edit mode
            editButton.innerText = 'Save edits'
            editButton.removeAttribute('disabled')
            
            tooltip.innerText = tooltip.innerText.replace('{this}', nameInput.value)
            positionTooltip(tooltip, highlightedStatsRow)  // positionTooltip defined in tooltip.js

            showAndHideTooltip(tooltip, 5000)
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
        await searchFilter()
        if ( activeTab == 'food' ) {
            dataDict = foodDataDict
        } else {
            dataDict = categoryDataDict
        }
        editButton.removeAttribute('disabled')
        resetEditMode(false, '')
        
        // Reloading the table un-highlights the row, so we re-highlight it by
        // faking a click event.
        let newHighlightedRowIndex = dataDict[nameInput.value]['rowIndex']
        let newHighlightedRow = table.rows[newHighlightedRowIndex]
        let fakeEvent = {'target': newHighlightedRow}
        highlightStatsRow(fakeEvent)
    }
}

const submitEditsHandler = () => submitEdits()

function unHighlightStatsRow() {
    highlightedStatsRow.classList.remove('highlight_stats');
    highlightedStatsRow = null;
    
    let statsHeader
    let statsBody
    if ( activeTab == 'food' ) {
        statsHeader = foodStatsHeader
        statsBody = foodStatsBody
    } else {
        statsHeader = categoryStatsHeader
        statsBody = categoryStatsBody
    }
    statsHeader.innerText = `Select a ${activeTab}`;
    statsBody.innerHTML = '';
    hideAllButtons();
    resetMergeMode(false, '');
}

function highlightStatsRow(event){
    targetElement = event.target
    let inputNodeNames = ['TEXTAREA', 'SELECT', 'SPAN', 'LABEL']
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

    let statsHeader
    let statsBody
    let statsTemplate
    let emptyStatsTemplate
    let mergeButton
    let editButton
    let deleteButton

    if ( activeTab=='food' ) {
        statsHeader = foodStatsHeader
        statsBody = foodStatsBody
        statsTemplate = foodStatsTemplate
        emptyStatsTemplate = emptyFoodStatsTemplate
        mergeButton = foodMergeButton
        editButton = foodEditButton
        deleteButton = foodDeleteButton
    } else {
        statsHeader = categoryStatsHeader
        statsBody = categoryStatsBody
        statsTemplate = categoryStatsTemplate
        emptyStatsTemplate = emptyCategoryStatsTemplate
        mergeButton = categoryMergeButton
        editButton = categoryEditButton
        deleteButton = categoryDeleteButton
    }

    if (highlightedStatsRow == targetElement) {
        // If clicking the already-highlighted row, un-highlight it and remove stats
        unHighlightStatsRow()
    } else {
        if (highlightedStatsRow) {
            // Un-highlight the different row
            highlightedStatsRow.classList.remove('highlight_stats')
        }
        // Highlight and set stats for this row
        targetElement.classList.add('highlight_stats')
        highlightedStatsRow = targetElement
        
        let food
        let category
        let statsList
        if ( activeTab=='food' ) {
            food = targetElement.getAttribute('data-food')
            category = targetElement.getAttribute('data-category')
            statsList = Array.from(foodDataDict[food]['recipes'])
            statsHeader.innerText = `${category}: ${food}`;
            if ( statsList.length > 0 ) {
                let listItemHTML = statsList.map(rec => `<li style="padding-bottom: 10px;"><a href="${currentUrlDomain}/recipe/${rec.clean_key}">${rec.title}</a></li>`).join('');
                statsBody.innerHTML = statsTemplate.replace('{statsList}', listItemHTML);
            }
        } else {
            category = targetElement.getAttribute('data-category')
            statsList = Array.from(categoryDataDict[category]['foods'])
            statsHeader.innerText = category;
            if ( statsList.length > 0 ) {
                let listItemHTML = statsList.map(food => `<li style="padding-bottom: 5px;">${food}</li>`).join('');
                statsBody.innerHTML = statsTemplate.replace('{statsList}', listItemHTML);
            }
        }

        if ( statsList.length > 0 ) {
            deleteButton.style.display = 'none';
        } else {
            deleteButton.style.display = '';
            statsBody.innerHTML = emptyStatsTemplate;
        }
        mergeButton.style.display = '';
        mergeButton.addEventListener('click', enterMergeMode);
        if ( ! mergeMode ) {
            editButton.style.display = '';
        }
    }
}

async function reloadDataTables(params) {
    if ( params == undefined ) {
        params = ''
    } else {
        params = `?${params}`
    }
    let apiResponse = await fetch(`/food/${params}`, {
        method: "GET",
    })
    .then(function(response) {
        // The response is a Response instance.
        return response.text();
    })
    
    // Semicolons were necessary here, I think because of the line that starts with []

    // Render the response text as an html element, then extract the new search result div from its innards
    let responseHtml = document.createElement('html');
    responseHtml.innerHTML = apiResponse;
    [foodDataDict, categoryDataDict] = getFoodData(responseHtml);
    let responseFoodCategoryTable = responseHtml.querySelector('#foods_categories_table');
    let responseFoodResultCount = responseHtml.querySelector('#food_result_count');
    let responseCategoryTable = responseHtml.querySelector('#categories_table');
    let responseCategoryResultCount = responseHtml.querySelector('#category_result_count');

    // Frankenstein it right into our existing page
    foodCategoryTable.innerHTML = responseFoodCategoryTable.innerHTML;
    foodResultCount.innerHTML = responseFoodResultCount.innerHTML;
    categoryTable.innerHTML = responseCategoryTable.innerHTML;
    categoryResultCount.innerHTML = responseCategoryResultCount.innerHTML;

    assignRowListeners()
}


async function mergeFoods(event) {
    event.preventDefault()
    let firstThing
    let secondThing
    let confirmText
    let apiUrl
    let apiParms
    let dataDict
    let table

    if ( activeTab == 'food' ) {
        firstThing = highlightedStatsRow.getAttribute('data-food')
        secondThing = highlightedMergeRow.getAttribute('data-food')
        confirmText = `Are you sure you want to merge "${firstThing}" with "${secondThing}"? All recipes using "${firstThing}" will be updated to instead use "${secondThing}", and "${firstThing}" will disappear from the database.`
        apiUrl = 'merge_foods'
        apiParms = {
            food_to_merge: firstThing,
            food_to_keep: secondThing,
        }
    } else {
        firstThing = highlightedStatsRow.getAttribute('data-category')
        secondThing = highlightedMergeRow.getAttribute('data-category')
        confirmText = `Are you sure you want to merge "${firstThing}" with "${secondThing}"? All foods assigned to "${firstThing}" will be updated to instead be assigned to "${secondThing}", and "${firstThing}" will disappear from the database.`
        apiUrl = 'merge_food_categories'
        apiParms = {
            category_to_merge: firstThing,
            category_to_keep: secondThing,
        }
    }
    let confirmMerge = confirm(confirmText)
    if (confirmMerge) {
        let apiSuccess = await fetch(`${currentUrlDomain}/${apiUrl}/`, {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(apiParms)
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
            await searchFilter()
            resetMergeMode(false, '')

            if ( activeTab == 'food' ) {
                dataDict = foodDataDict
                table = foodCategoryTable
            } else {
                dataDict = categoryDataDict
                table = categoryTable
            }
            
            // The merge row should now be highlighted, but using the highlightedMergeRow 
            // variable won't work since that is from before reloadDataTables. 
            // Instead we'll find it by index.
            let newHighlightedRowIndex = dataDict[secondThing]['rowIndex']
            let newHighlightedRow = table.rows[newHighlightedRowIndex]
            let fakeEvent = {'target': newHighlightedRow}
            highlightStatsRow(fakeEvent)
        }
    }
}

const mergeFoodsHandler = (event) => mergeFoods(event)

function resetMergeMode(stillInMergeMode, headerText) {
    mergeMode = stillInMergeMode
    
    let mergeButton
    let cancelMergeButton
    let editButton
    let mergeHeader
    let mergeBody

    if ( activeTab =='food' ) {
        mergeButton = foodMergeButton
        cancelMergeButton = foodCancelMergeButton
        editButton = foodEditButton
        mergeHeader = foodStatsMergeHeader
        mergeBody = foodStatsMergeBody
    } else {
        mergeButton = categoryMergeButton
        cancelMergeButton = categoryCancelMergeButton
        editButton = categoryEditButton
        mergeHeader = categoryStatsMergeHeader
        mergeBody = categoryStatsMergeBody
    }
    
    if (!stillInMergeMode) {
        // Remove cancel button and show edit button again
        cancelMergeButton.style.display = 'none'
        if (highlightedStatsRow) {
            editButton.style.display = ''
        }
    }
    mergeHeader.innerText = ''
    if (highlightedMergeRow) {
        highlightedMergeRow.classList.remove('highlight_merge')
        highlightedMergeRow = null
    }
    mergeHeader.innerText = headerText
    mergeBody.innerHTML = ''
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
        foodDeleteButton.innerText = 'Deleting...'
        foodDeleteButton.setAttribute('disabled', true)
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
            await searchFilter()

            foodDeleteButton.innerText = 'Delete food'
            foodDeleteButton.removeAttribute('disabled')
        }
    }
}

async function deleteCategory() {
    let categoryName = highlightedStatsRow.getAttribute('data-category')
    let confirmText = `Are you sure you want to delete "${categoryName}"? No foods are assigned it nothing will be impacted.`
    let confirmDelete = confirm(confirmText)
    if (confirmDelete) {
        categoryDeleteButton.innerText = 'Deleting...'
        categoryDeleteButton.setAttribute('disabled', true)
        let apiSuccess = await fetch(`${currentUrlDomain}/delete_food_category/`, {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                category_name: categoryName,
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
            await searchFilter()

            categoryDeleteButton.innerText = 'Delete category'
            categoryDeleteButton.removeAttribute('disabled')
        }
    }
}

function highlightMergeRow(event) {
    targetElement = event.target
    let inputNodeNames = ['TEXTAREA', 'SELECT', 'SPAN', 'LABEL']
    if (targetElement.nodeName == "TD") {
        // Target the parent row so we can standardize the code below
        targetElement = targetElement.parentNode
    } else if (inputNodeNames.includes(targetElement.nodeName)) {
        targetElement = targetElement.parentNode.parentNode
    }

    let defaultHeaderText
    let badMergeTooltip
    let mergeButton
    let mergeHeader
    let mergeBody
    let statsTemplate
    let emptyStatsTemplate

    if ( activeTab=='food' ) {
        defaultHeaderText = defaultFoodMergeHeaderText
        badMergeTooltip = foodBadMergeTooltip
        mergeButton = foodMergeButton
        mergeHeader = foodStatsMergeHeader
        mergeBody = foodStatsMergeBody
        statsTemplate = foodStatsTemplate
        emptyStatsTemplate = emptyFoodStatsTemplate
    } else {
        defaultHeaderText = defaultCategoryMergeHeaderText
        badMergeTooltip = categoryBadMergeTooltip
        mergeButton = categoryMergeButton
        mergeHeader = categoryStatsMergeHeader
        mergeBody = categoryStatsMergeBody
        statsTemplate = categoryStatsTemplate
        emptyStatsTemplate = emptyCategoryStatsTemplate
    }

    if (highlightedMergeRow == targetElement) {
        // If clicking the already-highlighted row, un-highlight it and remove stats
        resetMergeMode(true, defaultHeaderText)
    } else if (highlightedStatsRow == targetElement) {
        // Clicked the stats row, which is highlighted blue. You can't merge into yourself!
        // showAndHideTooltip is defined in tooltip.js

        positionTooltip(badMergeTooltip, targetElement)  // positionTooltip defined in tooltip.js
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

        let food
        let category
        let statsList
        if ( activeTab=='food' ) {
            food = targetElement.getAttribute('data-food')
            category = targetElement.getAttribute('data-category')
            statsList = Array.from(foodDataDict[food]['recipes'])
            mergeHeader.innerText = `${category}: ${food}`;
            if ( statsList.length > 0 ) {
                let listItemHTML = statsList.map(rec => `<li style="padding-bottom: 10px;"><a href="${currentUrlDomain}/recipe/${rec.clean_key}">${rec.title}</a></li>`).join('');
                mergeBody.innerHTML = statsTemplate.replace('{statsList}', listItemHTML);
            }
        } else {
            category = targetElement.getAttribute('data-category')
            statsList = Array.from(categoryDataDict[category]['foods'])
            mergeHeader.innerText = category;
            if ( statsList.length > 0 ) {
                let listItemHTML = statsList.map(food => `<li style="padding-bottom: 5px;">${food}</li>`).join('');
                mergeBody.innerHTML = statsTemplate.replace('{statsList}', listItemHTML);
            }
        }

        if ( statsList.length == 0 ) {
            mergeBody.innerHTML = emptyStatsTemplate;
        }
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
    let categoryNameSearchValue = categoryNameSearch.value
    let noCategorySearchValue = noCategorySearch.checked
    let noRecipeSearchValue = noRecipeSearch.checked
    let noFoodSearchValue = noFoodSearch.checked

    let params = {
        food_name: foodNameSearchValue,
        food_category: foodCategorySearchValue,
        category_name: categoryNameSearchValue,
        no_category: noCategorySearchValue,
        no_recipe: noRecipeSearchValue,
        no_food: noFoodSearchValue,
    }

    // Format params as URL query string
    let param_string = Object.entries(params)
        .map(([k, v]) => (`${k}=${v}`))
        .join('&')

    console.log(`Performing GET with params: ${param_string}`)

    await reloadDataTables(param_string)

    // searchFilterWithTimeout may set us to "searching" status
    foodCategoryTable.classList.remove('searching') 
    categoryTable.classList.remove('searching') 

    let dataDict
    let table

    if ( activeTab == 'food' ) {
        dataDict = foodDataDict
        table = foodCategoryTable
    } else {
        dataDict = categoryDataDict
        table = categoryTable
    }
    
    // If in merge mode, preserve the original highlighted row even if it's
    // not in the search results - in other words, always show the stats and don't
    // set highlightedStatsRow back to null. If the row disappears from the search
    // results, its stats stay visible. When it appears back in the search results,
    // highlight it again.
    if ( mergeMode && highlightedStatsRow ) {
        let oldHighlightedRowName = highlightedStatsRow.getAttribute(`data-${activeTab}`)
        if ( oldHighlightedRowName in dataDict ) {
            let newHighlightedRowIndex = dataDict[oldHighlightedRowName]['rowIndex']
            let newHighlightedRow = table.rows[newHighlightedRowIndex]
            let fakeEvent = {'target': newHighlightedRow}
            highlightStatsRow(fakeEvent)
        }
    }

    // If in merge mode and have selected a merge highlight row
    // Un-highlight the merge row if it's no longer in the search results
    if ( mergeMode && highlightedMergeRow ) {
        let oldHighlightedRowName = highlightedMergeRow.getAttribute(`data-${activeTab}`)
        if ( oldHighlightedRowName in dataDict ) {
            let newHighlightedRowIndex = dataDict[oldHighlightedRowName]['rowIndex']
            let newHighlightedRow = table.rows[newHighlightedRowIndex]
            let fakeEvent = {'target': newHighlightedRow}
            highlightMergeRow(fakeEvent)
        } else {
            // Un-highlight the merge row
            resetMergeMode(true, defaultHeaderText)
        }
    }

    // If NOT in merge mode and just have a highlighted stats row
    // Un-highlight the stats row if it's no longer in the search results
    // Excluding edit mode too, as we reach this stage during the table 
    // reset that comes with saving an edit
    if ( ! mergeMode && ! editMode && highlightedStatsRow ) {
        let oldHighlightedRowName = highlightedStatsRow.getAttribute(`data-${activeTab}`)
        if ( oldHighlightedRowName in dataDict ) {
            let newHighlightedRowIndex = dataDict[oldHighlightedRowName]['rowIndex']
            let newHighlightedRow = table.rows[newHighlightedRowIndex]
            let fakeEvent = {'target': newHighlightedRow}
            highlightStatsRow(fakeEvent)
        } else {
            // Un-highlight by passing the existing row into the highlight function
            unHighlightStatsRow()
        }
    }
    
}

async function executeWithTimeout(promise, timeoutMs) {
    let timeoutHandle;
  
    const timeoutPromise = new Promise((_, reject) => {
        timeoutHandle = setTimeout(() => reject(new Error("Timeout")), timeoutMs);
    });
  
    try {
        const result = await Promise.race([promise, timeoutPromise]);
        clearTimeout(timeoutHandle);
        return { result, timedOut: false };
    } catch (error) {
        clearTimeout(timeoutHandle);
        return { result: null, timedOut: true, error };
    }
}
  
async function searchFilterWithTimeout() {
    const timeoutDuration = 300; // Set your desired timeout in milliseconds
  
    const { result, timedOut, error } = await executeWithTimeout(searchFilter(), timeoutDuration);
    
    let resultCount
    let table
    if ( activeTab == 'food' ) {
        resultCount = foodResultCount
        table = foodCategoryTable
    } else {
        resultCount = categoryResultCount
        table = categoryTable
    }

    if (timedOut) {
        resultCount.innerText = 'Searching...'
        table.classList.add('searching')
    }
}
  


function assignRowListeners() {
    let rows = document.querySelectorAll('.manage_food_row')
    rows.forEach(row => {
        row.addEventListener('click', function(event) {handleFoodRowClick(event)})
    })

    autoHeightAllRows()
}

function autoHeightAllRows() {
    console.log('hi')
    let inputs = document.querySelectorAll('.food_name')
    inputs.forEach(textarea => {
        let fakeEvent = {'target': textarea}
        autoTextareaHeight(fakeEvent)
        textarea.addEventListener('change', function(event) {autoTextareaHeight(event)})
    })
}

assignRowListeners()
$(document).ready(showHideTabs)
foodEditButton.addEventListener('click', enterEditMode)
categoryEditButton.addEventListener('click', enterEditMode)

foodNameSearch.addEventListener("input", searchFilterWithTimeout)
foodCategorySearch.addEventListener("input", searchFilterWithTimeout)
noCategorySearch.addEventListener("input", searchFilterWithTimeout)
noRecipeSearch.addEventListener("input", searchFilterWithTimeout)
categoryNameSearch.addEventListener("input", searchFilterWithTimeout)
noFoodSearch.addEventListener("input", searchFilterWithTimeout)