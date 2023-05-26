// Adding and removing elements
$(document).ready(function () {
  $("form").submit(function (event) {
    event.preventDefault();
  });
  //Sending post request
  function submitForm(address, content) {
    $.post(address, content)
      .done(function () {
        //Request is successful and reset is triggered
        alert("Request was successful!");
        $("form")[0].reset();
      })
      .fail(function () {
        //Request is unsuccessful and reset is triggered
        alert("Request was unsuccessful!");
        $("form")[0].reset();
      });
  }

  $("#button1").click(function () {
    //User inputs for adding element
    var content = {
      ElementNumber: $("#ElementNumber").val(),
      ElementCode: $("#ElementCode").val(),
      ElementName: $("#ElementName").val(),
      colour1: $("#colour1").val(),
      colour2: $("#colour2").val(),
      colour3: $("#colour3").val(),
      radius: $("#radius").val(),
    };
    //Post request is sent to server with content
    submitForm("/elementAdd.html", content);
  });

  $("#button2").click(function () {
    //User inputs for removing element
    var content = {
      remove: $("#remove").val(),
    };
    //Post request is sent to server with content
    submitForm("/elementRemove.html", content);
    //Trigger reset
    $("#remove").val("");
  });
});

// Uploading sdf file
$(document).ready(function () {
  //Store variables
  var $form = $("form");
  var $molN = $("#molN");
  var $fileVersion = $("#fileVersion");
  var $passForm = $("#passForm");

  $form.submit(function (event) {
    event.preventDefault();
  });
  //Click upload button
  $("#button4").click(function () {
    //Receive molecule name and file
    var name = $molN.val().trim();
    var fileVersion = $fileVersion[0].files[0];

    var formData = new FormData();
    //add name and file
    formData.append("molecule-name", name);
    formData.append("fileSdf", fileVersion);

    //Direct ajax request to server
    $.ajax({
      url: "/fileUpload",
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
    })
      //Alert for if file was uploaded successfully
      .done(function () {
        alert("File uploaded!");
      })
      .fail(function () {
        //Alert for if file was not ploaded successfully
        alert("Error. File not uploaded.");
      })
      .always(function () {
        //Reset
        $passForm.trigger("reset");
      });
  });
});

//Display molecule
$(document).ready(function () {
  //GET request is being sent
  $.ajax({
    url: "/grabMol",
    type: "GET",
    dataType: "json",
    success: function (content, current) {
      //Need element
      var allMol = $("#allMolList");
      allMol.empty();
      if (current.status === 204) {
        console.log("Nothing is present");
      } else {
        var mole = content;
        //Going through molecule array
        for (var i = 0; i < mole.length; i++) {
          var molecule = mole[i];

          var molTable = $('<div class="molecule-bar"></div>');
          allMol.append(molTable);
          //Create button
          $("<button>")
            .addClass("molecule-name")
            .text(molecule.name)
            .appendTo(molTable)
            .on("click", function () {
              var nameMole = $(this).text();
              molProcess(nameMole);
            })
            //To show and hide atom and bond count
            .on("mouseenter", function () {
              $(this).next(".molecule-counts").show();
            })
            .on("mouseleave", function () {
              $(this).next(".molecule-counts").hide();
            })
            .css("margin-bottom", "16px");
          //Add to div
          var moleC = $('<div class="molecule-counts"></div>')
            .hide()
            .append(
              $('<span class="molecule-atoms"></span>').text(
                "Atoms Count: " + molecule.numAtom + "    "
              )
            )
            .append(
              $('<span class="molecule-bonds"></span>').text(
                "Bonds Count: " + molecule.numBond + " "
              )
            )
            .appendTo(molTable);
        }
      }
    },
  });

  function molProcess(nameMole) {
    //Sending a post request
    $.ajax({
      url: "/inspectMolecule",
      type: "POST",
      data: { nameMole: nameMole },
      success: function (content) {
        //Modify the height and width
        content = content.replace('width="1000"', 'width="500"');
        content = content.replace('height=1000"', 'height="400"');
        content = content.replace(
          "<svg ",
          '<svg version="1.1" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid meet" '
        );
        //Append file content
        $("#displayimg").empty().append(content);
        $("html, body").animate(
          {
            scrollTop: $(document).height(),
          },
          1000
        );
        //Rotation buttons
        $("#rotbutton").show();
      },
    });
  }
});

$(document).ready(function () {
  $(".rotate-btn").click(function () {
    //Receive data from clicked button
    var axis = $(this).data("axis");
    rotateFunc(axis);
  });
});

function rotateFunc(axis) {
  //Send post request to rotate
  $.ajax({
    url: "/rotate",
    type: "POST",
    data: { axis: axis },
    success: function (response) {
      //getSDF fubction call if successful
      getSDF();
    },
  });
}

function getSDF() {
  //Get request for sdf file
  $.ajax({
    url: "/fileFormat",
    type: "GET",
    dataType: "text",
    success: function (content, current) {
      var displayBox = $("#displayimg");
      displayBox.empty();
      if (current.status === 204) {
        console.log("Nothing is present");
      } else {
        //Modify the height and width
        content = content.replace('width="1000"', 'width="500"');
        content = content.replace('height=1000"', 'height="400"');
        content = content.replace(
          "<svg ",
          '<svg version="1.1" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid meet" '
        );
        //Append file content
        displayBox.append(content);
      }
    },
  });
}
