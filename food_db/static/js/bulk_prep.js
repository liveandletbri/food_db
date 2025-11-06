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