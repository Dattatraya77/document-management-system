function show_alert(message, alert){
    // alert for main html
    alert_wrapper.innerHTML = `
    <div class="ml-5 alert alert-${alert} alert-dismissible fade show" role="alert">
      <span>${message}</span>
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>`;
  $('#alert_wrapper').children().first().delay(7000).fadeOut(3000);
};

let openDescButton = document.querySelector('#openTempDescModal');

var isAdvancedUpload = function () {
    var div = document.createElement('div');
    return (('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)) && 'FormData' in window && 'FileReader' in window;
}();

// applying the effect for every form
var forms = document.querySelectorAll('.box');

$(document).ready(function ($) {
    $(".mul-select").select2({
    placeholder: "Click here to select groups that are allowed.",
    closeOnSelect: true,
    tags: false,
    allowClear: true,
    multiple: true,
    tokenSeparators: ['/',',',';'," "],
    });

    Array.prototype.forEach.call(forms, function (form) {
        var input = form.querySelector('input[type="file"]'),
            label = form.querySelector('label'),
            errorMsg = form.querySelector('.box__error span'),
            restart = form.querySelectorAll('.box__restart'),
            droppedFiles = false,
            showFiles = function (files) {
                label.textContent = files[0].name;
            },
            triggerFormSubmit = function () {
                var event = document.createEvent('HTMLEvents');
                event.initEvent('submit', true, false);
                form.dispatchEvent(event);
            };

        // letting the server side to know we are going to make an Ajax request
        var ajaxFlag = document.createElement('input');
        ajaxFlag.setAttribute('type', 'hidden');
        ajaxFlag.setAttribute('name', 'ajax');
        ajaxFlag.setAttribute('value', 1);
        form.appendChild(ajaxFlag);

        // automatically submit the form on file select
        input.addEventListener('change', function (e) {
            showFiles(e.target.files);
//            $("#upload").attr('disabled', false);
        });

        // drag&drop files if the feature is available
        if (isAdvancedUpload) {
            form.classList.add('has-advanced-upload'); // letting the CSS part to know drag&drop is supported by the browser

            ['drag', 'dragstart', 'dragend', 'dragover', 'dragenter', 'dragleave', 'drop'].forEach(function (event) {
                form.addEventListener(event, function (e) {
                    // preventing the unwanted behaviours
                    e.preventDefault();
                    e.stopPropagation();
                });
            });
            ['dragover', 'dragenter'].forEach(function (event) {
                form.addEventListener(event, function () {
                    form.classList.add('is-dragover');
                });
            });
            ['dragleave', 'dragend', 'drop'].forEach(function (event) {
                form.addEventListener(event, function () {
                    form.classList.remove('is-dragover');
                });
            });
            form.addEventListener('drop', function (e) {
                droppedFiles = e.dataTransfer.files; // the files that were dropped
                showFiles(droppedFiles);

            });
//            $("#upload").attr('disabled', false);
        }

        // if the form was submitted
        form.addEventListener('submit', function (e) {
            // preventing the duplicate submissions if the current one is in progress
            if (form.classList.contains('is-uploading')) return false;

            form.classList.add('is-uploading');
            form.classList.remove('is-error');

            if (isAdvancedUpload) // ajax file upload for modern browsers
            {
                e.preventDefault();

                // gathering the form data
                var ajaxData = new FormData(form);
                if (droppedFiles) {
                    Array.prototype.forEach.call(droppedFiles, function (file) {
                        ajaxData.append(input.getAttribute('name'), file);
                    });
                }

                $.ajax({
                    method: 'POST',
                    data: ajaxData,
                    cache: false,
                    contentType: false,
                    processData: false,

                    headers: {
                        "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val()
                    },
                    success: function (response) {
                        form.classList.remove('is-uploading');
                        if(response['success']) {
                            openDescButton.click();
                            if (!response['similarStructure']) {
                                openDescButton.click();

                            } else {
                                if (confirm('Found existing template with same structure.  Do you still want to proceed with training this as a new template?')) {
                                    alert("Proceeding with Training new template. Please add description when saving template to help differentiate from other template with similar looking structure.");
                                    window.location.href = '/trainingStructure/' + response['template_id'];
                                } else {
                                    $.ajax({
                                        url: '/duplicateStructure/' + response['template_id'],
                                        method: 'POST',
                                        data: ({
                                            old_document_id: response['similarStructure'],
                                        }),
                                        headers: {
                                            "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val()
                                        },
                                        success: function (response1) {
                                            if (response1['success']) {
                                                alert('Please select the "Training (blue) button next to the template named "' + response1['templateName'] + '" to update any metadata requirements.');
                                                window.location.reload();
                                            } else {
                                                alert('Something wrong, please create structure manually!');
                                                window.location.reload();
                                            }
                                        },
                                        error: function () {
                                            alert('Something wrong, please create structure manually!');
                                            window.location.reload();
                                        }
                                    });
                                }
                            }
                        }
                        else if (response['debug'] == "Wrong File") {
                            show_alert("Wrong files selection, please select .xlsx files","danger");
                            setTimeout(function(){
                               window.location.reload(1);
                            }, 5000);
                        }
                        else {
                            alert(response['debug'])
                        }

                    },
                    error: function () {
                        form.classList.remove('is-uploading');
                        form.classList.add('is-error');
                        alert('Error. Please, try again');
                    }
                });
            }
            else // fallback Ajax solution upload for older browsers
            {
                var iframeName = 'uploadiframe' + new Date().getTime(),
                    iframe = document.createElement('iframe');

                $iframe = $('<iframe name="' + iframeName + '" style="display: none;"></iframe>');

                iframe.setAttribute('name', iframeName);
                iframe.style.display = 'none';

                document.body.appendChild(iframe);
                form.setAttribute('target', iframeName);

                iframe.addEventListener('load', function () {
                    var data = JSON.parse(iframe.contentDocument.body.innerHTML);
                    form.classList.remove('is-uploading')
                    form.classList.add(data.success == true ? 'is-success' : 'is-error')
                    form.removeAttribute('target');
                    if (!data.success) errorMsg.textContent = data.error;
                    iframe.parentNode.removeChild(iframe);
                });
            }
        });


        // restart the form if has a state of error/success
        Array.prototype.forEach.call(restart, function (entry) {
            entry.addEventListener('click', function (e) {
                e.preventDefault();
                form.classList.remove('is-error', 'is-success');
                input.click();
            });
        });

        // Firefox focus bug fix for file input
        input.addEventListener('focus', function () {
            input.classList.add('has-focus');
        });
        input.addEventListener('blur', function () {
            input.classList.remove('has-focus');
        });

    });
});