// Add new item form submission
$(function() {
    $('#addNewItem').click(function() {

        if ($.trim($("#barcode").val()) === "" || $.trim($("#item_name").val()) === "" || $.trim($("#amount").val()) === "") {
          alert('Please fill in all the fields.');
          return false;
        }

        $.ajax({
            url: '/additem',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                $("body").load("/");
            },
            error: function(error) {
                $("body").load("/error/" + error);
            }
        });
    });
	
// Change name of item form submission	
    $('#saveItemName').click(function() {	

        if ($.trim($("#new_item_name").val()) === "") {
          alert('Please fill in the item name.');
          return false;
        }

        $.ajax({
            url: '/updatename',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response) {
                window.location.href = "/";
            },
            error: function(error) {
                $("body").load("/error/" + error);
            }
        });
    });
});

// Table search function
function tableSearch(inputID, tableID) {
  // Declare variables
  var input, filter, table, tr, td, i;
  input = document.getElementById(inputID);
  filter = input.value.toUpperCase();
  table = document.getElementById(tableID);
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those that don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0];
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        $(tr[i]).fadeIn('fast');
        //tr[i].style.display = "";
      } else {
        $(tr[i]).fadeOut('fast');
        //tr[i].style.display = "none";
      }
    }
  }
}
/*
// Tooltips
  $(document).ready(function(){
    $('.tooltipped').tooltip();
  });
*/