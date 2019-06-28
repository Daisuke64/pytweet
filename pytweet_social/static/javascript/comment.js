function add_comment(id){
    var my_comment = $("#my-comment").val()
    $.ajax({
        type:"POST",
        url: "/" + id + "/comment/add",
        data: { comment: my_comment }
    }).done( function(data){
        $(".comment-section").html(data)
        document.getElementById("my-comment").value = ""
        console.log(data)
    })
}

function delete_comment(id){
    $.ajax({
        type:"POST",
        url: "/comment/" + id + "/delete/",
    }).done( function(data){
        $(".comment-section").html(data)
        console.log(data)
    })
}

function toggle_comment_like(id){
    const like_id = '#heart-comment-' + id

    if($(like_id).hasClass('fa-heart')) {
        unlike_comment(id)
    } else {
        like_comment(id)
    }
}

function like_comment(id){
    $.ajax({
        type: 'POST',
        url: '/comment/' + id + '/favorite',
        data: null,
        contentType: 'application/json'
    }).done( function(data) {
        $('#heart-comment-' + id).removeClass('fa-heart-broken')
        $('#heart-comment-' + id).addClass('fa-heart')
        $('#like-comment-' + id).text(data)
        $('#like-comment-btn-' + id).removeClass('text-dark')
        $('#like-comment-btn-' + id).addClass('text-danger')
        console.log(data)
    })
}

function unlike_comment(id){
    $.ajax({
        type: 'DELETE',
        url: '/comment/' + id + '/favorite',
        date: null,
        contentType: 'application/json'
    }).done( function(data) {
        $('#heart-comment-' + id).removeClass('fa-heart')
        $('#heart-comment-' + id).addClass('fa-heart-broken')
        $('#like-comment-' + id).text(data)
        $('#like-comment-btn-' + id).removeClass('text-danger')
        $('#like-comment-btn-' + id).addClass('text-dark')
        console.log(data)
    })
}

//subcomments
function view_subcomment(id){
    $.ajax({
        type: "GET",
        url: "/comments/" + id + "/sub/",
        contentType: "application/json",
    }).done( function(data){
        $("#sub-comment-list-" +id).html(data)
        $("#comment-reply-"+id).removeClass("d-none")
    })
}

function add_subcomment(id){
    var my_subcomment = $("#subcomment-reply-" + id).val()
    console.log(my_subcomment)
    $.ajax({
        type:"POST",
        url: "/" + id + "/subcomment/add",
        data: { subcomment: my_subcomment }
    }).done( function(data){
        $("#sub-comment-list-" + id).html(data)
        // document.getElementById("my-subcomment").value = ""
        console.log(data)
    })
}

function edit_comment(id){
    $("#comment-"+id).addClass("d-none")
    $("#edit-comment-"+id).removeClass("d-none")
}

function cancel_edit(id){
    var my_comment = $("#comment-"+id).val()
    $("#edit-comment-"+id).val(my_comment)
    $("#comment-"+id).removeClass("d-none")
    $("#edit-comment-"+id).addClass("d-none")
}
function save_edit(id){
        console.log(id)
        var new_comment = $("#edit-comment-"+id).val()
        $.ajax({
            type: "POST",
            url: "/" + id + "/comment/edit",
            data: { new_comment: new_comment }
        }).done( function(data){
            $(".comment-section").html(data)
            // console.log(data)
        })
}

function edit_subcomment(id){
    $("#subcomment-"+id).addClass("d-none")
    $("#edit-subcomment-"+id).removeClass("d-none")
}

function cancel_edit_sub(id){
    var my_subcomment = $("#subcomment-"+id).val()
    $("#edit-subcomment-"+id).val(my_subcomment)
    $("#subcomment-"+id).removeClass("d-none")
    $("#edit-subcomment-"+id).addClass("d-none")
}
function save_edit_sub(id){
        console.log(id)
        var new_subcomment = $("#edit-subcomment-"+id).val()
        $.ajax({
            type: "POST",
            url: "/" + id + "/subcomment/edit",
            data: { new_subcomment: new_subcomment }
        }).done( function(data){
            $(".comment-section-sub").html(data)
            // console.log(data)
        })
}

function delete_sub(id){
    console.log(1)
    $.ajax({
        type:"POST",
        url: "/subcomment/" + id + "/delete/",
    }).done( function(data){
        $(".comment-section-sub").html(data)
        console.log(data)
    })
}