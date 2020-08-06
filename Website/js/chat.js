var outputArea = $("#chat-output");

$("#toUser").html(`<span>${localStorage.getItem('toUserName')}</span>`)

$("#user-input-form").on("submit", function (e) {

  e.preventDefault();

  var message = $("#user-input").val();

  var toUser = localStorage.getItem('toUser')
  var fromUser = localStorage.getItem('current_user')

  toUser = toUser.split('@')[0]
  fromUser = fromUser.split('@')[0]

  var url = 'http://35.197.100.199:5000/publish?msg=' + message + '&touser=' + toUser + '&fromuser=' + fromUser

  var config = {
    "url": url,
    "method": "GET",
    "timeout": 0,
  };

  $.ajax(config).done(function (response) {
    outputArea.append(`
      <div class='bot-message'>
        <div class='message'>
          ${message}
        </div>
      </div>
    `);
    $("#user-input").val("");
  })
});

setInterval(function () {
  var fromUser = localStorage.getItem('toUser')
  fromUser = fromUser.split('@')[0]

  var url = 'http://35.197.100.199:5000/subscribe?fromuser=' + fromUser

  var config = {
    "url": url,
    "method": "GET",
    "timeout": 0,
  };

  $.ajax(config).done(function (response) {
    for (i = 0; i < response.length; i++) {
      var message = response[i]
      outputArea.append(`
        <div class='user-message'>
          <div class='message'>
            ${message}
          </div>
        </div>
      `);
    }
  })
}, 5000);