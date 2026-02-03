function downloadPdf(path, id) {

    let document_id = id;
    let link = document.createElement("a");
    let uri = window.location.protocol + '//' + window.location.hostname;
    if (window.location.port) uri += ":" + window.location.port;
    let file_list = path.split("/");
    let name = file_list[file_list.length-1];
    let doc_name = name;
    let document_status = "download";

    $.ajax({
        type:'POST',
        url: "/download-view-document/",
        data: {'data' : document_id, 'status': document_status, 'doc_name' : doc_name},
        headers: {
            "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val()
        },
        dataType: "json",
        success: function (response) {
            if (response.success) {
                let link = document.createElement("a");
                link.href = response.file_url;
                link.setAttribute('download', '');
                document.body.appendChild(link);
                link.click();
                link.remove();

                Swal.fire({
                    position: 'top-end',
                    icon: 'success',
                    width: 300,
                    text: 'File downloaded',
                    showConfirmButton: false,
                    timer: 3000
                });
            }
        }

    });
}


function set_preview(path, id) {

    let document_id = id;
    let file_list = path.split("/");
    let name = file_list[file_list.length-1];
    let doc_name = name;
    let document_status = "view";

    $.ajax({
        type:'POST',
        url: "/download-view-document/",
        data: {'data' : document_id, 'status': document_status, 'doc_name' : doc_name },
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val()
        },
        dataType: "json",
        beforeSend: function () {
            loader('show');
        },
        complete: function () {
            loader('hide');
        },
        success: function (response) {
            if (!response.success) return;

            const extension = response.extension;
            const fileUrl = response.file_url;
            const fileSize = response.file_size;

            $("#document_viewer").attr('src', '');
            $("#document_modal").modal('hide');

            if (["docx","xlsx","xls","doc","docm","pptx"].includes(extension)) {

                let officeViewer =
                    "https://view.officeapps.live.com/op/embed.aspx?src=" +
                    encodeURIComponent(window.location.origin + fileUrl);

                $("#document_viewer").attr('src', officeViewer);
                $("#document_modal").modal('show');

            } else if (["png","jpg","jpeg","gif","pdf","txt","html"].includes(extension)) {

                $("#document_viewer").attr('src', fileUrl);
                $("#document_modal").modal('show');

            } else if (extension === "rtf") {

                let googleViewer =
                    "https://docs.google.com/viewerng/viewer?url=" +
                    encodeURIComponent(window.location.origin + fileUrl) +
                    "&embedded=true";

                $("#document_viewer").attr('src', googleViewer);
                $("#document_modal").modal('show');

            } else {

                let cadViewer =
                    "https://sharecad.org/cadframe/load?url=" +
                    encodeURIComponent(window.location.origin + fileUrl);

                $("#document_viewer").attr('src', cadViewer);
                $("#document_modal").modal('show');
            }
        }

    });
}


function downloadURI(path, id) {
    let document_id = id;
    let link = document.createElement("a");
    let uri = window.location.protocol + '//' + window.location.hostname;
    if (window.location.port) uri += ":" + window.location.port;
    link.href = uri + '/media/' + path;
    link.click();

    let file_list = path.split("/");
    let name = file_list[file_list.length-1];
    let doc_name = name;
    let document_status = "download";

    $.ajax({
        type:'POST',
        url: "/download-view-document/",
        data: {'data' : document_id, 'status': document_status, 'doc_name' : doc_name },
        headers: {
            "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val()
        },
        dataType: "json",
        success: function (response){
            if(response['success']) {
                var data = response['messages'];
                Swal.fire({
                  position: 'top-end',
                  icon: 'success',
                  width:300,
                  text: data,
                  showConfirmButton: false,
                  timer: 5000
                })
            }
        }
    });
}


function allMetas (id) {
    $.ajax({
        type:'GET',
        url:'/all-metas/',
        data:{
            documentId: id,
        },
        success:function(response){
            if (response['internal']) {
                let metas = response['metas'];
                document.getElementById('internalDiv').removeAttribute('hidden');
                document.getElementById('metaValueRow').innerHTML = '';
                for(let i=0; i<metas.length; i++) {
                    metakey = metas[i]['meta_key'];
                    metatype = metas[i]['meta_type'];
                    metavalue = metas[i]['meta_value']

                    metaValueRow.innerHTML += `<tr>
                                                <td>${metakey}</td>
                                                <td>${metatype}</td>
                                                <td style ="word-break:break-all;">${metavalue}</td>
                                               </tr>`
                };
            }

            else {
                document.getElementById('internalDiv').setAttribute('hidden', true);
            }

            if (response['external']) {
                let exMetas = response['ex_meta_list'];
                document.getElementById('externalDiv').removeAttribute('hidden');

                exMetaValueRow = document.getElementById('externalMetaTable');
                exMetaValueRow.innerHTML = '';

                for(let i=0; i<exMetas.length; i++) {
                    metakey = exMetas[i]['meta_key'];
                    metatype = exMetas[i]['meta_type'];
                    metavalue = exMetas[i]['meta_value']

                    exMetaValueRow.innerHTML += `<tr>
                                                <td>${metakey}</td>
                                                <td>${metatype}</td>
                                                <td style ="word-break:break-all;">${metavalue}</td>
                                               </tr>`
                };
            }

            else {
                document.getElementById('externalDiv').setAttribute('hidden', true);
            }

            $('#allMetaModal').modal('show');
            },error : function(response) {
                alert("Sorry, following error occured:" + response['error']);
            }
    });
}


function downloadDLF(path, id) {
    let document_id = id;
    let link = document.createElement("a");
    let uri = window.location.protocol + '//' + window.location.hostname;
    if (window.location.port) uri += ":" + window.location.port;
    let file_list = path.split("/");
    let name = file_list[file_list.length-1];
    link.href = uri + '/media/' + path;
    link.setAttribute('download',name);
    link.click();
}


function dlf_preview(path, id) {
    let uri = "https://docs.google.com/gview?url=";
    uri += window.location.protocol + '//';
    uri += window.location.hostname;
    if (window.location.port) uri += ':' + window.location.port;
    uri += path + '&embedded=true';
    $("#document_modal #document_viewer").attr('src', uri);
    $("#document_modal").modal('show');
}


function continue_to_view_file(){
    $("#document_viewer").show();
    $("#big-file-size").html('');
}