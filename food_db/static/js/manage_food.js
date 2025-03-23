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
let highlightedRow
let foodStatsHeader = document.getElementById('food_stats_header')
let foodStatsBody = document.getElementById('food_stats_body')
let foodStatsButtons = document.getElementById('food_stats_buttons')

let foodStatsTemplate = `<h4>Used in these recipes:</h4>
<ul>
{recipeList}
</ul>`

let foodStatsMergeButton = `<button id="merge_food_button" class="food_stats_button" type="button" 
onclick="showIngredientParserOnClick()">Merge foods...</button>`

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

function highlightRow(event){
    event.preventDefault()
    targetElement = event.target
    if (targetElement.nodeName == "TD") {
        // Target the parent row so we can standardize the code below
        targetElement = targetElement.parentNode;   
    }
    if (highlightedRow) {
        highlightedRow.classList.remove('highlight')
    }
    targetElement.classList.add('highlight')
    highlightedRow = targetElement
    let food = targetElement.getAttribute('data-food')
    let category = targetElement.getAttribute('data-category')
    let recipes = Array.from(foodDataDict[food]['recipes'])
    let recipeHTML = recipes.map(rec => `<li><a href="${currentUrlDomain}/recipe/${rec.clean_key}">${rec.title}</a></li>`)
    foodStatsHeader.innerText = `${category}: ${food}`
    foodStatsBody.innerHTML = foodStatsTemplate.replace('{food}',food).replace('{category}',category).replace('{recipeList}',recipeHTML)
    foodStatsButtons.innerHTML = foodStatsMergeButton
}

let rows = document.querySelectorAll('.manage_food_row')
rows.forEach(row => {
    row.addEventListener('click', function(event) {highlightRow(event)})
})

$(document).ready(showHideTabs)
