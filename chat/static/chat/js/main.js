const chat_socket = new WebSocket(ws_endpoint);

chat_socket.onmessage = function (e) {
    console.log(e.data);
    $("#room").html($("#room").html() + '<br/>' + e.data);
};

chat_socket.onopen = function (e) {
    console.log('Websocket Connected');
    $('#msg').removeClass('red');
    $('#msg').addClass('green');
};

chat_socket.onclose = function (e) {
    console.log('Websocket Disconnected');
    $('#msg').removeClass('green');
    $('#msg').addClass('red');

};

chat_socket.onerror = function (e) {
    console.log('Websocket Error');
    console.log(e);
    $('#msg').removeClass('green');
    $('#msg').addClass('yellow');

};

$('#sendbtn').click(function (e) {
    let msg = $('#msg').val();
    chat_socket.send(msg);
    $('#msg').val('');
});
