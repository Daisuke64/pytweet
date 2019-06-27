function toggle_like(id){
    const like_id = '#heart-' + id

    if($(like_id).hasClass('fa-heart')) {
        unlike_pytweet(id)
    } else {
        like_pytweet(id)
    }
}

function like_pytweet(id){
    $.ajax({
        type: 'POST',
        url: '/pytweet/' + id + '/favorite',
        data: null,
        contentType: 'application/json'
    }).done( function(data) {
        $('#heart-' + id).removeClass('fa-heart-broken')
        $('#heart-' + id).addClass('fa-heart')
        $('#like-' + id).text(data)
        $('#like-btn-' + id).removeClass('text-dark')
        $('#like-btn-' + id).addClass('text-danger')
    })
}

function unlike_pytweet(id){
    $.ajax({
        type: 'DELETE',
        url: '/pytweet/' + id + '/favorite',
        date: null,
        contentType: 'application/json'
    }).done( function(data) {
        $('#heart-' + id).removeClass('fa-heart')
        $('#heart-' + id).addClass('fa-heart-broken')
        $('#like-' + id).text(data)
        $('#like-btn-' + id).removeClass('text-danger')
        $('#like-btn-' + id).addClass('text-dark')
    })
}