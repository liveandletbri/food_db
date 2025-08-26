// From https://www.brennantymrak.com/articles/django-dynamic-formsets-javascript and https://stackoverflow.com/questions/6142025/dynamically-add-field-to-a-form

let addOrEditMode = JSON.parse(addOrEditModeRaw.textContent)

let ingredTable = document.querySelector("#ingred-table")
let ingredTableBody = ingredTable.querySelector('tbody')
let addIngredientButton = document.querySelector("#add-ingred-form")
let deleteLastIngredientButton = document.querySelector("#delete-ingred-form")

let extraIngredRowCountField = document.querySelector("#id_extra_ingred_count")
let extraIngredRowNum = Number(extraIngredRowCountField.value);

function addListenersToRowButtons() {
    let deleteThisIngredientButtons = document.querySelectorAll(".delete_ingred_button")
    let deleteThisStepButtons = document.querySelectorAll(".delete_step_button")
    let parseThisStepButtons = document.querySelectorAll(".parse_step_button")

    deleteThisIngredientButtons.forEach(btn => btn.addEventListener('click', removeThisIngredientRow, btn))
    deleteThisStepButtons.forEach(btn => btn.addEventListener('click', removeThisStepRow, btn))
    parseThisStepButtons.forEach(btn => btn.addEventListener('click', parseThisStepRow, btn))
}

// Need to wait for "onload" to be after all the SVGs are rendered by Font Awesome magic
function onLoadSetup() {
    console.log("Adding listeners to row buttons")
    addListenersToRowButtons()

    let markdownHelpIcon = document.querySelector("#markdown_help_icon")
    let markdownHelpTooltip = document.querySelector("#markdown_help_tooltip")
    markdownHelpIcon.addEventListener('mouseover', () => setTimeout(showToolTip, 300, markdownHelpTooltip))
    markdownHelpIcon.addEventListener('mouseleave', () => setTimeout(hideToolTip, 300, markdownHelpTooltip))


    let recipeStepsHeader = document.querySelector("#recipe_steps_header")
    markdownHelpTooltip.style.left = `${recipeStepsHeader.offsetLeft + 180}px`;
    markdownHelpTooltip.style.top = `${recipeStepsHeader.offsetTop + 8}px`;

    let ingredCategoryHelpIcon = document.querySelector("#ingred_category_help_icon")
    let ingredCategoryHelpTooltip = document.querySelector("#ingred_category_help_tooltip")
    ingredCategoryHelpIcon.addEventListener('mouseover', () => setTimeout(showToolTip, 300, ingredCategoryHelpTooltip))
    ingredCategoryHelpIcon.addEventListener('mouseleave', () => setTimeout(hideToolTip, 300, ingredCategoryHelpTooltip))

    let ingredCategoryHeader = document.querySelector("#ingred_category_header")
    let headerRect = ingredCategoryHeader.getBoundingClientRect()
    let scrollLeft = document.documentElement.scrollLeft
    let scrollTop = document.documentElement.scrollTop
    ingredCategoryHelpTooltip.style.left = `${headerRect.left + scrollLeft + 180}px`
    ingredCategoryHelpTooltip.style.top = `${headerRect.top + scrollTop + 8}px`
}

window.addEventListener('load', onLoadSetup)

function getHighestIngredientNumber () {
    // Since you can delete and add rows in the middle of the table, we need to find the highest ingredient ID number and increment that for the new row
    let ingredTableArray = Array.from(ingredTable.rows) // convert HTMLCollection into Array, so we can...
    let ingredRows = ingredTableArray.slice(1) // Remove header row
    
    return Math.max(...
        ingredRows.map(row => row.querySelector("td:first-child > input").name) // iterate over ingredient rows and strip the name of each row
        .map(name =>  Number(name.replace('ingred_','').split('_')[0])) // strip number out of name
    )
}

function addIngredientRow(e, rowToInsertAfter = null) {
    e.preventDefault()

    let newRow = ingredTable.rows[1].cloneNode(true) // Clone the first ingredient row
    let idRegex = RegExp(`ingred_(\\d){1}`,'g') // Regex to find all instances of the ID number

    let highestRowNumber = getHighestIngredientNumber()
    let newRowNumber = highestRowNumber + 1
    
    newRow.innerHTML = newRow.innerHTML.replace(idRegex, `ingred_${newRowNumber}`) // Update the new row to have the correct row number
    newRow.setAttribute('name', `ingred_${newRowNumber}_row`)
    newRow.querySelectorAll('input').forEach(x => x.value = '') // Blank out text in new row

    // If specified, insert this row after another row. Otherwise, append to bottom
    let rowToInsertBefore
    if ( rowToInsertAfter == null ) {
        // set artificially high number as the row to insert before - it will just add to the end
        rowToInsertBefore = 999
    } else {
        rowToInsertBefore = rowToInsertAfter.rowIndex + 1
    }
    ingredTableBody.insertBefore(newRow, ingredTable.rows[rowToInsertBefore])

    // Increment the number of total rows in the hidden field
    extraIngredRowNum++
    extraIngredRowCountField.value = extraIngredRowNum 

    addListenersToRowButtons()
}

function removeBottomIngredientRow(e) {
    e.preventDefault()

    if (ingredTable.rows.length > 2) {
        let lastRowNum = ingredTable.rows.length - 1
        ingredTable.deleteRow(lastRowNum)

        extraIngredRowNum--
        extraIngredRowCountField.value = extraIngredRowNum
    }
}

function removeThisIngredientRow(e) {
    let row = e.currentTarget.closest('tr')
    if (row.rowIndex > 1) {  // Don't delete the first ingredient row, always leave at least one ingredient (or other stuff breaks)
        ingredTableBody.removeChild(row)

        extraIngredRowNum--
        extraIngredRowCountField.value = extraIngredRowNum
    } else {
        // If you try to delete the first row, just clear the values instead
        // Each row has multiple children, a <td> for each field of an ingredient
        // Each <td> has just one child, an <input> element. This is what we clear.

        Array.from(row.children).forEach(td => {
            let input = td.querySelector('input')
            // There is also a <td> for the delete button, but it doesn't have an <input> element
            if (input) {
                input.value = ''
            }
        })
    }

}

addIngredientButton.addEventListener('click', addIngredientRow)
deleteLastIngredientButton.addEventListener('click', removeBottomIngredientRow)

// Same thing, but now Steps

let stepTable = document.querySelector("#step_table")
let stepTableBody = stepTable.querySelector('tbody')
let addStepButton = document.querySelector("#add-step-form")
let deleteLastStepButton = document.querySelector("#delete-step-form")

let extraStepRowCountField = document.querySelector("#id_extra_step_count")
let extraStepRowNum = Number(extraStepRowCountField.value);

function getHighestStepNumber () {
    // Since you can delete and add rows in the middle of the table, we need to find the highest step ID number and increment that for the new row
    return Math.max(...
        Array.from(stepTable.rows, // convert HTMLCollection into Array, so we can...
        (row) => row.querySelector("td:first-child > textarea").name) // iterate over it and strip the name of each row
        .map(name =>  Number(name.replace('step_','').split('_')[0])) // strip number out of name
    )
}

function addStepRow(e, rowToInsertAfter = null) {
    e.preventDefault()

    let newRow = stepTable.rows[0].cloneNode(true) // Clone the first step row
    let idRegex = RegExp(`step_(\\d){1}`,'g') // Regex to find all instances of the ID number

    let highestRowNumber = getHighestStepNumber()
    let newRowNumber = highestRowNumber + 1
    
    newRow.innerHTML = newRow.innerHTML.replace(idRegex, `step_${newRowNumber}`) // Update the new row to have the correct row number
    newRow.setAttribute('name', `step_${newRowNumber}_row`)
    newRow.querySelector('textarea').textContent = '' // Blank out text in new row's HTML
    newRow.querySelector('textarea').value = '' // Blank out text in new row

    // If specified, insert this row after another row. Otherwise, append to bottom
    let rowToInsertBefore
    if ( rowToInsertAfter == null ) {
        // set artificially high number as the row to insert before - it will just add to the end
        rowToInsertBefore = 999
    } else {
        rowToInsertBefore = rowToInsertAfter.rowIndex + 1
    }
    stepTableBody.insertBefore(newRow, stepTable.rows[rowToInsertBefore])

    // Increment the number of total rows in the hidden field
    extraStepRowNum++
    extraStepRowCountField.value = extraStepRowNum

    addListenersToRowButtons() 
}

function removeBottomStepRow(e) {
    e.preventDefault()

    if (stepTable.rows.length > 1) {
        let lastRowNum = stepTable.rows.length - 1
        stepTable.deleteRow(lastRowNum)

        extraStepRowNum--
        extraStepRowCountField.value = extraStepRowNum
    }
}

function removeThisStepRow(e) {
    let row = e.currentTarget.closest('tr')
    stepTableBody.removeChild(row)

    extraStepRowNum--
    extraStepRowCountField.value = extraStepRowNum
}

function parseThisStepRow(e) {
    let row = e.currentTarget.closest('tr')
    let rawText = row.querySelector('textarea').value
    let parsedText = rawText.split(/(\n)(\d\.)*/gm)
        .filter(chunk => chunk) // remove undefined
        .filter(chunk => !chunk.match(/^\s+$/)) // remove chunks that are just white space
        .filter(chunk => !chunk.match(/^\d\.$/)) // remove chunks that are just a number and period
        .map(chunk => chunk.trim())
        .map(chunk => chunk.replace(/^\d\./,''))
    let numberNewSteps = parsedText.length - 1
    
    // create new steps and set their values to the parsed text chunks
    for(let i = 0; i < numberNewSteps; i++){ // Note the less than - it will insert exactly numberNewSteps rows
        addStepRow(e, rowToInsertAfter=stepTable.rows[row.rowIndex])
    }
    for(let i = 0; i <= numberNewSteps; i++){ // Less than or equal - this runs one more time to account for the original row that we are keeping
        let rowNumber = i + row.rowIndex
        stepTable.rows[rowNumber].querySelector('textarea').value = parsedText[i]
    }
}

addStepButton.addEventListener('click', addStepRow)
deleteLastStepButton.addEventListener('click', removeBottomStepRow)

// Function to copy Category from current row to next row
function copyCategoryToNextRow() {
    // Get the currently focused element
    const activeElement = document.activeElement;
    
    // Check if the focused element is in an ingredient row
    const currentRow = activeElement.closest('tr[name^="ingred_"]');
    
    if (!currentRow) {
        // Not in an ingredient row, do nothing
        return;
    }
    
    // Check if this is the bottom row (last ingredient row)
    const ingredientRows = document.querySelectorAll('tr[name^="ingred_"]');
    const isLastRow = currentRow === ingredientRows[ingredientRows.length - 1];
    
    if (isLastRow) {
        // This is the bottom row, do nothing
        return;
    }
    
    // Get the current row's category value
    const currentCategoryInput = currentRow.querySelector('input[name$="_ingredient_category"]');
    const currentCategoryValue = currentCategoryInput.value;
    
    // Find the next row
    const nextRow = currentRow.nextElementSibling;
    
    // Check if the next row is also an ingredient row
    if (nextRow && nextRow.getAttribute('name') && nextRow.getAttribute('name').startsWith('ingred_')) {
        // Get the next row's category input
        const nextCategoryInput = nextRow.querySelector('input[name$="_ingredient_category"]');
        
        // Copy the category value
        nextCategoryInput.value = currentCategoryValue;
        
        // Move cursor to the next row's category field
        nextCategoryInput.focus();
        nextCategoryInput.select();
    }
}

// Add keyboard event listener for Ctrl+Alt+C
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.altKey && e.key === 'c') {
        e.preventDefault(); // Prevent default browser behavior
        copyCategoryToNextRow();
    }
});