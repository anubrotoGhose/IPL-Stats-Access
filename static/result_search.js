function showColumn(key) {
    var columnData = searchData[key];
    var displayArea = document.getElementById('columnData');
    displayArea.innerHTML = ''; // Clear previous data

    if(columnData) {
        columnData.forEach(function(item) {
            if(item != null) {
                // Create a link for each item
                var link = document.createElement('a');
                link.href = '/profile_page/' + key + '?value=' + encodeURIComponent(item);
                link.textContent = item;
                link.className = 'data-link'; // Apply the class
                displayArea.appendChild(link);
                displayArea.innerHTML += '<br>';
            }
        });
    }
}


// Load the default column (Players)
window.onload = function() {
    showColumn('Players');
};
