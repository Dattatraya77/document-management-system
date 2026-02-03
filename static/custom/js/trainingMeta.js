
let count = 0;
let metadataLocal = [];

document.addEventListener("DOMContentLoaded", function () {

    /* ---------------- DOM ELEMENTS ---------------- */
    const allSpans = document.querySelectorAll('.document-box span[id^="span"]');
    const documentLastSpan = document.querySelector('#lastSpan')?.innerHTML;
    const existingFoundSpan = document.querySelector('#existingFound');

    const metaHeader = document.querySelector('#trainingMetaName');

    const next_btn = document.querySelector('#nextPara');
    const save_btn = document.querySelector('#saveMeta');
    const saveMotButton = document.querySelector('#saveMotButton');
    const openModal = document.querySelector('#openModalButton');

    const input_type = document.querySelector('#metaType');
    const input_label = document.querySelector('#metaName');
    const input_text = document.querySelector('#mataText');

    const meta_choice_div = document.getElementById('meta_choice_div');

    const progressCounter = document.querySelector('#progressCounter');
    const undo_btn = document.querySelector('#undoMeta');
    const totalCount = allSpans.length;

    function updateProgress() {
        progressCounter.innerText = `${count + 1} / ${totalCount}`;
    }

    if (!allSpans.length || !next_btn || !save_btn) {
        console.error("Training Meta JS: required elements missing");
        return;
    }

    let currentSpan = allSpans[0];
    let currentSpanId = currentSpan.id;

    /* ---------------- HELPERS ---------------- */
    function cleanMeta(text) {
        let t = text.replace('{{', '').replace('}}', '').trim();
        return {
            key: t,
            label: t.replaceAll('_', ' ')
        };
    }

    function highlightSpan(span) {
        span.scrollIntoView({ behavior: "smooth", block: "center" });
        span.classList.add('metaHighlited');
    }

    function loadSpan() {
        highlightSpan(currentSpan);
        updateProgress();
        highlightActiveMeta(currentSpanId);

        const cleaned = cleanMeta(currentSpan.innerHTML);
        metaHeader.innerHTML = count + 1;

        input_label.value = cleaned.key;
        input_text.value = cleaned.label;

        // Existing metadata lock
        if (typeof exMetaKeys !== "undefined" && cleaned.key in exMetaKeys) {
            existingFoundSpan.innerHTML = 'Found Existing: Yes (Changes not allowed)';
            input_type.value = exMetaKeys[cleaned.key][0];
            input_type.setAttribute("disabled", true);
            input_text.setAttribute("disabled", true);
        } else {
            existingFoundSpan.innerHTML = 'Found Existing: No';
            input_type.removeAttribute("disabled");
            input_text.removeAttribute("disabled");
        }

        next_btn.setAttribute("disabled", true);
        save_btn.removeAttribute("disabled");
    }

    /* ---------------- EVENTS ---------------- */

    next_btn.addEventListener('click', function () {
        loadSpan();
    });

    input_type.addEventListener('change', function () {
        if (this.value === 'choice') {
            meta_choice_div.removeAttribute('hidden');
        } else {
            meta_choice_div.setAttribute('hidden', true);
        }
    });

    save_btn.addEventListener('click', function () {

        undo_btn.removeAttribute('disabled');

        const description = input_text.value;
        const metaId = currentSpanId.replace("span", '');

        if (input_type.value === 'choice') {
            let metaChoices = [];
            document.querySelectorAll("#meta_key_choices option:checked").forEach(opt => {
                metaChoices.push(opt.value + ' ');
            });

            metadataLocal.push({
                id: metaId,
                description: description,
                type: input_type.value,
                choices: metaChoices
            });

            meta_choice_div.setAttribute('hidden', true);
        } else {
            metadataLocal.push({
                id: metaId,
                description: description,
                type: input_type.value
            });
        }

        currentSpan.classList.remove('metaHighlited');
        currentSpan.classList.add('metaProcessed');

        save_btn.setAttribute('disabled', true);
        next_btn.removeAttribute('disabled');

        if (metaId === documentLastSpan) {
            next_btn.setAttribute('disabled', true);
            openModal.removeAttribute('hidden');
        } else {
            count++;
            currentSpan = allSpans[count];
            currentSpanId = currentSpan.id;
            setTimeout(() => next_btn.click(), 400);
        }
    });

    /* ---------------- MOT SAVE ---------------- */
    saveMotButton?.addEventListener('click', function () {
        const checks = document.getElementsByName("m_o_t");
        for (let i = 0; i < checks.length; i++) {
            if (checks[i].checked) {
                metadataLocal.push({
                    id: checks[i].value,
                    mot: true
                });
            }
        }
        addMetadata();
    });

    /* ---------------- AJAX ---------------- */
    function addMetadata() {
        console.log("Data:->", JSON.stringify(metadataLocal));
        $.ajax({
            type: 'POST',
            data: {
                template_id: document.getElementById("template_id").value,
                provision_data: JSON.stringify(metadataLocal)
            },
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            },
            success: function (response) {
                if (response.success) {
                    window.location.href = '/train-docx-template/';
                } else {
                    alert(response.debug);
                }
            },
            error: function () {
                alert('Error, try again!');
            }
        });
    }


    undo_btn.addEventListener('click', function () {

        if (count === 0) return;

        // Remove last metadata
        metadataLocal.pop();

        // Reset current span
        currentSpan.classList.remove('metaProcessed');
        currentSpan.classList.remove('metaHighlited');

        // Move back
        count--;
        metaHeader.innerHTML = count + 1;

        currentSpan = allSpans[count];
        currentSpanId = currentSpan.id;

        // Restore highlight
        currentSpan.classList.add('metaHighlited');
        highlightActiveMeta(currentSpanId);

        // Enable editing again
        save_btn.removeAttribute('disabled');
        next_btn.setAttribute('disabled', true);

        undo_btn.setAttribute('disabled', count === 0);

        updateProgress();
    });

    undo_btn.setAttribute('disabled', true);

});


function applyMetaTypeHighlighting() {
    document.querySelectorAll('#document-box span[id^="span"]').forEach(span => {

        // Extract key name from {{KEY}}
        const rawText = span.innerText || span.textContent;
        const metaKey = rawText.replace('{{', '').replace('}}', '').trim();

        if (exMetaKeys[metaKey]) {
            const metaType = exMetaKeys[metaKey][0];

            span.classList.add('meta');               // base style
            span.classList.add(`meta-${metaType}`);   // type style
            span.classList.add('meta_init');          // your existing class
        }
    });
}

document.addEventListener("DOMContentLoaded", applyMetaTypeHighlighting);


function highlightActiveMeta(spanId) {
    document.querySelectorAll('.meta').forEach(el =>
        el.classList.remove('meta-active')
    );

    const activeSpan = document.getElementById(spanId);
    if (activeSpan) {
        activeSpan.classList.add('meta-active');
        activeSpan.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}




