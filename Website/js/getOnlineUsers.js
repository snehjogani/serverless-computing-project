get_online_users_link = "https://us-east4-serverless-data-processing.cloudfunctions.net/get-user-list";
function setToUser(email, username) {
    localStorage.setItem('toUser', email)
    localStorage.setItem('toUserName', username)
    // var email = localStorage.getItem('current_user')
    // var url = 'http://35.197.100.199:5000/publish?msg=' + '&touser=' + toUser + '&fromuser=' + email
    // var data = JSON.stringify({
    //     "email": email,
    // })
}

function get_online_users() {
    var email = localStorage.getItem('current_user')
    var data = JSON.stringify({
        "email": email
    });
    console.log(data)
    console.log("USER: " + data)
    var config = {
        "url": get_online_users_link,
        "method": "POST",
        "timeout": 0,
        "data": data,
    };
    $.ajax(config).done(function (response) {
        var online_users = response.data
        console.log(online_users)
        console.log(online_users.length)
        var i;
        var content = '';
        for (i = 0; i < online_users.length; i++) {
            var name = online_users[i]['name'];
            var email_fetched = online_users[i]['email'];
            var institute = online_users[i]['instituteName'];
            // var role = online_users[i]['role'];
            if (email === email_fetched) {
                // document.getElementById('usernamespan').innerText = "Welcome, " + name;
                localStorage.setItem('name', name);
            } else {
                var newdiv1 = `
                <div class="col-xl-3 col-md-6 mb-4">
                    <div class="card border-left-primary shadow h-100 py-2">
                        <div class="card-body">
                            <div class="row no-gutters align-items-center">
                                <div class="col-auto mr-2">
                                    <i class="fas fa-user fa-2x text-gray-300"></i>
                                </div>
                                <div class="col">
                                    <div class="h5 mb-0 font-weight-bold text-primary text-uppercase mb-1"><a target="_blank" href="chatbox.html" onClick="setToUser('${email_fetched}', '${name}')">
                                    Name: ${name}
                                    </a>
                                    </div>
                                    <div class="text-xs font-weight-bold text-gray-500 text-uppercase ">Institute: ${institute}
                                    </div>
                                </div>                                
                            </div>
                        </div>
                    </div>
                </div>
            `;
                content += newdiv1;
            }
        }
        $('#parentOnlineUserDiv').html(content)
    })
}
