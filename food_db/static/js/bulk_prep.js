// Tab switching functionality
let activeTab = 'prep';

function showHideTabs(){   
    // on page load, show first tab and hide the other
    $('#tabs li a:not(:first)').addClass('inactive');
    $('.tab_container').hide();
    $('.tab_container:first').show();
    activeTab = 'prep'  // prep tab is the first tab
    
    // actions when a tab is clicked
    $('#tabs li a').click(function() {
        let thisTabId = $(this).attr('id');

        // if the tab was inactive, make it active and hide the old tab
        if($(this).hasClass('inactive')){ 
            // perform the tab swap
            $('#tabs li a').addClass('inactive');           
            $(this).removeClass('inactive');
            
            $('.tab_container').hide();
            $('#'+ thisTabId + '_content').fadeIn('slow');
            
            // set the new "active tab" to be this tab
            if (thisTabId === 'prep_tab') {
                activeTab = 'prep'
            } else if (thisTabId === 'view_config_tab') {
                activeTab = 'view_config'
            }
        }
    });
}

// Initialize row shift functionality for timing table
window.addEventListener('load', function() {
    initializeRowShiftFunctionality('.timing_table_row', '#timing_table tbody');
});

// Add extra event to listeners for column sorts (column sorting defined in table_sort.js)
// As long as this event listener as registered last (after the event listeners in table_sort.js), it should happen after the rows are sorted
const timingTableHideButtonsHandler = () => hideTopAndBottomButtons('.timing_table_row');
document.querySelectorAll('th').forEach(th => th.addEventListener('click', timingTableHideButtonsHandler))

// Initialize tabs when document is ready
$(document).ready(showHideTabs)

// View Config form validation
let submitViewConfigButton = document.querySelector("#submit_view_config_button")
let viewConfigForm = document.querySelector("#view_config_form")
let viewConfigNameInput = document.querySelector("#view_config_name")

let viewConfigNameTooltip = document.querySelector("#view_config_name_tooltip")
let viewConfigTagsTooltip = document.querySelector("#view_config_tags_tooltip")
let viewConfigAttributesTooltip = document.querySelector("#view_config_attributes_tooltip")

function validateViewConfig(e) {
    e.preventDefault()
    
    let invalid = false
    
    // Get current form values
    let name = viewConfigNameInput.value.trim()
    let selectedTags = document.querySelectorAll('input[name="tags"]:checked')
    let selectedAttributes = document.querySelectorAll('input[name="recipe_attributes"]:checked')
    
    // Name must be filled out
    if (name === '' || name.toLowerCase() === 'default') {
        showAndHideTooltip(viewConfigNameTooltip)
        invalid = true
    }
    
    // At least one tag must be checked
    if (selectedTags.length === 0) {
        showAndHideTooltip(viewConfigTagsTooltip)
        invalid = true
    }
    
    // At least one recipe attribute must be checked
    if (selectedAttributes.length === 0) {
        showAndHideTooltip(viewConfigAttributesTooltip)
        invalid = true
    }
    
    // Submit if all clear!
    if (invalid == false) {
        submitViewConfigButton.innerText = 'Creating...'
        submitViewConfigButton.style.backgroundColor = 'lightgray'
        submitViewConfigButton.style.opacity = 0.25
        viewConfigForm.submit()
    }
}

// Add event listener when document is ready
$(document).ready(function() {
    if (submitViewConfigButton) {
        submitViewConfigButton.addEventListener('click', validateViewConfig)
    }
    
    // Add click handlers to checkbox divs to toggle the checkbox when clicking anywhere on the div
    document.querySelectorAll('.checkbox').forEach(function(checkboxDiv) {
        checkboxDiv.addEventListener('click', function(event) {
            // Only toggle if the click wasn't directly on the checkbox input itself
            // (to avoid double-toggling when clicking directly on the checkbox)
            if (event.target.type !== 'checkbox') {
                let checkboxInput = checkboxDiv.querySelector('input[type="checkbox"]')
                if (checkboxInput) {
                    checkboxInput.checked = !checkboxInput.checked
                }
            }
        })
    })
    
    // Handle view config radio button selection
    document.querySelectorAll('input[name="view_config_radio"]').forEach(function(radio) {
        radio.addEventListener('change', function() {
            let currentUrl = window.location.href
            let currentUrlDomain = currentUrl.split("/bulk")[0]
            let viewConfigKey = this.value
            
            if (viewConfigKey === '') {
                // Redirect to bulk_prep without view_config_key (default)
                window.location.href = currentUrlDomain + '/bulk/'
            } else {
                // Redirect to bulk_prep with the selected view_config_key
                window.location.href = currentUrlDomain + '/bulk/?view_config_key=' + viewConfigKey
            }
        })
    })
})