$(document).ready(function ($) {
    if ($("#logged_in").val()) {
        $("#newTipModal").modal('show');
    }

});

function user_logout_func(current_user) {
    var username = current_user;

    Swal.fire({
        position: 'top',
        title: username+'<h5>Are you sure you want to log out?</h5>',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        cancelButtonText: 'No',
        confirmButtonText: 'Yes',
        reverseButtons: true,
        customClass : {
            popup: 'swal2-popup-custom',
            icon : 'swal2-icon.swal2-warning',
            confirmButton: 'swal2-styled.swal2-confirm',
            cancelButton: 'swal2-styled.swal2-cancel',
        },
        }).then((result) => {
            if(result.isConfirmed){
            $.ajax({
                type: "POST",
                url: '/logout/',
                data: {
                    'csrfmiddlewaretoken':$('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function (response) {

                    Swal.fire({
                        position: 'top',
                        icon: 'success',
                        width:300,
                        text: 'User "'+username +'" logged out successfully!',
                        showConfirmButton: false,
                        timer: 5000
                    })
                    setTimeout(function(){
                       window.location.href = '/logout/';
                    }, 1500);
                }
            });
        }
    })
}