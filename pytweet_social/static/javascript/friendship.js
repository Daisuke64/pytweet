function toggle_friendship(target_user_id) {
    const elm_id = "#follow-btn-" + target_user_id;
    if ($(elm_id).hasClass("btn-outline-info")) {
        un_follow(target_user_id);
    } else {
        follow(target_user_id);
    }
}


function follow(target_user_id) {
    const elm_id = "#follow-btn-" + target_user_id;

    $.ajax({
        type:'POST',
        url:'/users/' + target_user_id + '/friendship',
        data: null,
        contentType:'application/json'
    })
    .done((_) => {
        $(elm_id).removeClass("btn-info");
        $(elm_id).addClass("btn-outline-info");
        $(elm_id).text("Following");
        console.log("You followed");
    });
}

function un_follow(target_user_id) {
    const elm_id = "#follow-btn-" + target_user_id;

    $.ajax({
        type:'DELETE',
        url:'/users/' + target_user_id + '/friendship',
        data: null,
        contentType:'application/json'
    })
    .done((_) => {
        $(elm_id).removeClass("btn-outline-info");
        $(elm_id).addClass("btn-info");
        $(elm_id).text("Follow");
        console.log("You stopped following");
    });
}