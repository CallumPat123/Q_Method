let nRegister = 0;
let nQuestion = 0;
let nRow = 0;

$("#statements-input").bind("input propertychange", () => {
  $("#statements-notice").html(
    $("#statements-input")
      .val()
      .split(/[\n\r]/g)
      .filter(n => n.trim() != "").length
  );
});

function display_instruction(index) {
  if (index < 0 || index > 6) {
    return false;
  }
  $(".instruction-input.current").removeClass("current");
  $($(".instruction-input")[index]).addClass("current");
  return true;
}

function addRegister() {
  nRegister = nRegister + 1; // Create new ID just in case
  $("#register").append(
    "<textarea id='reg" +
      nRegister +
      "' class='form-control input-group' name='register' required></textarea>"
  );
  $("#register").append(
    "<button id='reg" +
      nRegister +
      "-remove" +
      "' class='btn btn-danger remove-reg' type='button' onclick='removeRegister(" +
      nRegister +
      ")'> Remove Question </button>"
  );
}

// Used only in the register section
function removeRegister(id) {
  let textbox = document.getElementById("reg" + id);
  let button = document.getElementById("reg" + id + "-remove");
  textbox.remove();
  button.remove();
}

function addQuestionnaire() {
  nQuestion = nQuestion + 1;
  $("#questionnaire").append(
    "<input id='que" +
      nQuestion +
      "' type='text' class='form-control input-group' name='questionnaire' required/>"
  );
  $("#questionnaire").append(
    "<button id='que" +
      nQuestion +
      "-remove" +
      "' class='btn btn-danger remove-que' type='button' onclick='removeQuestionnaire(" +
      nQuestion +
      ")'> Remove Question </button>"
  );
}

function removeQuestionnaire(id) {
  let textbox = document.getElementById("que" + id);
  let button = document.getElementById("que" + id + "-remove");
  textbox.remove();
  button.remove();
}

function addRow() {
  nRow = nRow + 1;
  $("#cols").append(
    "<input id='row" +
      nRow +
      "' type='number' class='form-control input-group rows' name='cols' min='1' placeholder='Number of columns in this row'/>"
  );
  $("#cols").append(
    "<button id='row" +
      nRow +
      "-remove" +
      "' class='btn btn-danger btn-sm remove-row' type='button' onclick='removeRow(" +
      nRow +
      ")'> Remove Row </button>"
  );
}

function removeRow(id) {
  let textbox = document.getElementById("row" + id);
  let button = document.getElementById("row" + id + "-remove");
  textbox.remove();
  button.remove();
}

function validate_fields() {
  let min_range = $("#rangemin").val();
  let max_range = $("#rangemax").val();
  let range = max_range - min_range;
  let rows = $(".rows");
  let sum = 0;
  let nStatements = $("#statements-notice").html();
  const blockContainer = document.querySelector(".block-container");
  const cols = document.querySelector(".cols");
  if (!blockContainer) {
    alert("Please generate a grid. ");
    return false;
  }

  // if(range % 2 != 0) {
  //   alert("The range specified produces an even amount of columns which is incompatible with this type of survey.");
  //   return false;
  // }
  // if($(".rows")[0] == undefined || $(".rows")[0].value != range + 1) {
  //   alert("The first row of the grid must match the range given. Please check your grid.");
  //   return false;
  // }
  // for(var i = 0; i < rows.length; i++) {
  //   if(rows[i].value == "" || rows[i].value <= 0 || rows[i].value > range + 1) {
  //     alert("Rows cannot be empty, 0, negative or higher than the number of columns.");
  //     return false;
  //   }
  //   if(rows[i].value % 2 == 0) {
  //     alert("Rows cannot be even in length as there are an odd number of columns.");
  //     return false;
  //   }
  //   sum = sum + parseInt(rows[i].value);
  // }

  const min = Math.abs(parseInt(min_range));
  const max = parseInt(max_range);
  const columns = [];

  for (var i = 0; i <= max + min; i++) {
    columns.push(blockContainer.children[i].children.length);
    sum += blockContainer.children[i].children.length;
  }

  if ($("#register > textarea").length == 0) {
    alert("Please have at least one registration question.");
    return false;
  }
  if (
    $("#questionnaire > input").length == 2 &&
    $("#questionnaire > input")[0].value == "" &&
    $("#questionnaire > input")[1].value == ""
  ) {
    alert("Please have at least one questionnaire question.");
    return false;
  }
  if (sum != nStatements) {
    alert(
      "Your grid has " +
        sum +
        " slots but you have " +
        nStatements +
        " statements."
    );
    return false;
  }

  cols.innerHTML = `<textarea
    id="cols"
    class="form-control input-group"
    name="cols"
    required
  >${columns}</textarea>`;

  return true;
}
