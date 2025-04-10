let copyButton = document.getElementById('copy_groceries_button')
let ingredsTable = document.getElementById('recipe_detail_ingredients_table')

function parseIngredientsTable () {
    let rows = ingredsTable.querySelectorAll('tbody tr')
    let ingredsByCategory = {}

    for (let row of rows) {
        let cells = row.querySelectorAll('td')
        // I put all the data attributes on the notes cell, which is the last one
        let dataCell = cells[cells.length - 1]
        let foodCategory = dataCell.getAttribute('data-food_category')
        if ( foodCategory == '' ) {
            foodCategory = 'Other'
        }
        let food = dataCell.getAttribute('data-food')
        let quantity = dataCell.getAttribute('data-quantity').trim()
        let foodQuantity
        if ( quantity != '' ) {
            foodQuantity = `${quantity} ${food}`
        } else {
            foodQuantity = food
        }

        if ( ! (foodCategory in ingredsByCategory) ) {
            ingredsByCategory[foodCategory] = [foodQuantity]
        } else {
            ingredsByCategory[foodCategory].push(foodQuantity)
        }
    }
    return ingredsByCategory
}

function copyGroceryList () {
    let groceryList = parseIngredientsTable()
    let groceryListString = ""
    for (let category in groceryList) {
        groceryListString += `${category}:\n`
        let groceryListItems = groceryList[category].map(item => '- ' + item)
        groceryListString += groceryListItems.join('\n')
        groceryListString += '\n\n'
    }
    navigator.clipboard.writeText(groceryListString).then(function() {
        console.log('Grocery list copied to clipboard!')
    }, function(err) {
        console.error('Could not copy text: ', err)
    })
}

copyButton.addEventListener('click', copyGroceryList)