function toggle_retweet(id){
    const retweet_id = '#retweet-btn-' + id

    if($(retweet_id).hasClass('text-success')) {
        unretweet_pytweet(id)
    } else {
        retweet_pytweet(id)
    }
}

function unretweet_pytweet(id){
    $.ajax({
        type: 'DELETE',
        url: '/pytweet/' + id + '/retweet',
        data: null,
        contentType: 'application/json'
    }).done( function(data) {
        $('#retweet-' + id).text(data)
        $('#retweet-btn-' + id).removeClass('text-success')
        $('#retweet-btn-' + id).addClass('text-dark')
    })
}

function retweet_pytweet(id){
    $.ajax({
        type: 'POST',
        url: '/pytweet/' + id + '/retweet',
        date: null,
        contentType: 'application/json'
    }).done( function(data) {
        $('#retweet-' + id).text(data)
        $('#retweet-btn-' + id).removeClass('text-dark')
        $('#retweet-btn-' + id).addClass('text-success')
    })
}