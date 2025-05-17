function fetchComments() {
    $.get("http://127.0.0.1:5000/comments", function (response) {
        if (response.status === "success") {
            const comments = response.data;
            $("#comments").empty(); 
            comments.forEach(comment => {
                const commentHTML = `
                    <div class="comment-box">
                        <div class="comment-header">
                            <span class="username">${comment.username}</span>
                            <span class="score">Score: ${comment.rating}</span>
                        </div>
                        <div class="comment-content">${comment.comment}</div>
                    </div>
                `;
                $("#comments").append(commentHTML);
            });
        } else {
            alert("Failed to load comments.");
        }
    }).fail(function (jqXHR, textStatus, errorThrown) {
        console.error("Request failed:", textStatus, errorThrown);
        alert(`An error occurred: ${jqXHR.status} ${errorThrown}`);
    });
}

function submitComment() {
    const comment = $("#comment-input").val();
    const rating = $("#rating").val();

    if (comment && rating) {
        $.post("http://127.0.0.1:5000/add_comment", { comment, rating }, function (response) {
            if (response.status === "success") {
                alert("Comment added successfully!");
                fetchComments(); 
                $("#comment-input").val("");
                $("#rating").val("");
            } else {
                alert("Failed to add comment.");
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.error("Request failed:", textStatus, errorThrown);
            alert(`An error occurred: ${jqXHR.status} ${errorThrown}`);
        });
    } else {
        alert("Please fill out all fields.");
    }
}

function validateRating(input) {
    const value = input.value;
    if (!/^[0-5]$/.test(value)) {
        input.value = ""; 
        alert("Please enter a number between 0 and 5.");
    }
}

$(document).ready(function () {
    fetchComments();
});