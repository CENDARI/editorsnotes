var toastr_options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": true,
    "progressBar": false,
    "positionClass": "toast-top-center",
    "preventDuplicates": true,
    "onclick": null,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "5000000000000000",
    "extendedTimeOut": "5000000000000000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
}

function showToastrMessage(type,message){
    toastr.clear();
    toastr[type](message);
}

function showErrorMessage(message){
    toastr.options.timeOut="1000";
    toastr.options.extendedTimeOut="1000";
    showToastrMessage('error',message);
}

function showSuccessMessage(message){
    toastr.options.timeOut="500";
    toastr.options.extendedTimeOut="1000";
    showToastrMessage('success',message);
}


function showWarningMessage(message){
    toastr.options.timeOut="5000";
    toastr.options.extendedTimeOut="10000";
    showToastrMessage('warning',message);
}

function showInfoMessage(message){
    toastr.options.timeOut="5000000000000000";
    toastr.options.extendedTimeOut="5000000000000000";
    showToastrMessage('info',message)
}

$(document).ready(function() {
    toastr.options = toastr_options
});
