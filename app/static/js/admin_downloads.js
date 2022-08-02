// Checkbox function
function export_toggle(source) {
  checkboxes = document.getElementsByName("download");
  for (var i = 0, n = checkboxes.length; i < n; i++) {
    checkboxes[i].checked = source.checked;
  }
}

function action_toggle(source) {
  checkboxes = document.getElementsByName("delete");
  for (var i = 0, n = checkboxes.length; i < n; i++) {
    checkboxes[i].checked = source.checked;
  }
}

// Download selected rows
function downloadRow() {
  if ($("input.download").is(":checked")) {
    if (confirm("Do you want to download the selected rows?")) {
      console.log("Yes");
    }
  }
}

// Delete selected rows
function deleteRow() {
  if ($("input.delete").is(":checked")) {
    if (
      confirm(
        "Are you sure you want to delete the selected rows? This cannot be undone."
      )
    ) {
      document.querySelectorAll("#table .delete:checked").forEach(e => {
        e.parentNode.parentNode.remove();

        // Get primary key of row. Get first <td> inside <tr>
        // For debugging purposes using console.log -> survey_id = document.getElementsByTagName("tbody")[0].rows[0].getElementsByTagName("td")[0].innerHTML

        // In the User Response table in the database, given the survey_id, we want to delete the row of that user (given that a user submits a survey only once).
        // not sure how to do

        // 1. Find survey_id
        //$('#table tr').each(function() {
        //  var surveyId = $(this).find(".survey_id").html();
        //});

        // $.ajax({
        //  type: 'POST',
        //   url: '/delete',
        //   data: JSON.stringify(surveyId),
        //   contentType: 'application/json',
        //  success: function(surveyId) {

        //  });
      });
    }
  }
}
