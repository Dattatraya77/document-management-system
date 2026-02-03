$(document).ready(function ($) {
    $(".mul-select").select2({
    placeholder: "Click here to select groups that are allowed.",
    closeOnSelect: true,
    tags: false,
    allowClear: true,
    multiple: true,
    tokenSeparators: ['/',',',';'," "],
    });
});

// create_document_template.js
document.addEventListener("DOMContentLoaded", function () {

    document.querySelectorAll("input[type=file]").forEach(input => {
        input.addEventListener("change", function () {
            if (this.files[0] && this.files[0].size > 2_000_000) {
                alert("Image too large (max 2MB)");
                this.value = "";
            }
        });
    });

    // Auto-expand textarea like MS Word
    document.addEventListener("input", function (e) {
        if (e.target.matches("textarea.textarea-input")) {
            const textarea = e.target;

            textarea.style.height = "auto";              // reset
            textarea.style.overflowY = "hidden";         // important
            textarea.style.height = textarea.scrollHeight + "px";
        }

        // Auto-grow width for inline text inputs
        if (e.target.matches("input.text-input")) {
            const input = e.target;
            input.style.width = Math.max(input.value.length + 1, 6) + "ch";
        }
    });


});

$("#file_name").keypress(function (e) {

    var keyCode = e.keyCode || e.which;
    $("#fileNameError").html("");

    var regex = /^[/:;*?<>|"'\\]+$/;
    var isValid = regex.test(String.fromCharCode(keyCode));
    var invalid_char = '\\ / : * ? " | ; < >'+"'";

    if (isValid) {
        $("#fileNameError").html('A file name can not contain any of the characters: '+ invalid_char+'');
    }
    return !isValid;
});


window.addEventListener("load", function () {
    document.querySelectorAll("textarea.textarea-input").forEach(textarea => {
        textarea.style.height = "auto";
        textarea.style.height = textarea.scrollHeight + "px";
    });
});



let currentSigKey = null;
let sigPad = null;

document.addEventListener("click", function (e) {

    // ---------------- OPEN MODAL ----------------
    if (e.target.classList.contains("signature-btn")) {
        currentSigKey = e.target.dataset.key;

        const sigImage = document.getElementById("sigImage");
        const hiddenInput = document.getElementById(currentSigKey + "_value");

        // reset everything
        sigImage.value = "";
        sigImage.removeAttribute("name");

        hiddenInput.value = "";
        hiddenInput.name = currentSigKey;   // ✅ VERY IMPORTANT

        document.getElementById(currentSigKey + "_preview").innerHTML = "";

        document.getElementById("signatureModal").style.display = "flex";

        const canvas = document.getElementById("sigCanvas");
        sigPad = new SignaturePad(canvas);
    }

    // ---------------- CLEAR ----------------
    if (e.target.id === "sigClear") {
        if (sigPad) sigPad.clear();
        document.getElementById("sigTypeText").value = "";
        document.getElementById("sigImage").value = "";
    }

    // ---------------- CANCEL ----------------
    if (e.target.id === "sigCancel") {
        closeSignatureModal();
    }

    // ---------------- SAVE ----------------
    if (e.target.id === "sigSave") {
        const type = document.querySelector("input[name='sig_type']:checked").value;

        const hiddenInput = document.getElementById(currentSigKey + "_value");
        const sigImage = document.getElementById("sigImage");

        // ---------- DRAW ----------
        if (type === "draw") {
            if (sigPad.isEmpty()) {
                alert("Please draw signature");
                return;
            }

            const dataURL = sigPad.toDataURL("image/png");

            hiddenInput.name = currentSigKey;     // ✅ POST
            hiddenInput.value = dataURL;

            sigImage.removeAttribute("name");     // ❌ FILES

            document.getElementById(currentSigKey + "_preview").innerHTML =
                `<img src="${dataURL}" class="sig-preview-img">`;
        }

        // ---------- TYPE ----------
        if (type === "type") {
            const text = document.getElementById("sigTypeText").value.trim();
            if (!text) {
                alert("Please type signature");
                return;
            }

            hiddenInput.name = currentSigKey;     // ✅ POST
            hiddenInput.value = text;

            sigImage.removeAttribute("name");     // ❌ FILES

            document.getElementById(currentSigKey + "_preview").innerHTML =
                `<span class="typed-signature">${text}</span>`;
        }

        // ---------- IMAGE ----------
        if (type === "image") {
            const file = sigImage.files[0];
            if (!file) {
                alert("Please upload image");
                return;
            }

            sigImage.name = currentSigKey;        // ✅ FILES
            hiddenInput.removeAttribute("name");  // ❌ POST

            document.getElementById(currentSigKey + "_preview").innerHTML =
                `<img src="${URL.createObjectURL(file)}" class="sig-preview-img">`;
        }

        closeSignatureModal();
    }
});

// ---------------- RADIO TOGGLE ----------------
document.querySelectorAll("input[name='sig_type']").forEach(radio => {
    radio.addEventListener("change", function () {
        document.getElementById("sigCanvas").style.display =
            this.value === "draw" ? "block" : "none";

        document.getElementById("sigImage").style.display =
            this.value === "image" ? "block" : "none";

        document.getElementById("sigTypeText").style.display =
            this.value === "type" ? "block" : "none";
    });
});

// ---------------- CLOSE MODAL ----------------
function closeSignatureModal() {
    document.getElementById("signatureModal").style.display = "none";
    if (sigPad) sigPad.clear();
}

