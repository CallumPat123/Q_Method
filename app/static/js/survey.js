// Global Variables intialisation
const SURVEY_STAGES = 4;
const INSTR_BEGIN = 0;
const INSTR_USER_ID = 1;
const INSTR_OFFSET = 2;

let galleryIndex = 0;
let negative_sort = [];
let neutral_sort = [];
let positive_sort = [];
let surveyIndex = -1;
let responseId = null;
let matrix = [];

// Switching between pages
function display_page(index) {
  let surveyArray = $(".survey-section");
  if (index != -1) {
    set_instruction();
  }
  if (index < -1 || index >= SURVEY_STAGES) {
    return false;
  }

  $(".survey-section.current").removeClass("current");
  $(surveyArray[index + 1]).addClass("current");
}

function next_page() {
  if (surveyIndex == SURVEY_STAGES - 1) {
    return false;
  }

  surveyIndex = surveyIndex + 1;
  display_page(surveyIndex);
  return true;
}

function next_button() {
  let input = {};
  input.progress = surveyIndex + 1;
  input.surveyId = survey_id;
  input.userId = responseId;
  switch (surveyIndex) {
    case 0: // Personal Information Section
      let register_ans = [];
      // Checks that all fields are filled
      let isPersonalFinished = true;
      let personalFields = $("#personal-information .form-control");
      // Checks if the page is completed or not
      for (var i = 0; i < personalFields.length; i++) {
        let type = personalFields[i].type;
        let answer = personalFields[i].value;
        register_ans.push(answer);
        // If it is a text area
        if (type == "textarea") {
          let validate = answer.replace(/\s+/g, ""); // Removes empty spaces
          if (validate == "") {
            isPersonalFinished = false;
          }
        } else {
          // Then it must be a select-one
          if (answer == "") {
            isPersonalFinished = false;
          }
        }
      }
      if (isPersonalFinished) {
        // Send data to server
        input.register = register_ans;
        $.ajax({
          type: "POST",
          url: "/receive",
          data: JSON.stringify(input),
          contentType: "application/json",
          success: function(response) {
            console.log("Response sent to server: " + response);
            next_page();

            // SHOW THEIR ID/SURVEY ID
            $("#instructions-close").hide();
            $("#instructions-dismiss").show();
            set_instruction(INSTR_USER_ID);
            view_instruction();
          },
          error: function(jqXHR, textStatus, errorThrown) {
            alert("" + textStatus + " " + errorThrown + " An error occured.");
          }
        });
      }
      break;
    case 1: // Initial Sort Section
      let isSortingFinished = false;
      let unsortedArray = $("#gallery .unselectable");

      if (unsortedArray.length == 0) {
        isSortingFinished = true;
      }
      if (isSortingFinished) {
        negative_sort = [];
        neutral_sort = [];
        positive_sort = [];
        // Negative
        let sortedNegative = $("#sort-container > div:nth-child(1) p");
        for (var i = 0; i < sortedNegative.length; i++) {
          // Add to array
          negative_sort.push(sortedNegative[i].innerHTML);
          // Add to column for next page
          let element = $("#sort-container > div:nth-child(1) > div")[0];
          $("#sorted-container-grid > div")[0].appendChild(element);
        }
        let sortedNeutral = $("#sort-container > div:nth-child(2) p");
        for (var i = 0; i < sortedNeutral.length; i++) {
          neutral_sort.push(sortedNeutral[i].innerHTML);

          let element = $("#sort-container > div:nth-child(2) > div")[0];
          $("#sorted-container-grid > div")[1].appendChild(element);
        }
        let sortedPositive = $("#sort-container > div:nth-child(3) p");
        for (var i = 0; i < sortedPositive.length; i++) {
          positive_sort.push(sortedPositive[i].innerHTML);

          let element = $("#sort-container > div:nth-child(3) > div")[0];
          $("#sorted-container-grid > div")[2].appendChild(element);
        }

        // Send data to server:
        input.negative = negative_sort;
        input.neutral = neutral_sort;
        input.positive = positive_sort;
        $.ajax({
          type: "POST",
          url: "/receive",
          data: JSON.stringify(input),
          contentType: "application/json",
          success: function(response) {
            console.log("Response sent to server: " + response);
            next_page();
            view_instruction();
          },
          error: function(jqXHR, textStatus, errorThrown) {
            alert("" + textStatus + " " + errorThrown + " An error occured.");
          }
        });
      }
      break;
    case 2: // Grid Section
      // Check if grid is completed
      let isGridFinished = false;
      let unsortedStatements = $("#sorted-container-grid > div > div");
      if (unsortedStatements.length == 0) {
        isGridFinished = true;
      }

      if (isGridFinished) {
        arr = [];
        const grid = document.querySelector(".grid");
        const header = document.querySelector(".header-row");

        lengths = [];
        for (var i = 0; i < grid.children.length; i++) {
          lengths.push(grid.children[i].children.length);
        }

        const highestLength = Math.max(...lengths);

        for (let i = 0; i < grid.children.length; i++) {
          cols = [];
          for (let j = 0; j < highestLength; j++) {
            if (grid.children[i].children.length <= j) {
              cols.push("");
            } else {
              cols.push(
                grid.children[i].children[j].children[0].children[0].innerHTML
              );
            }
            // grid.children[0].children[0].children[0].children[0].innerHTML
          }
          arr.push(cols);
        }

        // nRows = $(".table tr").length - 1;
        // nCols = $(".table tr:nth-child(1) td").length;

        // for (var i = 2; i <= nRows + 1; i++) {
        //   rowData = [];
        //   for (var j = 1; j <= nCols; j++) {
        //     statement = $(
        //       ".table tr:nth-child(" + i + ") td:nth-child(" + j + ") p"
        //     ).text();
        //     rowData.push(statement);
        //   }
        //   arr.push(rowData);
        // }
        input.matrix = arr;
        matrix = arr;
        $.ajax({
          type: "POST",
          url: "/receive",
          data: JSON.stringify(input),
          contentType: "application/json",
          success: function(response) {
            console.log("Response sent to server: " + response);
            next_page();
            $("#survey-submit").html("Submit"); // Changes button to submit for NEXT section
            view_instruction();
            load_statements_to_questionnaire(matrix);
          },
          error: function(jqXHR, textStatus, errorThrown) {
            alert("" + textStatus + " " + errorThrown + " An error occured.");
          }
        });
      }
      break;
    case 3:
      let question_ans = [];

      // Checks that all fields are filled
      let isQuestionnaireFinished = true;
      let questionnareFields = $("#questionnaire textarea");
      // Checks if the page is completed or not
      for (var i = 0; i < questionnareFields.length; i++) {
        let answer = questionnareFields[i].value;
        question_ans.push(answer);
        let validate = answer.replace(/\s+/g, ""); // Removes empty spaces
        if (validate == "") {
          isQuestionnaireFinished = false;
        }
      }
      if (isQuestionnaireFinished) {
        input.question = question_ans;
        $.ajax({
          type: "POST",
          url: "/receive",
          data: JSON.stringify(input),
          contentType: "application/json",
          success: function(response) {
            console.log("Response sent to server: " + response);
            if (!alert("Your response has been submitted!")) {
              location.reload(true);
            }
          },
          error: function(jqXHR, textStatus, errorThrown) {
            alert("" + textStatus + " " + errorThrown + " An error occured.");
          }
        });
      }
      break;
    default:
      return false;
  }
}

// functions for mouse over
function mouseOver(ev) {
  if (ev.target.children[0] || ev.target) {
    try {
      const p = document.querySelector(".text-hovered");
      if (ev.target.children[0]) {
        p.innerHTML = ev.target.children[0].textContent;
      } else {
        p.innerHTML = ev.target.textContent;
      }
    } catch (err) {}
  }
}
// Functions for Drag & Drop

function drag_handler(ev) {
  ev.dataTransfer.setData("target-id", ev.target.id);
  ev.dataTransfer.effectAllowed = "move";
}

function dragover_handler(ev) {
  ev.preventDefault();
  ev.dataTransfer.dropEffect = "move";
}

function drop_handler(ev) {
  ev.preventDefault();
  let id = ev.dataTransfer.getData("target-id");
  let element = document.getElementById(id);
  ev.currentTarget.appendChild(element);

  let gallerySize = $("#gallery > div").length;

  if (gallerySize == 0) {
    $("#statement-counter").html(0 + "/" + 0);
    return;
  }

  if (galleryIndex == gallerySize) {
    galleryIndex = gallerySize - 1;
    display_statement(galleryIndex);
  } else {
    display_statement(galleryIndex);
  }
}

// Functions for initial sort

function display_statement(index) {
  let statementArray = $("#gallery > div");
  let gallerySize = statementArray.length;

  if (index < 0 || index >= gallerySize) {
    return false;
  }

  $("#gallery > div.current").removeClass("current");
  $(statementArray[index]).addClass("current");

  $("#statement-counter").html(index + 1 + "/" + gallerySize);
  return true;
}

function next_statement() {
  let gallerySize = $("#gallery > div").length;
  if (galleryIndex == gallerySize - 1) {
    galleryIndex = 0;
  } else {
    galleryIndex = galleryIndex + 1;
  }
  display_statement(galleryIndex);

  return true;
}

function previous_statement() {
  let gallerySize = $("#gallery > div").length;
  if (galleryIndex == 0) {
    galleryIndex = gallerySize - 1;
  } else {
    galleryIndex = galleryIndex - 1;
  }
  display_statement(galleryIndex);

  return true;
}

function dragEnter(ev) {
  ev.preventDefault();
  ev.target.classList.add("drag-over");
}

function dragOver(ev) {
  ev.preventDefault();
  ev.target.classList.add("drag-over");
}

function dragLeave(ev) {
  ev.target.classList.remove("drag-over");
}

function drop(ev, parentid) {
  ev.preventDefault();
  try {
    parentbox = document.getElementById(parentid);
    if (parentbox.children.length == 0) {
      parentbox.classList.remove("drag-over");
      let id = ev.dataTransfer.getData("target-id");
      let element = document.getElementById(id);
      parentbox.appendChild(element);
      element.classList.remove("hide");
    } else {
      //gets the original statement
      let original = ev.target.parentElement;
      console.log(original);
      if (!original.children[0].classList.contains("block")) {
        if (original.classList.contains("block")) {
          original = ev.target;
        }
        // //old code
        // parentbox.classList.remove("drag-over");
        let id = ev.dataTransfer.getData("target-id");
        let element = document.getElementById(id);

        console.log(element);
        if (element.parentElement.classList.contains("drop-container")) {
          const o = original;

          var container = document.createElement("div");
          container.appendChild(element.cloneNode(true));
          original.parentElement.innerHTML = container.innerHTML;
          element.innerHTML = o.innerHTML;
          element.id = o.id;
        } else {
          const originalhtml = original.parentElement.innerHTML;
          original.parentElement.innerHTML = element.parentElement.innerHTML;
          element.parentElement.innerHTML = originalhtml;
        }
      }
    }
  } catch (err) {
    console.log(err);
  }
}

// Functions for starting survey
function new_survey() {
  let input = {};
  input.responseType = 0;
  $.ajax({
    type: "POST",
    url: "/startSurvey",
    data: JSON.stringify(input),
    contentType: "application/json",
    success: function(response) {
      responseId = response;
      surveyIndex = 0;
      display_page(0);
      set_instruction(INSTR_BEGIN);
      view_instruction();
      $("#survey-submit").show();
      show_instructions_button();
    },
    error: function(jqXHR, textStatus, errorThrown) {
      alert("" + textStatus + " " + errorThrown + " An error occured.");
    }
  });
  return true;
}

// Resuming survey from a given id
function resume_survey() {
  // Get the inputted user ID
  responseId = $("#survey-start-code").val();

  let input = {};
  input.responseType = 1;
  input.user_id = responseId;
  $.ajax({
    type: "POST",
    url: "/startSurvey",
    data: JSON.stringify(input),
    contentType: "application/json",
    success: function(response) {
      responseId = response.user_id;
      negative_sort = response.negative_sort;
      neutral_sort = response.neutral_sort;
      positive_sort = response.positive_sort;
      matrix = response.matrix;
      if (response.progress == 4) {
        alert(
          "This survey has already been submitted. If you wish to delete your response, please send a message to survey administrator with your response token."
        );
        return;
      }

      $("#response-id-display").html("Response token = " + responseId);

      if (response.progress > 1) {
        load_for_grid();
      }

      if (response.progress == 3) {
        load_statements_to_questionnaire(matrix);
      }

      surveyIndex = response.progress;
      display_page(surveyIndex);
      $("#survey-submit").show(); // Show the button
      show_instructions_button();

      agree_button();
      view_instruction();
    },
    error: function(jqXHR, textStatus, errorThrown) {
      alert("Response not found, check your code and try again.");
    }
  });
  return true;
}

// Unique function used to continue a survey at the grid section
function load_for_grid() {
  for (var i = 0; i < negative_sort.length; i++) {
    let statement = negative_sort[i];
    let element = $("div.unselectable:contains(" + statement + ")")[0];
    $("#sorted-container-grid > div")[0].appendChild(element);
  }
  for (var i = 0; i < neutral_sort.length; i++) {
    let statement = neutral_sort[i];
    let element = $("div.unselectable:contains(" + statement + ")")[0];
    $("#sorted-container-grid > div")[1].appendChild(element);
  }
  for (var i = 0; i < positive_sort.length; i++) {
    let statement = positive_sort[i];
    let element = $("div.unselectable:contains(" + statement + ")")[0];
    $("#sorted-container-grid > div")[2].appendChild(element);
  }
}

function move(clicked) {
  let gallerySize = $("#gallery > div").length;

  let id = document.getElementsByClassName("container unselectable")[
    galleryIndex
  ];
  if (galleryIndex == gallerySize - 1) {
    previous_statement();
    display_statement(galleryIndex);
  }

  if (galleryIndex == gallerySize) {
    clicked.children[0].disabled = true;
  } else {
    //gets me the parent of the button
    clicked.appendChild(id);
    if (gallerySize == 0) {
      $("#statement-counter").html(0 + "/" + 0);
      return;
    }

    if (galleryIndex == gallerySize) {
      galleryIndex = gallerySize - 1;
      display_statement(galleryIndex);
    } else {
      display_statement(galleryIndex);
    }
  }
}

// Instructions
function show_instructions_button() {
  $("#modal-btn").show();
}

function view_instruction() {
  $("#instructions-modal").modal();
}

function set_instruction(index = null) {
  if (index == null) {
    $("#instructions-content").html(
      atos(instructions[surveyIndex + INSTR_OFFSET])
    );
  } else {
    // Manual override to show specific instructions
    let html = atos(instructions[index]);

    if (index == INSTR_USER_ID) {
      html += "<p> Response Token = " + responseId + "</p>";
      html += "<p> Survey ID = " + survey_id + "</p>";
      $("#response-id-display").html("Response token = " + responseId);
    }
    $("#instructions-content").html(html);
  }
}

function modal_button() {
  if (surveyIndex != -1) {
    set_instruction();
  }
  return;
}

function agree_button() {
  set_instruction();

  $("#instructions-agree").hide();
  $("#instructions-close").show();
}

function dismiss_button() {
  set_instruction();

  $("#instructions-dismiss").hide();
  $("#instructions-close").show();
}

// Array of strings to string with paragraph tags
function atos(arr) {
  let string = "";
  let length = arr.length;
  for (var i = 0; i < length; i++) {
    string += "<p>" + arr[i] + "</p>";
  }
  return string;
}

function copy_to_clipboard(string) {
  navigator.clipboard.writeText(string);
}

// Special function to load in grid response in questionnaire

/*
    Input the matrix of the grid sort and returns an array of 2 arrays, containing either the statements
    on the left most column of the grid, or the right most.
*/

function load_statements_to_questionnaire(matrix) {
  let left = matrix[0],
    right = matrix[matrix.length - 1];

  for (var i = 0; i < left.length; i++) {
    if (left[i] != "")
      $(".least-agree").append(
        "<li class='list-group-item'>" + left[i] + "</li>"
      );
  }
  for (var i = 0; i < right.length; i++) {
    if (right[i] != "")
      $(".most-agree").append(
        "<li class='list-group-item'>" + right[i] + "</li>"
      );
  }
}
