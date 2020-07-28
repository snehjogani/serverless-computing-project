var Lambda_function_login = 'https://895rj8lhk0.execute-api.us-east-1.amazonaws.com/v1/';
var GCP_twofa = 'https://us-east4-serverless-data-processing.cloudfunctions.net/user-authentication-second-factor';

function twofa() {
    var question = $('#question').val();
    var answer = $('#answer').val();
    var email = $('#email').val();
    console.log(question, answer)
    var data = JSON.stringify({
        "question": question,
        "answer": answer,
        "email": email
    })
    var config = {
        "url": GCP_twofa,
        "method": "POST",
        "timeout": 0,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": data,
    };
    $.ajax(config).done(function (response) {
        localStorage.setItem('current_user', email);
        window.location.href = "index.html"
    }).fail(function (error) {
        console.log(error)
        if (error.responseJSON.error) {
            alert(error.responseJSON.error);
        }
        window.location.href = "login.html"
    });
}
function login() {
    var email = $('#email').val();
    var password = $('#password').val();
    console.log(email, password)
    var data = JSON.stringify({
        "email": email,
        "password": password
    })
    console.log(data)
    var config = {
        "url": Lambda_function_login,
        "method": "POST",
        "timeout": 0,
        "headers": {
            "Content-Type": "application/json"
        },
        "data": data,
    };
    console.log("data posted succussfully")
    $.ajax(config).done(function (response) {
        console.log(response.user)
        if (response.statusCode == 200) {
            // window.location.href = "index.html"
           // var body = JSON.parse(response.user)
            console.log(response.user.email)
            var email = response.user.email
            var question = response.user.question
            console.log(email, question)
            var str = `<div class="text-center">
                    <h1 class="h4 text-gray-900 mb-4">Please answer the security question.</h1>
                </div>
                <form class="user">
                    <div class="form-group">
                        <input type="text" style="visibility: hidden" class="form-control form-control-user" id="email" aria-describedby="emailHelp"
                        value="${email}" disabled>
                    </div>
                    <div class="form-group">
                        <input type="text" class="form-control form-control-user" id="question" aria-describedby="questionHelp"
                        value="${question}" disabled>
                    </div>
                    <div class="form-group">
                        <input type="text" class="form-control form-control-user" id="answer"
                        placeholder="Your Answer">
                    </div>
                    <button onclick="twofa();" type="button" class="btn btn-success btn-user btn-block">Submit</button>
                </form>
            `
            console.log(str);
            $('#parentDiv').html(str);
        }


    }).fail(function (error) {
        console.log(error)
        if (error.responseJSON.message) {
            alert(error.responseJSON.message);

        } else {
            alert(error.responseJSON.error);
        }
    })
    console.log("function ends here")
    ;
}
