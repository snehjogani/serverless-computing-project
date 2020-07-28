function fileUpload() {
    var form = new FormData();
    var fileInput = document.getElementById("uploadfile");
    form.append("file", fileInput.files[0], fileInput.files[0].name);
    var settings = {
        "url": "http://35.197.100.199:5000/predict",
        "method": "POST",
        "timeout": 0,
        "headers": {},
        "processData": false,
        "mimeType": "multipart/form-data",
        "contentType": false,
        "data": form
    };
    $.ajax(settings).done(function (response) {
        var response = JSON.parse(response);
        console.log(response.cluster)
        alert("File uploaded successfully")
        var cluster_number = response.cluster;
        var str = `<div class="text-center">
                    <h6 class="text-gray-900 mb-4">Cluster:${cluster_number}</h6>
                   </div>                   
            `
            console.log(str);
            $('#clusterDiv').html(str);
        
    }).fail(function (error) {
        console.log(error);
    });
}